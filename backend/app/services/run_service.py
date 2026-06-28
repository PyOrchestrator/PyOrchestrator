from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import RunStatus
from app.models.run import Run, RunLog, RunMetric
from app.services.notification_service import dispatch_run_failure_alerts


async def complete_run(
    db: AsyncSession,
    run_id: UUID,
    status: str,
    exit_code: int,
    duration_ms: int,
    stdout: str,
    stderr: str,
    hostname: str = "",
) -> Run:
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one()
    run.status = status
    run.exit_code = exit_code
    run.duration_ms = duration_ms
    run.finished_at = datetime.now(timezone.utc)
    run.runtime_hostname = hostname
    if stderr and status != RunStatus.SUCCESS.value:
        run.error_message = stderr[:4000]

    for line in (stdout + stderr).splitlines():
        if line.strip():
            db.add(RunLog(run_id=run_id, level="info" if status == RunStatus.SUCCESS.value else "error", message=line))

    await db.flush()

    if status in (RunStatus.FAILED.value, RunStatus.TIMEOUT.value):
        await dispatch_run_failure_alerts(db, run)

    return run


async def append_run_log(db: AsyncSession, run_id: UUID, level: str, message: str) -> None:
    db.add(RunLog(run_id=run_id, level=level, message=message))
    await db.flush()


async def start_run(db: AsyncSession, run_id: UUID, pid: int, hostname: str) -> None:
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one()
    run.status = RunStatus.RUNNING.value
    run.started_at = datetime.now(timezone.utc)
    run.pid = pid
    run.runtime_hostname = hostname
    await db.flush()


async def record_metric(
    db: AsyncSession,
    run_id: UUID,
    cpu_percent: float,
    memory_bytes: int,
    thread_count: int = 0,
    open_files: int = 0,
    network_connections: int = 0,
) -> None:
    db.add(
        RunMetric(
            run_id=run_id,
            cpu_percent=cpu_percent,
            memory_bytes=memory_bytes,
            thread_count=thread_count,
            open_files=open_files,
            network_connections=network_connections,
        )
    )
    await db.flush()


from app.models.run import RunMetric  # noqa: E402
