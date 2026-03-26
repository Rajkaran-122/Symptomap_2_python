#!/usr/bin/env python3
"""
Seed exactly N local doctor_outbreaks with a fixed approved/pending split.

Default target:
- add_total: 2000
- add_approved: 500
- add_pending: 1500

This script is intentionally scoped to backend-python/symptomap.db and
expects execution from the backend-python directory.
"""

import argparse
import random
import shutil
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


DISEASES = [
    "Dengue",
    "Malaria",
    "Typhoid",
    "Cholera",
    "COVID-19",
    "Viral Fever",
    "Chikungunya",
    "Flu",
    "Hepatitis A",
    "Tuberculosis",
]

HOSPITAL_PREFIXES = [
    "City General Hospital",
    "District Medical Center",
    "Community Health Centre",
    "Apollo Care Hospital",
    "Fortis Clinic",
    "Max Super Specialty",
    "Medanta Hospital",
    "Sunrise Medical Institute",
    "Lifeline Hospital",
    "Metro Public Hospital",
]

CITY_POOL = [
    {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lon": 72.8777},
    {"city": "Delhi", "state": "Delhi", "lat": 28.7041, "lon": 77.1025},
    {"city": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946},
    {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lon": 80.2707},
    {"city": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lon": 88.3639},
    {"city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lon": 78.4867},
    {"city": "Pune", "state": "Maharashtra", "lat": 18.5204, "lon": 73.8567},
    {"city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lon": 72.5714},
    {"city": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lon": 75.7873},
    {"city": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lon": 80.9462},
    {"city": "Patna", "state": "Bihar", "lat": 25.5941, "lon": 85.1376},
    {"city": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lon": 77.4126},
    {"city": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lon": 75.8577},
    {"city": "Nagpur", "state": "Maharashtra", "lat": 21.1458, "lon": 79.0882},
    {"city": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.6868, "lon": 83.2185},
    {"city": "Surat", "state": "Gujarat", "lat": 21.1702, "lon": 72.8311},
    {"city": "Kochi", "state": "Kerala", "lat": 9.9312, "lon": 76.2673},
    {"city": "Thiruvananthapuram", "state": "Kerala", "lat": 8.5241, "lon": 76.9366},
    {"city": "Guwahati", "state": "Assam", "lat": 26.1445, "lon": 91.7362},
    {"city": "Ranchi", "state": "Jharkhand", "lat": 23.3441, "lon": 85.3096},
    {"city": "Raipur", "state": "Chhattisgarh", "lat": 21.2514, "lon": 81.6296},
    {"city": "Bhubaneswar", "state": "Odisha", "lat": 20.2961, "lon": 85.8245},
    {"city": "Chandigarh", "state": "Punjab", "lat": 30.7333, "lon": 76.7794},
    {"city": "Dehradun", "state": "Uttarakhand", "lat": 30.3165, "lon": 78.0322},
    {"city": "Shimla", "state": "Himachal Pradesh", "lat": 31.1048, "lon": 77.1734},
    {"city": "Srinagar", "state": "Jammu & Kashmir", "lat": 34.0837, "lon": 74.7973},
    {"city": "Jammu", "state": "Jammu & Kashmir", "lat": 32.7266, "lon": 74.8570},
    {"city": "Amritsar", "state": "Punjab", "lat": 31.6340, "lon": 74.8723},
    {"city": "Ludhiana", "state": "Punjab", "lat": 30.9010, "lon": 75.8573},
    {"city": "Nashik", "state": "Maharashtra", "lat": 19.9975, "lon": 73.7898},
]

EXPECTED_TABLE = "doctor_outbreaks"
INSERT_COLUMNS = [
    "disease_type",
    "patient_count",
    "severity",
    "latitude",
    "longitude",
    "location_name",
    "city",
    "state",
    "description",
    "date_reported",
    "submitted_by",
    "created_at",
    "status",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed local outbreaks with fixed approved split.")
    parser.add_argument("--add-total", type=int, default=2000, help="Total new rows to add.")
    parser.add_argument("--add-approved", type=int, default=500, help="Approved rows within new rows.")
    parser.add_argument(
        "--db-path",
        type=str,
        default="./symptomap.db",
        help="Database path. Must resolve to backend-python/symptomap.db.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible data.")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=250,
        help="Insert batch size (must be between 200 and 500).",
    )
    return parser.parse_args()


def fail(message: str) -> "None":
    print(f"ERROR: {message}")
    raise RuntimeError(message)


def resolve_db_path(db_path_arg: str) -> Path:
    script_dir = Path(__file__).resolve().parent
    expected_cwd = script_dir
    cwd = Path.cwd().resolve()

    if cwd != expected_cwd:
        fail(
            f"Run this script from backend-python only. "
            f"current_cwd={cwd} expected_cwd={expected_cwd}"
        )

    expected_db = (script_dir / "symptomap.db").resolve()
    candidate = Path(db_path_arg)
    resolved = (cwd / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()

    if resolved != expected_db:
        fail(
            f"Resolved db path must be backend-python/symptomap.db. "
            f"resolved={resolved} expected={expected_db}"
        )
    if not resolved.exists():
        fail(f"Database file does not exist at {resolved}")
    return resolved


def create_backup(db_path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.with_name(f"{db_path.name}.bak.{timestamp}")
    shutil.copy2(db_path, backup_path)
    print(f"backup_created={backup_path}")
    return backup_path


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def validate_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (EXPECTED_TABLE,),
    )
    if cur.fetchone() is None:
        fail(f"Required table not found: {EXPECTED_TABLE}")

    cur.execute(f"PRAGMA table_info({EXPECTED_TABLE})")
    cols = {row["name"] for row in cur.fetchall()}
    missing = [col for col in INSERT_COLUMNS if col not in cols]
    if missing:
        fail(f"Schema drift detected. Missing columns in {EXPECTED_TABLE}: {missing}")


def get_counts(conn: sqlite3.Connection) -> Tuple[int, int, int]:
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) AS c FROM {EXPECTED_TABLE}")
    total = int(cur.fetchone()["c"])
    cur.execute(f"SELECT COUNT(*) AS c FROM {EXPECTED_TABLE} WHERE status='approved'")
    approved = int(cur.fetchone()["c"])
    cur.execute(f"SELECT COUNT(*) AS c FROM {EXPECTED_TABLE} WHERE status='pending'")
    pending = int(cur.fetchone()["c"])
    return total, approved, pending


def choose_severity(rng: random.Random) -> str:
    return rng.choices(
        population=["mild", "moderate", "severe"],
        weights=[0.45, 0.35, 0.20],
        k=1,
    )[0]


def choose_patient_count(rng: random.Random, severity: str) -> int:
    if severity == "mild":
        return rng.randint(5, 30)
    if severity == "moderate":
        return rng.randint(20, 80)
    return rng.randint(50, 180)


def random_iso_in_last_90_days(rng: random.Random) -> str:
    now = datetime.now(timezone.utc)
    days_back = rng.randint(0, 89)
    seconds_back = rng.randint(0, 86399)
    ts = now - timedelta(days=days_back, seconds=seconds_back)
    return ts.replace(microsecond=0).isoformat()


def build_rows(add_total: int, add_approved: int, rng: random.Random) -> List[Tuple]:
    add_pending = add_total - add_approved
    statuses = ["approved"] * add_approved + ["pending"] * add_pending
    rng.shuffle(statuses)

    rows: List[Tuple] = []
    for status in statuses:
        city = rng.choice(CITY_POOL)
        disease = rng.choice(DISEASES)
        severity = choose_severity(rng)
        patient_count = choose_patient_count(rng, severity)
        latitude = round(city["lat"] + rng.uniform(-0.08, 0.08), 6)
        longitude = round(city["lon"] + rng.uniform(-0.08, 0.08), 6)
        location_name = f"{city['city']} {rng.choice(HOSPITAL_PREFIXES)}"
        ts = random_iso_in_last_90_days(rng)
        description = (
            f"Seeded {severity} {disease} outbreak in {city['city']} for local "
            f"testing and analytics calibration."
        )

        rows.append(
            (
                disease,
                patient_count,
                severity,
                latitude,
                longitude,
                location_name,
                city["city"],
                city["state"],
                description,
                ts,
                "seed_2000_500",
                ts,
                status,
            )
        )
    rng.shuffle(rows)
    return rows


def insert_rows(
    conn: sqlite3.Connection,
    rows: Sequence[Tuple],
    batch_size: int,
) -> None:
    placeholders = ", ".join(["?"] * len(INSERT_COLUMNS))
    sql = (
        f"INSERT INTO {EXPECTED_TABLE} "
        f"({', '.join(INSERT_COLUMNS)}) VALUES ({placeholders})"
    )

    conn.execute("BEGIN")
    try:
        total_rows = len(rows)
        for offset in range(0, total_rows, batch_size):
            batch = rows[offset : offset + batch_size]
            conn.executemany(sql, batch)
            done = offset + len(batch)
            print(f"insert_progress={done}/{total_rows}")
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def main() -> int:
    args = parse_args()

    if args.add_total <= 0:
        fail("--add-total must be > 0")
    if args.add_approved < 0:
        fail("--add-approved must be >= 0")
    if args.add_approved > args.add_total:
        fail("--add-approved cannot exceed --add-total")
    if args.batch_size < 200 or args.batch_size > 500:
        fail("--batch-size must be between 200 and 500")

    db_path = resolve_db_path(args.db_path)
    create_backup(db_path)

    rng = random.Random(args.seed)
    conn = connect(db_path)
    try:
        validate_schema(conn)
        pre_total, pre_approved, pre_pending = get_counts(conn)
        print(f"pre_total={pre_total}")
        print(f"pre_approved={pre_approved}")
        print(f"pre_pending={pre_pending}")

        rows = build_rows(args.add_total, args.add_approved, rng)
        inserted = Counter(row[-1] for row in rows)
        inserted_total = len(rows)
        inserted_approved = inserted.get("approved", 0)
        inserted_pending = inserted.get("pending", 0)

        if inserted_total != args.add_total:
            fail("Generated row total does not match --add-total")
        if inserted_approved != args.add_approved:
            fail("Generated approved total does not match --add-approved")
        if inserted_pending != (args.add_total - args.add_approved):
            fail("Generated pending total does not match expected remainder")

        print(f"inserted_total_precommit={inserted_total}")
        print(f"inserted_approved_precommit={inserted_approved}")
        print(f"inserted_pending_precommit={inserted_pending}")

        insert_rows(conn, rows, args.batch_size)

        post_total, post_approved, post_pending = get_counts(conn)
        print(f"post_total={post_total}")
        print(f"post_approved={post_approved}")
        print(f"post_pending={post_pending}")

        delta_total = post_total - pre_total
        delta_approved = post_approved - pre_approved
        delta_pending = post_pending - pre_pending

        print(f"delta_total={delta_total}")
        print(f"delta_approved={delta_approved}")
        print(f"delta_pending={delta_pending}")

        expected_pending_add = args.add_total - args.add_approved
        if (
            delta_total != args.add_total
            or delta_approved != args.add_approved
            or delta_pending != expected_pending_add
        ):
            fail(
                "Post-commit verification failed. "
                f"expected_delta=({args.add_total}, {args.add_approved}, {expected_pending_add}) "
                f"actual_delta=({delta_total}, {delta_approved}, {delta_pending})"
            )

        print("verification=SUCCESS")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"fatal_error={exc}")
        raise SystemExit(1)
