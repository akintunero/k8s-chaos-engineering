"""API v1 routes — stable surface for integrations."""

from __future__ import annotations

import os
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from loader import load_chaos_modules
from utils import get_config

router = APIRouter(prefix="/api/v1", tags=["v1"])
_mods = load_chaos_modules()
chaos_runner = _mods["chaos_runner"]
config = get_config()

_api_key = os.getenv("CHAOS_API_KEY", "")


def verify_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    if _api_key and x_api_key != _api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


class ExperimentRequest(BaseModel):
    name: str
    namespace: Optional[str] = None


@router.get("/health")
async def health_v1():
    return {"status": "ok", "api_version": "v1"}


@router.get("/experiments", dependencies=[Depends(verify_api_key)])
async def list_experiments_v1():
    return {
        "experiments": chaos_runner.list_experiments(),
        "chaos_env": os.getenv("CHAOS_ENV", "dev"),
    }


@router.post("/experiments/run", dependencies=[Depends(verify_api_key)])
async def run_experiment_v1(request: ExperimentRequest):
    namespace = request.namespace or config.app_namespace
    try:
        chaos_runner.run_experiment(request.name, namespace)
        return {"status": "started", "experiment": request.name, "namespace": namespace}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/experiments/{experiment_name}/stop", dependencies=[Depends(verify_api_key)])
async def stop_experiment_v1(experiment_name: str, namespace: Optional[str] = None):
    ns = namespace or config.app_namespace
    try:
        chaos_runner.stop_experiment(experiment_name, ns)
        return {"status": "stopped", "experiment": experiment_name, "namespace": ns}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/config", dependencies=[Depends(verify_api_key)])
async def config_v1():
    return {
        "api_version": "v1",
        "app_namespace": config.app_namespace,
        "litmus_namespace": config.litmus_namespace,
        "chaos_env": os.getenv("CHAOS_ENV", "dev"),
    }
