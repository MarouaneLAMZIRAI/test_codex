from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pandas as pd
from sqlalchemy import Select, and_, select

from app.models.schema import DaqSample, DiagnosisStep, Part, StepPartLink, Vehicle
from app.services.db import db_service

logger = logging.getLogger(__name__)


@dataclass
class VehicleFilter:
    manufacturer: str
    model: str
    year: int
    variant: str | None


class Repository:
    def get_vehicle_filters(self) -> list[VehicleFilter]:
        if not db_service.online:
            return [
                VehicleFilter("Syana Motors", "EonX", 2025, "AWD"),
                VehicleFilter("Syana Motors", "EonX", 2024, "RWD"),
            ]

        stmt: Select = select(Vehicle.manufacturer, Vehicle.model, Vehicle.year, Vehicle.variant).order_by(
            Vehicle.manufacturer, Vehicle.model, Vehicle.year
        )
        with db_service.session_scope() as session:
            rows = session.execute(stmt).all()
        return [VehicleFilter(*row) for row in rows]

    def get_vehicle_id(self, vf: VehicleFilter) -> int | None:
        if not db_service.online:
            return 1
        stmt = select(Vehicle.id).where(
            and_(
                Vehicle.manufacturer == vf.manufacturer,
                Vehicle.model == vf.model,
                Vehicle.year == vf.year,
                Vehicle.variant == vf.variant,
            )
        )
        with db_service.session_scope() as session:
            return session.execute(stmt).scalar_one_or_none()

    def get_kpi_timeseries(self, vehicle_id: int, hours: int = 1) -> pd.DataFrame:
        if not db_service.online:
            now = datetime.now(timezone.utc)
            records = []
            for i in range(60):
                records.append(
                    {
                        "ts": now - timedelta(minutes=59 - i),
                        "voltage": 364 + i * 0.03,
                        "current": 35 + (i % 10) * 0.8,
                        "soc": 78 - i * 0.04,
                        "temp_c": 33 + (i % 7) * 0.3,
                    }
                )
            return pd.DataFrame(records)

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        stmt = (
            select(DaqSample.ts, DaqSample.voltage, DaqSample.current, DaqSample.soc, DaqSample.temp_c)
            .where(and_(DaqSample.vehicle_id == vehicle_id, DaqSample.ts >= cutoff))
            .order_by(DaqSample.ts)
        )
        with db_service.session_scope() as session:
            rows = session.execute(stmt).all()
        return pd.DataFrame(rows, columns=["ts", "voltage", "current", "soc", "temp_c"])

    def get_steps(self, vehicle_id: int) -> list[DiagnosisStep]:
        if not db_service.online:
            return [
                DiagnosisStep(
                    id=1,
                    vehicle_id=1,
                    step_order=1,
                    title="Verify HV Isolation",
                    instructions="Power down system, apply LOTO, and verify isolation before touching busbars.",
                    tools_required="PPE gloves, multimeter",
                    safety_warning="High Voltage - Follow LOTO",
                    estimated_minutes=10,
                    severity="HIGH",
                ),
                DiagnosisStep(
                    id=2,
                    vehicle_id=1,
                    step_order=2,
                    title="Inspect Coolant Loop",
                    instructions="Check pump operation and inspect hoses for restriction/leakage.",
                    tools_required="Flashlight",
                    safety_warning="Hot coolant risk",
                    estimated_minutes=15,
                    severity="MEDIUM",
                ),
            ]

        stmt = select(DiagnosisStep).where(DiagnosisStep.vehicle_id == vehicle_id).order_by(DiagnosisStep.step_order)
        with db_service.session_scope() as session:
            return list(session.scalars(stmt).all())

    def get_target_part_codes(self, step_id: int) -> list[str]:
        if not db_service.online:
            if step_id == 1:
                return ["BATTERY_PACK"]
            if step_id == 2:
                return ["COOLANT_PUMP"]
            return []

        stmt = (
            select(Part.part_code)
            .join(StepPartLink, StepPartLink.part_id == Part.id)
            .where(StepPartLink.step_id == step_id)
        )
        with db_service.session_scope() as session:
            return [x[0] for x in session.execute(stmt).all()]
