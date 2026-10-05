from datetime import date
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from . import mock_service

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"name": settings.app_name, "mock_mode": settings.mock_mode, "docs": "/docs"}

@app.get("/api/mock/info")
async def mock_info():
    return {
        "start_date": mock_service.START_DATE,
        "end_date": mock_service.END_DATE,
        "cycles_per_day": mock_service.CYCLES_PER_DAY,
        "sample_interval_ms": mock_service.SAMPLE_INTERVAL_MS,
        "cycle_seconds": mock_service.CYCLE_SECONDS,
        "total_cycles": len(mock_service.load_features()),
    }

@app.get("/api/serials")
async def serials(date_: date = Query(alias="date")):
    return {"serials": mock_service.serials_for_date(date_)}

@app.get("/api/cycle/{serial}/equipment")
async def cycle_equipment(serial: str, axis: int = Query(1, ge=1, le=6)):
    try:
        data = mock_service.equipment_waveform(serial, axis)
        feat = mock_service.feature_by_serial(serial)
        return {
            "serial": serial,
            "axis": axis,
            "sample_interval_ms": 5,
            "features": {
                "torque_rms": float(feat[f"axis{axis}_torque_rms"]),
                "torque_peak": float(feat[f"axis{axis}_torque_peak"]),
                "feed_std": float(feat[f"axis{axis}_feed_std"]),
                "position_error": float(feat[f"axis{axis}_position_error"]),
                "dominant_freq_hz": float(feat[f"axis{axis}_dominant_freq_hz"]),
            },
            "data": data,
        }
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/cycle/{serial}/measurement")
async def cycle_measurement(serial: str):
    try:
        return mock_service.measurement_profile(serial)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/cycle/{serial}/changes")
async def cycle_changes(serial: str):
    try:
        return {"data": mock_service.changes(serial)}
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/cycle/{serial}/traceability")
async def cycle_traceability(serial: str):
    try:
        return mock_service.traceability(serial)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/period/dashboard")
async def period_dashboard(
    start: date,
    end: date,
    machine: str = "ALL",
    axis: int = Query(1, ge=1, le=6),
):
    if start > end:
        raise HTTPException(status_code=400, detail="start must be <= end")
    if (end-start).days > 366:
        raise HTTPException(status_code=400, detail="range too large")
    return mock_service.period_dashboard(start, end, machine, axis)
