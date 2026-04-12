INSERT INTO vehicles (id, manufacturer, model, year, variant, vin, battery_pack_version, motor_variant)
VALUES
    (1, 'Syana Motors', 'EonX', 2025, 'AWD', 'SYNDEMO0001', 'BP-4.1', 'MTR-DUAL')
ON CONFLICT (id) DO NOTHING;

INSERT INTO parts (vehicle_id, part_code, display_name, asset_path, format, external_id)
VALUES
    (1, 'BATTERY_PACK', 'Battery Pack', 'assets/battery_pack.obj', 'OBJ', 'node_battery_pack'),
    (1, 'COOLANT_PUMP', 'Coolant Pump', 'assets/coolant_pump.stl', 'STL', 'node_coolant_pump')
ON CONFLICT (part_code) DO NOTHING;

INSERT INTO diagnosis_steps (id, vehicle_id, step_order, title, instructions, tools_required, safety_warning, estimated_minutes, severity)
VALUES
    (1, 1, 1, 'Verify HV Isolation', 'Power down, lockout-tagout, verify no residual voltage.', 'PPE gloves, CAT III multimeter', 'HIGH VOLTAGE - LOTO mandatory', 10, 'HIGH'),
    (2, 1, 2, 'Inspect Coolant Circuit', 'Inspect pump, hoses, and pressure values.', 'Flashlight', 'Hot fluid risk', 15, 'MEDIUM')
ON CONFLICT (id) DO NOTHING;

INSERT INTO step_part_links (step_id, part_id)
SELECT 1, id FROM parts WHERE part_code = 'BATTERY_PACK'
ON CONFLICT DO NOTHING;

INSERT INTO step_part_links (step_id, part_id)
SELECT 2, id FROM parts WHERE part_code = 'COOLANT_PUMP'
ON CONFLICT DO NOTHING;

INSERT INTO daq_samples (vehicle_id, ts, voltage, current, soc, soh, temp_c, pressure_bar, system_state)
SELECT
    1,
    NOW() - ((60 - gs) || ' minutes')::interval,
    360 + (gs * 0.08),
    32 + (gs % 8),
    82 - (gs * 0.05),
    95,
    31 + (gs % 6) * 0.4,
    1.2,
    CASE WHEN gs % 10 = 0 THEN 'ALERT' ELSE 'NORMAL' END
FROM generate_series(1, 60) AS gs;
