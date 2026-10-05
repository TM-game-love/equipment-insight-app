from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from functools import lru_cache
import csv
import math
import random
import re
from .config import settings

START_DATE = date(2026, 7, 5)
END_DATE = date(2026, 10, 5)
CYCLES_PER_DAY = 600
SAMPLE_INTERVAL_MS = 5
CYCLE_SECONDS = 100
SAMPLES = CYCLE_SECONDS * 1000 // SAMPLE_INTERVAL_MS

def parse_serial(serial: str):
    m = re.fullmatch(r"G(\d{8})-(\d{4})", serial)
    if not m:
        raise ValueError("serial format must be GYYYYMMDD-NNNN")
    d = datetime.strptime(m.group(1), "%Y%m%d").date()
    idx = int(m.group(2))
    return d, idx

@lru_cache(maxsize=1)
def load_features():
    path = Path(settings.mock_csv_path)
    if not path.exists():
        path = Path("/app") / settings.mock_csv_path
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows

@lru_cache(maxsize=2048)
def feature_by_serial(serial: str):
    for r in load_features():
        if r["serial_no"] == serial:
            return r
    raise KeyError(serial)

def serials_for_date(target_date: date):
    if not (START_DATE <= target_date <= END_DATE):
        return []
    return [f"G{target_date:%Y%m%d}-{i:04d}" for i in range(1, CYCLES_PER_DAY+1)]

def cycle_start(serial: str):
    d, idx = parse_serial(serial)
    return datetime.combine(d, datetime.min.time()) + timedelta(hours=6, seconds=(idx-1)*CYCLE_SECONDS)

def _anomaly_params(serial: str):
    feat = feature_by_serial(serial)
    return feat["anomaly_type"], float(feat["anomaly_score"])

def equipment_waveform(serial: str, axis: int):
    if axis < 1 or axis > 6:
        raise ValueError("axis must be 1..6")
    d, idx = parse_serial(serial)
    anomaly, score = _anomaly_params(serial)
    feat = feature_by_serial(serial)
    rng = random.Random(int(d.strftime("%Y%m%d"))*1000 + idx + axis*100000)
    start_ts = cycle_start(serial)
    wear = ((int(feat["dress_count"]) * 900 + idx) % 900) / 900.0

    # Process motion: approach -> grinding -> retract
    points = []
    spike_center = 44.0 + (idx % 11) * 0.55
    chatter_freq = float(feat[f"axis{axis}_dominant_freq_hz"]) or 18.0
    axis_weight = 1.0 if axis in (2,3,4) else 0.45

    for n in range(SAMPLES):
        t = n * SAMPLE_INTERVAL_MS / 1000.0

        if t < 12:
            pos = t / 12 * 20.0
            feed = 1.6
            load = 0.15
        elif t < 78:
            pos = 20.0 + (t-12)/66 * 65.0
            feed = 0.98
            load = 1.0
        else:
            pos = 85.0 - (t-78)/22 * 18.0
            feed = -0.82
            load = 0.25

        pos += axis * 0.8
        torque = (4.0 + axis*0.7) + load*(8.5 + axis*0.9) + 0.8*wear
        feed_val = feed

        # Normal low amplitude modulation
        torque += 0.45 * math.sin(2*math.pi*1.2*t + axis)
        pos += 0.004 * math.sin(2*math.pi*2.0*t + axis)
        feed_val += 0.025 * math.sin(2*math.pi*1.1*t)

        if anomaly == "chatter" and 20 < t < 72:
            torque += axis_weight * (2.5 + 0.4*score) * math.sin(2*math.pi*chatter_freq*t)
            pos += axis_weight * 0.018 * math.sin(2*math.pi*chatter_freq*t + 0.4)
            feed_val += axis_weight * 0.22 * math.sin(2*math.pi*chatter_freq*t + 0.8)

        elif anomaly == "chip_entrapment":
            width = 0.18
            pulse = math.exp(-((t-spike_center)/width)**2)
            torque += axis_weight * (12 + 2*score) * pulse
            feed_val -= axis_weight * 0.55 * pulse
            pos += axis_weight * 0.010 * pulse

        elif anomaly == "backlash" and (10 < t < 18 or 76 < t < 86):
            f = 6.0
            torque += axis_weight * 1.7 * math.sin(2*math.pi*f*t)
            pos += axis_weight * 0.035 * math.sin(2*math.pi*f*t)
            feed_val += axis_weight * 0.25 * math.sin(2*math.pi*f*t + 0.6)

        # Deterministic small noise
        noise = (((n*37 + idx*13 + axis*101) % 100) / 100.0 - 0.5)
        torque += noise * 0.16
        pos += noise * 0.0008
        feed_val += noise * 0.012

        points.append({
            "timestamp": (start_ts + timedelta(milliseconds=n*SAMPLE_INTERVAL_MS)).isoformat(timespec="milliseconds"),
            "time_ms": n*SAMPLE_INTERVAL_MS,
            "position": round(pos, 6),
            "torque": round(torque, 5),
            "feed": round(feed_val, 5),
        })
    return points

def measurement_profile(serial: str):
    d, idx = parse_serial(serial)
    feat = feature_by_serial(serial)
    anomaly = feat["anomaly_type"]
    score = float(feat["anomaly_score"])
    rng = random.Random(int(d.strftime("%Y%m%d"))*1000 + idx + 777)

    pts = []
    for n in range(1000):
        x = n / 999 * 100.0
        y = 0.55*math.sin(2*math.pi*x/32.0) + 0.22*math.sin(2*math.pi*x/8.0)

        if anomaly == "chatter":
            y += (1.2 + 0.25*score) * math.sin(2*math.pi*x/4.5)
        elif anomaly == "chip_entrapment":
            center = 43 + (idx % 13) * 0.7
            y += (5.0 + 0.6*score) * math.exp(-((x-center)/1.3)**2)
        elif anomaly == "backlash":
            y += (1.1 + 0.15*score) * math.sin(2*math.pi*x/13.0)

        noise = (((n*29 + idx*7) % 100)/100 - 0.5) * 0.18
        y += noise
        pts.append({"profile_position": round(x,4), "deviation_um": round(y,5)})

    return {
        "profile": pts,
        "metrics": {
            "profile_rms_um": float(feat["profile_rms_um"]),
            "profile_pv_um": float(feat["profile_pv_um"]),
            "waviness_um": float(feat["waviness_um"]),
            "judgment": feat["judgment"],
        }
    }

def changes(serial: str):
    start = cycle_start(serial)
    feat = feature_by_serial(serial)
    anomaly = feat["anomaly_type"]
    result = [
        {
            "event_time": (start + timedelta(seconds=2)).isoformat(timespec="milliseconds"),
            "item_name": "CycleStart",
            "before_value": "-",
            "after_value": "ON",
            "description": "加工サイクル開始",
        }
    ]
    if anomaly == "chip_entrapment":
        result.append({
            "event_time": (start + timedelta(seconds=46)).isoformat(timespec="milliseconds"),
            "item_name": "TorqueSpike",
            "before_value": "normal",
            "after_value": "high",
            "description": "局所的なトルク急上昇",
        })
    elif anomaly == "chatter":
        result.append({
            "event_time": (start + timedelta(seconds=28)).isoformat(timespec="milliseconds"),
            "item_name": "PeriodicVariation",
            "before_value": "normal",
            "after_value": "oscillation",
            "description": "周期的なトルク/送り変動",
        })
    elif anomaly == "backlash":
        result.append({
            "event_time": (start + timedelta(seconds=13)).isoformat(timespec="milliseconds"),
            "item_name": "PositionVariation",
            "before_value": "normal",
            "after_value": "oscillation",
            "description": "反転近傍で位置揺れ",
        })
    return result

def traceability(serial: str):
    feat = feature_by_serial(serial)
    return {
        "serial_no": serial,
        "assy_serial": feat["assy_serial"],
        "machine_name": feat["machine_name"],
        "production_time": feat["production_time"],
        "wheel_id": feat["wheel_id"],
        "dress_count": int(feat["dress_count"]),
        "anomaly_type": feat["anomaly_type"],
        "judgment": feat["judgment"],
        "lot_no": "LOT-" + feat["production_date"].replace("-","") + "-" + feat["machine_name"],
    }

def period_dashboard(start: date, end: date, machine: str, axis: int):
    if axis < 1 or axis > 6:
        raise ValueError("axis must be 1..6")

    selected = []
    for r in load_features():
        d = date.fromisoformat(r["production_date"])
        if not (start <= d <= end):
            continue
        if machine != "ALL" and r["machine_name"] != machine:
            continue
        selected.append(r)

    # Daily aggregate
    buckets = {}
    for r in selected:
        k = r["production_date"]
        b = buckets.setdefault(k, {
            "date": k, "count": 0, "ng": 0,
            "torque_rms": 0.0, "torque_peak": 0.0,
            "feed_std": 0.0, "position_error": 0.0,
            "profile_rms_um": 0.0, "waviness_um": 0.0,
        })
        b["count"] += 1
        b["ng"] += 1 if r["judgment"] == "NG" else 0
        b["torque_rms"] += float(r[f"axis{axis}_torque_rms"])
        b["torque_peak"] = max(b["torque_peak"], float(r[f"axis{axis}_torque_peak"]))
        b["feed_std"] += float(r[f"axis{axis}_feed_std"])
        b["position_error"] += float(r[f"axis{axis}_position_error"])
        b["profile_rms_um"] += float(r["profile_rms_um"])
        b["waviness_um"] += float(r["waviness_um"])

    daily = []
    for k in sorted(buckets):
        b = buckets[k]
        c = max(b["count"],1)
        daily.append({
            "date": k,
            "count": b["count"],
            "ng_rate": round(b["ng"]/c*100, 3),
            "torque_rms": round(b["torque_rms"]/c, 4),
            "torque_peak": round(b["torque_peak"], 4),
            "feed_std": round(b["feed_std"]/c, 5),
            "position_error": round(b["position_error"]/c, 6),
            "profile_rms_um": round(b["profile_rms_um"]/c, 4),
            "waviness_um": round(b["waviness_um"]/c, 4),
        })

    # Top anomalies
    ranked = sorted(selected, key=lambda r: float(r["anomaly_score"]), reverse=True)[:80]
    anomalies = [{
        "serial_no": r["serial_no"],
        "production_time": r["production_time"],
        "machine_name": r["machine_name"],
        "anomaly_type": r["anomaly_type"],
        "judgment": r["judgment"],
        "anomaly_score": float(r["anomaly_score"]),
        "torque_rms": float(r[f"axis{axis}_torque_rms"]),
        "torque_peak": float(r[f"axis{axis}_torque_peak"]),
        "feed_std": float(r[f"axis{axis}_feed_std"]),
        "position_error": float(r[f"axis{axis}_position_error"]),
        "profile_rms_um": float(r["profile_rms_um"]),
        "waviness_um": float(r["waviness_um"]),
    } for r in ranked]

    # Sampled correlation points (max about 2000)
    step = max(1, len(selected)//2000)
    scatter = [{
        "serial_no": r["serial_no"],
        "x": float(r[f"axis{axis}_torque_rms"]),
        "y": float(r["profile_rms_um"]),
        "judgment": r["judgment"],
        "anomaly_type": r["anomaly_type"],
    } for r in selected[::step]]

    total = len(selected)
    ng = sum(1 for r in selected if r["judgment"] == "NG")
    return {
        "summary": {
            "cycles": total,
            "ng_count": ng,
            "ng_rate": round(ng/max(total,1)*100, 3),
        },
        "daily": daily,
        "anomalies": anomalies,
        "scatter": scatter,
    }
