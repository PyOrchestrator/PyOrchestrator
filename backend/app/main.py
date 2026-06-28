"""PyOrchestrator Backend API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from sqlalchemy import select

from app.api.v1.router import api_router
from app.api.v1.misc import internal_router as internal_routes
from app.core.config import settings
from app.core.security import hash_password
from app.db.session import async_session, engine
from app.models import Base
from app.models.run import BackupSettings
from app.models.script import ScriptTemplate
from app.models.user import Group, User
from app.ws.logs import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_data()
    yield
    await engine.dispose()


async def seed_data() -> None:
    async with async_session() as db:
        admin = await db.execute(select(User).where(User.email == settings.default_admin_email))
        if not admin.scalar_one_or_none():
            db.add(User(
                email=settings.default_admin_email,
                password_hash=hash_password(settings.default_admin_password),
                display_name="Administrator",
                role="Administrator",
            ))

        for name, color, icon in [
            ("monitoring", "#42a5f5", "monitor"),
            ("bots", "#66bb6a", "smart_toy"),
            ("integrations", "#ab47bc", "hub"),
            ("analytics", "#ffa726", "analytics"),
            ("etl", "#26c6da", "sync_alt"),
            ("parsers", "#ef5350", "code"),
        ]:
            exists = await db.execute(select(Group).where(Group.name == name))
            if not exists.scalar_one_or_none():
                db.add(Group(name=name, description=f"{name} scripts", color=color, icon=icon))

        templates = [
            ("Hello World", "Basic print script", {"main.py": 'print("Hello from PyOrchestrator")\n'}),
            ("HTTP Poller", "Poll REST API", {
                "main.py": (
                    "import os, urllib.request\n"
                    "url = os.environ.get('SECRET_API_URL', 'https://httpbin.org/get')\n"
                    "print(urllib.request.urlopen(url).read().decode()[:200])\n"
                ),
                "requirements.txt": "",
            }),
            ("Interval Bot", "Long-running bot skeleton", {
                "main.py": (
                    "import time\n"
                    "for i in range(5):\n"
                    "    print(f'tick {i}')\n"
                    "    time.sleep(1)\n"
                ),
            }),
        ]
        for name, desc, files in templates:
            exists = await db.execute(select(ScriptTemplate).where(ScriptTemplate.name == name))
            if not exists.scalar_one_or_none():
                db.add(ScriptTemplate(name=name, description=desc, file_tree=files, category="system"))

        backup_settings = await db.execute(select(BackupSettings).where(BackupSettings.id == 1))
        if not backup_settings.scalar_one_or_none():
            db.add(BackupSettings(id=1))

        await db.commit()


app = FastAPI(
    title="PyOrchestrator API",
    version=settings.app_version,
    description="SCADA/CMS platform for Python scripts and bots",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(internal_routes, prefix="/internal")
app.include_router(ws_router, prefix="/ws", tags=["websocket"])
app.mount("/metrics", make_asgi_app())


@app.get("/health")
async def health():
    return {"status": "ok", "service": "backend", "version": settings.app_version}
