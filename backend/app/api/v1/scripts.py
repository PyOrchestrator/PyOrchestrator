from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.deps import get_current_user, require_permission
from app.db.session import get_db
from app.models.enums import ScriptStatus
from app.models.script import Script, ScriptFile, ScriptTemplate
from app.models.user import User
from app.schemas import ScriptCreate, ScriptFileResponse, ScriptFileUpdate, ScriptResponse, ScriptUpdate, TemplateResponse
from app.services.script_service import (
    create_script,
    export_script_zip,
    get_script_or_404,
    import_script_zip,
    queue_run,
    redis_service,
    storage_service,
)

router = APIRouter()


@router.get("", response_model=list[ScriptResponse])
async def list_scripts(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("scripts:read"))],
    group_id: UUID | None = None,
):
    q = select(Script)
    if group_id:
        q = q.where(Script.group_id == group_id)
    result = await db.execute(q.order_by(Script.name))
    return result.scalars().all()


@router.post("", response_model=ScriptResponse, status_code=201)
async def create_script_endpoint(
    body: ScriptCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("scripts:write"))],
):
    files = None
    if body.code:
        files = {body.entrypoint: body.code, "requirements.txt": ""}
    script = await create_script(
        db, body.name, body.description, body.group_id, body.script_type, body.entrypoint, files
    )
    return script


@router.get("/templates", response_model=list[TemplateResponse])
async def list_templates(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("scripts:read"))],
):
    result = await db.execute(select(ScriptTemplate))
    return result.scalars().all()


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(
    script_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("scripts:read"))],
):
    try:
        return await get_script_or_404(db, script_id)
    except ValueError:
        raise HTTPException(404, "Script not found")


@router.put("/{script_id}", response_model=ScriptResponse)
async def update_script(
    script_id: UUID,
    body: ScriptUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("scripts:write"))],
):
    try:
        script = await get_script_or_404(db, script_id)
    except ValueError:
        raise HTTPException(404, "Script not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(script, field, value)
    script.version += 1
    await redis_service.publish(settings.script_updated_channel, str(script.id))
    return script


@router.delete("/{script_id}", status_code=204)
async def delete_script(
    script_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("scripts:delete"))],
):
    try:
        script = await get_script_or_404(db, script_id)
    except ValueError:
        raise HTTPException(404, "Script not found")
    await db.delete(script)


@router.post("/{script_id}/copy", response_model=ScriptResponse, status_code=201)
async def copy_script(
    script_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("scripts:write"))],
):
    try:
        original = await get_script_or_404(db, script_id)
    except ValueError:
        raise HTTPException(404, "Script not found")
    files = {f.path: f.content or "" for f in original.files}
    return await create_script(
        db, f"{original.name} (copy)", original.description, original.group_id,
        original.script_type, original.entrypoint, files
    )


@router.post("/{script_id}/enable", response_model=ScriptResponse)
async def enable_script(
    script_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("scripts:write"))],
):
    script = await get_script_or_404(db, script_id)
    script.status = ScriptStatus.ENABLED.value
    return script


@router.post("/{script_id}/disable", response_model=ScriptResponse)
async def disable_script(
    script_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("scripts:disable"))],
):
    script = await get_script_or_404(db, script_id)
    script.status = ScriptStatus.DISABLED.value
    return script


@router.get("/{script_id}/files", response_model=list[ScriptFileResponse])
async def list_files(
    script_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("scripts:read"))],
):
    script = await get_script_or_404(db, script_id)
    return script.files


@router.put("/{script_id}/files/{file_path:path}", response_model=ScriptFileResponse)
async def update_file(
    script_id: UUID,
    file_path: str,
    body: ScriptFileUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("scripts:write"))],
):
    script = await get_script_or_404(db, script_id)
    sf = next((f for f in script.files if f.path == file_path), None)
    if not sf:
        sf = ScriptFile(script_id=script.id, path=file_path, file_type="source")
        script.files.append(sf)
        db.add(sf)
    sf.content = body.content
    sf.size_bytes = len(body.content.encode())
    storage_service.put_file(script.id, file_path, body.content.encode())
    script.version += 1
    await redis_service.publish(settings.script_updated_channel, str(script.id))
    return sf


@router.get("/{script_id}/export")
async def export_script(
    script_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("scripts:read"))],
):
    script = await get_script_or_404(db, script_id)
    data = await export_script_zip(script)
    return Response(
        content=data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{script.slug}.zip"'},
    )


@router.post("/import", response_model=ScriptResponse, status_code=201)
async def import_script(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("scripts:write"))],
    file: UploadFile = File(...),
    group_id: UUID | None = None,
):
    data = await file.read()
    return await import_script_zip(db, data, group_id)


@router.post("/from-template/{template_id}", response_model=ScriptResponse, status_code=201)
async def create_from_template(
    template_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("scripts:write"))],
):
    result = await db.execute(select(ScriptTemplate).where(ScriptTemplate.id == template_id))
    tpl = result.scalar_one_or_none()
    if not tpl:
        raise HTTPException(404, "Template not found")
    files = {k: v for k, v in tpl.file_tree.items() if isinstance(v, str)}
    return await create_script(db, tpl.name, tpl.description, files=files)
