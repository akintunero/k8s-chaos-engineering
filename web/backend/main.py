"""
FastAPI Backend for Chaos Engineering Web UI
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import asyncio
from datetime import datetime
import sys
from pathlib import Path

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

import importlib.util

# Import from scripts directory
spec = importlib.util.spec_from_file_location("chaos_runner", scripts_dir / "chaos-runner.py")
chaos_runner = importlib.util.module_from_spec(spec)
sys.modules["chaos_runner"] = chaos_runner
spec.loader.exec_module(chaos_runner)

spec = importlib.util.spec_from_file_location("scheduler", scripts_dir / "scheduler.py")
scheduler_module = importlib.util.module_from_spec(spec)
sys.modules["scheduler"] = scheduler_module
spec.loader.exec_module(scheduler_module)

spec = importlib.util.spec_from_file_location("notifications", scripts_dir / "notifications.py")
notifications_module = importlib.util.module_from_spec(spec)
sys.modules["notifications"] = notifications_module
spec.loader.exec_module(notifications_module)

from utils import get_config, get_logger

# Import modules dynamically (handling hyphens in filenames)
spec = importlib.util.spec_from_file_location("chaos_runner", scripts_dir / "chaos-runner.py")
chaos_runner = importlib.util.module_from_spec(spec)
sys.modules["chaos_runner"] = chaos_runner
spec.loader.exec_module(chaos_runner)

spec = importlib.util.spec_from_file_location("scheduler", scripts_dir / "scheduler.py")
scheduler_module = importlib.util.module_from_spec(spec)
sys.modules["scheduler"] = scheduler_module
spec.loader.exec_module(scheduler_module)

spec = importlib.util.spec_from_file_location("notifications", scripts_dir / "notifications.py")
notifications_module = importlib.util.module_from_spec(spec)
sys.modules["notifications"] = notifications_module
spec.loader.exec_module(notifications_module)

# Now import functions
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()
scheduler = ChaosScheduler()
notification_service = NotificationService()


# Pydantic models
class ExperimentRequest(BaseModel):
    name: str
    namespace: Optional[str] = None

class ScheduleRequest(BaseModel):
    experiment: str
    schedule: str
    namespace: Optional[str] = None

class NotificationRequest(BaseModel):
    message: str
    title: str = "Chaos Experiment"
    level: str = "info"
    experiment_name: Optional[str] = None


# API Routes
@app.get("/")
async def root():
    return {"message": "Chaos Engineering API", "version": "1.0.0"}

@app.get("/api/experiments")
async def get_experiments():
    """Get list of available experiments"""
    try:
        experiments = list_experiments()
        return {"experiments": experiments}
    except Exception as e:
        logger.error(f"Error listing experiments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/experiments/running")
async def get_running_experiments():
    """Get list of running experiments"""
    try:
        # This would need to be adapted to return JSON
        experiments = list_running_experiments()
        return {"running": []}  # Placeholder
    except Exception as e:
        logger.error(f"Error getting running experiments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/experiments/run")
async def run_experiment_api(request: ExperimentRequest):
    """Run a chaos experiment"""
    try:
        namespace = request.namespace or config.app_namespace
        run_experiment(request.name, namespace)
        
        # Send notification
        notification_service.notify_experiment_started(request.name, namespace)
        
        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "experiment_started",
            "experiment": request.name,
            "namespace": namespace,
            "timestamp": datetime.now().isoformat()
        })
        
        return {"status": "started", "experiment": request.name}
    except Exception as e:
        logger.error(f"Error running experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/experiments/{experiment_name}/status")
async def get_experiment_status(experiment_name: str, namespace: Optional[str] = None):
    """Get status of an experiment"""
    try:
        namespace = namespace or config.app_namespace
        check_experiment_status(experiment_name, namespace)
        return {"status": "checking", "experiment": experiment_name}
    except Exception as e:
        logger.error(f"Error checking experiment status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/experiments/{experiment_name}/stop")
async def stop_experiment_api(experiment_name: str, namespace: Optional[str] = None):
    """Stop a running experiment"""
    try:
        namespace = namespace or config.app_namespace
        stop_experiment(experiment_name, namespace)
        
        await manager.broadcast({
            "type": "experiment_stopped",
            "experiment": experiment_name,
            "namespace": namespace,
            "timestamp": datetime.now().isoformat()
        })
        
        return {"status": "stopped", "experiment": experiment_name}
    except Exception as e:
        logger.error(f"Error stopping experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/schedules")
async def get_schedules():
    """Get list of scheduled experiments"""
    try:
        schedules = scheduler.list_scheduled_experiments()
        return {"schedules": schedules}
    except Exception as e:
        logger.error(f"Error getting schedules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schedules")
async def create_schedule(request: ScheduleRequest):
    """Create a scheduled experiment"""
    try:
        success = scheduler.create_scheduled_experiment(
            experiment_name=request.experiment,
            schedule=request.schedule,
            namespace=request.namespace
        )
        if success:
            return {"status": "created", "experiment": request.experiment, "schedule": request.schedule}
        else:
            raise HTTPException(status_code=400, detail="Failed to create schedule")
    except Exception as e:
        logger.error(f"Error creating schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/schedules/{experiment_name}")
async def delete_schedule(experiment_name: str):
    """Delete a scheduled experiment"""
    try:
        success = scheduler.delete_scheduled_experiment(experiment_name)
        if success:
            return {"status": "deleted", "experiment": experiment_name}
        else:
            raise HTTPException(status_code=404, detail="Schedule not found")
    except Exception as e:
        logger.error(f"Error deleting schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
async def get_config_api():
    """Get current configuration"""
    return {
        "app_namespace": config.app_namespace,
        "litmus_namespace": config.litmus_namespace,
        "monitoring_namespace": config.monitoring_namespace,
        "monitoring_enabled": config.monitoring_enabled
    }

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back or process message
            await websocket.send_json({"type": "echo", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
