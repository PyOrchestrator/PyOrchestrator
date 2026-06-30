from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.db.session import async_session
from app.models.enums import RoleName
from app.models.user import User
from app.services.notification_service import create_notification
from app.services.update_service import update_service
from app.services.update_settings_service import update_settings_service


async def _notify_admins(db, title: str, body: str, severity: str = "info") -> None:
    result = await db.execute(
        select(User).where(User.role == RoleName.ADMINISTRATOR.value, User.is_active == True)  # noqa: E712
    )
    for user in result.scalars().all():
        await create_notification(db, user.id, title, body, severity=severity, run_id=None)
    await db.commit()


async def notify_update_available(db, version: str, release_url: str) -> None:
    body = f"A new version v{version} is available."
    if release_url:
        body += f" Release: {release_url}"
    await _notify_admins(db, f"Update available: v{version}", body, severity="info")


async def notify_update_started(db, job) -> None:
    await _notify_admins(
        db,
        f"Update started: v{job.from_version} → v{job.target_version}",
        f"Update job {job.id} is running ({job.trigger}).",
        severity="info",
    )


async def notify_update_completed(db, job) -> None:
    await _notify_admins(
        db,
        f"Update completed: v{job.target_version}",
        f"PyOrchestrator was updated successfully to v{job.target_version}.",
        severity="info",
    )


async def notify_update_failed(db, job, message: str) -> None:
    await _notify_admins(
        db,
        f"Update failed: v{job.target_version}",
        message[:4000],
        severity="error",
    )


class UpdateScheduler:
    def __init__(self) -> None:
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()
        self._last_check_at: datetime | None = None
        self._last_auto_at: datetime | None = None

    async def start(self) -> None:
        if self._task:
            return
        self._stop.clear()
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        self._stop.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def reload_schedule(self) -> None:
        self._last_check_at = None
        self._last_auto_at = None

    async def _loop(self) -> None:
        await asyncio.sleep(5)
        while not self._stop.is_set():
            try:
                await update_service.process_result_file()
                await update_service.process_progress_file()
                async with async_session() as db:
                    await update_service.reconcile_stale_jobs(db)
                    cfg = await update_settings_service.load(db)
                    now = datetime.now(timezone.utc)
                    if cfg.check_enabled:
                        due = (
                            self._last_check_at is None
                            or (now - self._last_check_at).total_seconds()
                            >= cfg.check_interval_hours * 3600
                        )
                        if due:
                            try:
                                await update_service.check_for_updates(db, persist=True)
                            except Exception:
                                pass
                            self._last_check_at = now
                    if cfg.auto_update_enabled and update_service:
                        due_auto = (
                            self._last_auto_at is None
                            or (now - self._last_auto_at).total_seconds()
                            >= cfg.auto_update_interval_hours * 3600
                        )
                        if due_auto:
                            try:
                                status = await update_service.get_status(db)
                                if status["update_available"] and status["executor_available"]:
                                    await update_service.start_update(db, trigger="auto")
                            except Exception:
                                pass
                            self._last_auto_at = now
            except Exception:
                pass
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=5)
            except asyncio.TimeoutError:
                continue


update_scheduler = UpdateScheduler()
