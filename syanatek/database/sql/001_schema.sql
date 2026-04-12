CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    manufacturer VARCHAR(64) NOT NULL,
    model VARCHAR(64) NOT NULL,
    year INTEGER NOT NULL,
    variant VARCHAR(64),
    vin VARCHAR(64),
    battery_pack_version VARCHAR(64),
    motor_variant VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS daq_samples (
    id BIGSERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    voltage DOUBLE PRECISION,
    current DOUBLE PRECISION,
    soc DOUBLE PRECISION,
    soh DOUBLE PRECISION,
    temp_c DOUBLE PRECISION,
    pressure_bar DOUBLE PRECISION,
    system_state VARCHAR(32)
);
CREATE INDEX IF NOT EXISTS idx_daq_vehicle_ts ON daq_samples(vehicle_id, ts DESC);

CREATE TABLE IF NOT EXISTS parts (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    part_code VARCHAR(64) NOT NULL UNIQUE,
    display_name VARCHAR(128) NOT NULL,
    asset_path TEXT NOT NULL,
    format VARCHAR(16) NOT NULL,
    external_id VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS diagnosis_steps (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    title VARCHAR(128) NOT NULL,
    instructions TEXT NOT NULL,
    tools_required TEXT,
    safety_warning TEXT,
    estimated_minutes INTEGER,
    severity VARCHAR(16),
    completed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS step_part_links (
    id SERIAL PRIMARY KEY,
    step_id INTEGER NOT NULL REFERENCES diagnosis_steps(id) ON DELETE CASCADE,
    part_id INTEGER NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    UNIQUE(step_id, part_id)
);
