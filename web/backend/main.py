"""
FastAPI backend for the Chaos Engineering web UI.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from loader import load_chaos_modules
from utils import get_config, get_logger

try:
    from api_v1 import router as api_v1_router
except ImportError:
    api_v1_router = None

mods = load_chaos_modules()
chaos_runner = mods["chaos_runner"]
scheduler_module = mods["scheduler"]
notifications_module = mods["notifications"]

list_experiments = chaos_runner.list_experiments
run_experiment = chaos_runner.run_experiment
check_experiment_status = chaos_runner.check_experiment_status
stop_experiment = chaos_runner.stop_experiment
list_running_experiments = chaos_runner.list_running_experiments
ChaosScheduler = scheduler_module.ChaosScheduler
NotificationService = notifications_module.NotificationService

app = FastAPI(title="Chaos Engineering API", version="1.0.0")
config = get_config()
logger = get_logger(__name__)

if api_v1_router is not None:
    app.include_router(api_v1_router)

_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
_api_key = os.getenv("CHAOS_API_KEY", "")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    if _api_key and x_api_key != _api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict) -> None:
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()
scheduler = ChaosScheduler()
notification_service = NotificationService()


class ExperimentRequest(BaseModel):
    name: str
    namespace: Optional[str] = None


class ScheduleRequest(BaseModel):
    experiment: str
    schedule: str
    namespace: Optional[str] = None


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Chaos Engineering API", "version": "1.0.0"}


@app.get("/api/experiments", dependencies=[Depends(verify_api_key)])
async def get_experiments():
    try:
        return {"experiments": list_experiments()}
    except Exception as exc:
        logger.error("Error listing experiments: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/experiments/running", dependencies=[Depends(verify_api_key)])
async def get_running_experiments():
    try:
        list_running_experiments()
        return {"running": [], "note": "Use kubectl get chaosengine for details"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/experiments/run", dependencies=[Depends(verify_api_key)])
async def run_experiment_api(request: ExperimentRequest):
    try:
        namespace = request.namespace or config.app_namespace
        run_experiment(request.name, namespace)
        notification_service.notify_experiment_started(request.name, namespace)
        await manager.broadcast(
            {
                "type": "experiment_started",
                "experiment": request.name,
                "namespace": namespace,
                "timestamp": datetime.now().isoformat(),
            }
        )
        return {"status": "started", "experiment": request.name}
    except Exception as exc:
        logger.error("Error running experiment: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/experiments/{experiment_name}/status", dependencies=[Depends(verify_api_key)])
async def get_experiment_status(experiment_name: str, namespace: Optional[str] = None):
    try:
        check_experiment_status(experiment_name, namespace or config.app_namespace)
        return {"status": "checked", "experiment": experiment_name}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/experiments/{experiment_name}/stop", dependencies=[Depends(verify_api_key)])
async def stop_experiment_api(experiment_name: str, namespace: Optional[str] = None):
    try:
        ns = namespace or config.app_namespace
        stop_experiment(experiment_name, ns)
        await manager.broadcast(
            {
                "type": "experiment_stopped",
                "experiment": experiment_name,
                "namespace": ns,
                "timestamp": datetime.now().isoformat(),
            }
        )
        return {"status": "stopped", "experiment": experiment_name}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/abort", dependencies=[Depends(verify_api_key)])
async def abort_api(namespace: Optional[str] = None):
    from abort import abort_namespace

    ns = namespace or config.app_namespace
    total = abort_namespace(ns)
    return {"status": "aborted", "count": total, "namespace": ns}


@app.get("/api/schedules", dependencies=[Depends(verify_api_key)])
async def get_schedules():
    try:
        return {"schedules": scheduler.list_scheduled_experiments()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/schedules", dependencies=[Depends(verify_api_key)])
async def create_schedule(request: ScheduleRequest):
    try:
        success = scheduler.create_scheduled_experiment(
            experiment_name=request.experiment,
            schedule=request.schedule,
            namespace=request.namespace,
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create schedule")
        return {
            "status": "created",
            "experiment": request.experiment,
            "schedule": request.schedule,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.delete("/api/schedules/{experiment_name}", dependencies=[Depends(verify_api_key)])
async def delete_schedule(experiment_name: str):
    try:
        if scheduler.delete_scheduled_experiment(experiment_name):
            return {"status": "deleted", "experiment": experiment_name}
        raise HTTPException(status_code=404, detail="Schedule not found")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/config", dependencies=[Depends(verify_api_key)])
async def get_config_api():
    return {
        "app_namespace": config.app_namespace,
        "litmus_namespace": config.litmus_namespace,
        "monitoring_namespace": config.monitoring_namespace,
        "monitoring_enabled": config.monitoring_enabled,
        "chaos_env": os.getenv("CHAOS_ENV", "dev"),
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "echo", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
