import io
import json
import zipfile
from io import BytesIO
from uuid import UUID

import redis.asyncio as aioredis
from minio import Minio
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.crypto import decrypt_secret, encrypt_secret
from app.models.enums import RunStatus, ScriptStatus, TriggerType
from app.models.run import Run, RunLog, Schedule
from app.models.script import Script, ScriptFile, ScriptSecret
from app.models.user import Group


class RedisService:
  def __init__(self):
      self._client: aioredis.Redis | None = None

  async def client(self) -> aioredis.Redis:
      if not self._client:
          self._client = aioredis.from_url(settings.redis_url, decode_responses=True)
      return self._client

  async def enqueue_run(self, payload: dict) -> None:
      c = await self.client()
      await c.rpush(settings.runtime_queue_key, json.dumps(payload))

  async def publish(self, channel: str, message: str) -> None:
      c = await self.client()
      await c.publish(channel, message)

  async def publish_log(self, run_id: str, level: str, message: str) -> None:
      c = await self.client()
      await c.publish(f"run:{run_id}:logs", json.dumps({"level": level, "message": message}))


redis_service = RedisService()


class StorageService:
    def __init__(self):
        self._client: Minio | None = None

    @property
    def client(self) -> Minio:
        if not self._client:
            self._client = Minio(
                settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=settings.minio_secure,
            )
        return self._client

    def script_prefix(self, script_id: UUID) -> str:
        return f"scripts/{script_id}/"

    def put_file(self, script_id: UUID, path: str, data: bytes) -> None:
        key = f"{self.script_prefix(script_id)}{path}"
        self.client.put_object(settings.minio_bucket, key, BytesIO(data), len(data))

    def get_file(self, script_id: UUID, path: str) -> bytes:
        key = f"{self.script_prefix(script_id)}{path}"
        resp = self.client.get_object(settings.minio_bucket, key)
        try:
            return resp.read()
        finally:
            resp.close()
            resp.release_conn()


storage_service = StorageService()


async def slugify(name: str, db: AsyncSession) -> str:
    base = name.lower().replace(" ", "-")[:200]
    slug = base
    i = 1
    while True:
        exists = await db.execute(select(Script.id).where(Script.slug == slug))
        if not exists.scalar_one_or_none():
            return slug
        slug = f"{base}-{i}"
        i += 1


async def create_script(
    db: AsyncSession,
    name: str,
    description: str = "",
    group_id: UUID | None = None,
    script_type: str = "script",
    entrypoint: str = "main.py",
    files: dict[str, str] | None = None,
) -> Script:
    script = Script(
        name=name,
        slug=await slugify(name, db),
        description=description,
        group_id=group_id,
        script_type=script_type,
        entrypoint=entrypoint,
    )
    db.add(script)
    await db.flush()

    default_files = files or {
        entrypoint: 'print("Hello from PyOrchestrator")\n',
        "requirements.txt": "",
    }
    for path, content in default_files.items():
        sf = ScriptFile(
            script_id=script.id,
            path=path,
            content=content,
            size_bytes=len(content.encode()),
            file_type="requirements" if path.endswith("requirements.txt") else "source",
        )
        db.add(sf)
        storage_service.put_file(script.id, path, content.encode())

    await db.flush()
    await redis_service.publish(settings.script_updated_channel, str(script.id))
    return script


async def get_script_or_404(db: AsyncSession, script_id: UUID) -> Script:
    result = await db.execute(
        select(Script).options(selectinload(Script.files)).where(Script.id == script_id)
    )
    script = result.scalar_one_or_none()
    if not script:
        raise ValueError("Script not found")
    return script


async def queue_run(
    db: AsyncSession,
    script: Script,
    trigger_type: str = TriggerType.MANUAL.value,
    user_id: UUID | None = None,
    schedule_id: UUID | None = None,
    max_runtime_seconds: int | None = None,
) -> Run:
    if script.status != ScriptStatus.ENABLED.value:
        raise ValueError("Script is disabled")

    schedule: Schedule | None = None
    if schedule_id:
        result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
        schedule = result.scalar_one_or_none()
        if not schedule:
            raise ValueError("Schedule not found")
        now = datetime.now(timezone.utc)
        if schedule.start_at and now < schedule.start_at:
            raise ValueError("Schedule is not active yet")
        if schedule.end_at and now > schedule.end_at:
            raise ValueError("Schedule has expired")
        running_for_schedule = await db.execute(
            select(func.count()).select_from(Run).where(
                Run.schedule_id == schedule_id,
                Run.status.in_([RunStatus.QUEUED.value, RunStatus.RUNNING.value]),
            )
        )
        if (running_for_schedule.scalar() or 0) >= schedule.max_instances:
            raise ValueError("Max schedule instances reached")

    # reload files
    await db.refresh(script, ["files"])

    running = await db.execute(
        select(func.count()).select_from(Run).where(
            Run.script_id == script.id, Run.status.in_([RunStatus.QUEUED.value, RunStatus.RUNNING.value])
        )
    )
    if (running.scalar() or 0) >= script.max_concurrent_runs:
        raise ValueError("Max concurrent runs reached")

    run = Run(
        script_id=script.id,
        schedule_id=schedule_id,
        triggered_by_user_id=user_id,
        trigger_type=trigger_type,
        status=RunStatus.QUEUED.value,
    )
    db.add(run)
    await db.flush()

    main_content = ""
    for f in script.files:
        if f.path == script.entrypoint:
            main_content = f.content or ""
            break

    secrets_env = {}
    result = await db.execute(select(ScriptSecret).where(ScriptSecret.script_id == script.id))
    for sec in result.scalars():
        secrets_env[f"SECRET_{sec.key}"] = decrypt_secret(sec.ciphertext, sec.nonce)

    max_runtime = (
        max_runtime_seconds
        or (schedule.max_runtime_seconds if schedule and schedule.max_runtime_seconds else None)
        or script.max_runtime_seconds
    )

    job = {
        "script_id": str(script.id),
        "run_id": str(run.id),
        "entrypoint": script.entrypoint,
        "code": main_content,
        "files": {f.path: f.content or "" for f in script.files},
        "max_memory_bytes": script.max_memory_bytes,
        "max_cpu_seconds": max_runtime,
        "wall_timeout_sec": max_runtime,
        "secrets": secrets_env,
    }
    await redis_service.enqueue_run(job)
    return run


async def export_script_zip(script: Script) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        meta = {"name": script.name, "slug": script.slug, "entrypoint": script.entrypoint}
        zf.writestr("pyorchestrator.json", json.dumps(meta, indent=2))
        for f in script.files:
            zf.writestr(f.path, f.content or "")
    return buf.getvalue()


async def import_script_zip(db: AsyncSession, data: bytes, group_id: UUID | None = None) -> Script:
    with zipfile.ZipFile(BytesIO(data)) as zf:
        meta = json.loads(zf.read("pyorchestrator.json")) if "pyorchestrator.json" in zf.namelist() else {}
        files = {}
        for name in zf.namelist():
            if name == "pyorchestrator.json" or name.endswith("/"):
                continue
            files[name] = zf.read(name).decode()
        return await create_script(
            db,
            name=meta.get("name", "imported-script"),
            entrypoint=meta.get("entrypoint", "main.py"),
            group_id=group_id,
            files=files,
        )
