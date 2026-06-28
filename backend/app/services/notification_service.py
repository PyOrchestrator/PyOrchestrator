from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import RoleName, RunStatus
from app.models.run import Run
from app.models.user import Notification, User


def _event_title(event: str, script_name: str) -> str:
    titles = {
        "started": f"Script started: {script_name}",
        "completed": f"Script completed: {script_name}",
        "failed": f"Script failed: {script_name}",
        "timeout": f"Script timeout: {script_name}",
    }
    return titles.get(event, f"Script event: {script_name}")


async def _notification_exists(db: AsyncSession, user_id: UUID, run_id: UUID) -> bool:
    result = await db.execute(
        select(Notification.id).where(Notification.user_id == user_id, Notification.run_id == run_id)
    )
    return result.scalar_one_or_none() is not None


async def create_notification(
    db: AsyncSession,
    user_id: UUID,
    title: str,
    body: str,
    severity: str = "info",
    run_id: UUID | None = None,
) -> Notification:
    n = Notification(user_id=user_id, title=title, body=body, severity=severity, run_id=run_id)
    db.add(n)
    await db.flush()
    return n


async def notify_run_event(
    db: AsyncSession,
    user_id: UUID,
    event: str,
    script_name: str,
    run_id: UUID,
    body: str | None = None,
) -> None:
    if await _notification_exists(db, user_id, run_id):
        return
    await create_notification(
        db,
        user_id=user_id,
        title=_event_title(event, script_name),
        body=body or f"Run {run_id} — {event}",
        severity="error" if event in ("failed", "timeout") else "info",
        run_id=run_id,
    )


async def dispatch_run_failure_alerts(db: AsyncSession, run: Run) -> None:
    if run.status not in (RunStatus.FAILED.value, RunStatus.TIMEOUT.value):
        return

    await db.refresh(run, ["script"])
    event = "timeout" if run.status == RunStatus.TIMEOUT.value else "failed"
    script_name = run.script.name if run.script else "Unknown"
    body = (run.error_message or f"Run {run.id} — {event}")[:4000]

    user_ids: set[UUID] = set()
    if run.triggered_by_user_id:
        user_ids.add(run.triggered_by_user_id)

    admin_ids = await db.execute(
        select(User.id).where(User.role == RoleName.ADMINISTRATOR.value, User.is_active == True)  # noqa: E712
    )
    user_ids.update(admin_ids.scalars().all())

    for user_id in user_ids:
        await notify_run_event(db, user_id, event, script_name, run.id, body=body)


async def sync_failure_alerts_for_user(db: AsyncSession, user: User) -> None:
    """Backfill alerts for recent failed runs so Alerts page matches dashboard failures."""
    day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
    q = (
        select(Run)
        .options(selectinload(Run.script))
        .where(
            Run.status.in_([RunStatus.FAILED.value, RunStatus.TIMEOUT.value]),
            Run.finished_at >= day_ago,
        )
    )
    if user.role != RoleName.ADMINISTRATOR.value:
        q = q.where(Run.triggered_by_user_id == user.id)

    result = await db.execute(q.order_by(Run.finished_at.desc()))
    for run in result.scalars().all():
        event = "timeout" if run.status == RunStatus.TIMEOUT.value else "failed"
        script_name = run.script.name if run.script else "Unknown"
        body = (run.error_message or f"Run {run.id} — {event}")[:4000]
        await notify_run_event(db, user.id, event, script_name, run.id, body=body)
