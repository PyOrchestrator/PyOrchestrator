from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import RunStatus, ScriptStatus
from app.models.run import Run, Schedule
from app.models.script import Script


async def get_dashboard_stats(db: AsyncSession) -> dict:
    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(hours=24)

    total = await db.scalar(select(func.count()).select_from(Script))
    active = await db.scalar(
        select(func.count()).select_from(Script).where(Script.status == ScriptStatus.ENABLED.value)
    )
    stopped = await db.scalar(
        select(func.count()).select_from(Script).where(Script.status == ScriptStatus.DISABLED.value)
    )
    errors_24h = await db.scalar(
        select(func.count()).select_from(Run).where(
            Run.status.in_([RunStatus.FAILED.value, RunStatus.TIMEOUT.value]),
            Run.finished_at >= day_ago,
        )
    )
    completed = await db.scalar(
        select(func.count()).select_from(Run).where(Run.status == RunStatus.SUCCESS.value)
    )
    active_cron = await db.scalar(
        select(func.count()).select_from(Schedule).where(Schedule.is_active == True)  # noqa: E712
    )
    running_now = await db.scalar(
        select(func.count()).select_from(Run).where(Run.status == RunStatus.RUNNING.value)
    )

    return {
        "total_scripts": total or 0,
        "active_scripts": active or 0,
        "stopped_scripts": stopped or 0,
        "errors_24h": errors_24h or 0,
        "completed_tasks": completed or 0,
        "active_cron_jobs": active_cron or 0,
        "running_now": running_now or 0,
    }
