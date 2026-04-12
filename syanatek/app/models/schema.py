from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    manufacturer: Mapped[str] = mapped_column(String(64), index=True)
    model: Mapped[str] = mapped_column(String(64), index=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    variant: Mapped[str | None] = mapped_column(String(64), nullable=True)
    vin: Mapped[str | None] = mapped_column(String(64), nullable=True)
    battery_pack_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    motor_variant: Mapped[str | None] = mapped_column(String(64), nullable=True)

    steps: Mapped[list[DiagnosisStep]] = relationship(back_populates="vehicle")


class DaqSample(Base):
    __tablename__ = "daq_samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True)
    ts: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    voltage: Mapped[float | None] = mapped_column(Float, nullable=True)
    current: Mapped[float | None] = mapped_column(Float, nullable=True)
    soc: Mapped[float | None] = mapped_column(Float, nullable=True)
    soh: Mapped[float | None] = mapped_column(Float, nullable=True)
    temp_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    pressure_bar: Mapped[float | None] = mapped_column(Float, nullable=True)
    system_state: Mapped[str | None] = mapped_column(String(32), nullable=True)


class Part(Base):
    __tablename__ = "parts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True)
    part_code: Mapped[str] = mapped_column(String(64), unique=True)
    display_name: Mapped[str] = mapped_column(String(128))
    asset_path: Mapped[str] = mapped_column(Text)
    format: Mapped[str] = mapped_column(String(16))
    external_id: Mapped[str | None] = mapped_column(String(128), nullable=True)


class DiagnosisStep(Base):
    __tablename__ = "diagnosis_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True)
    step_order: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(128))
    instructions: Mapped[str] = mapped_column(Text)
    tools_required: Mapped[str | None] = mapped_column(Text, nullable=True)
    safety_warning: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(16), nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)

    vehicle: Mapped[Vehicle] = relationship(back_populates="steps")
    links: Mapped[list[StepPartLink]] = relationship(back_populates="step")


class StepPartLink(Base):
    __tablename__ = "step_part_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    step_id: Mapped[int] = mapped_column(ForeignKey("diagnosis_steps.id"), index=True)
    part_id: Mapped[int] = mapped_column(ForeignKey("parts.id"), index=True)

    step: Mapped[DiagnosisStep] = relationship(back_populates="links")
