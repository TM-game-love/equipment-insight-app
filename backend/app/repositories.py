"""
実DBへ切り替える際のSQL置き場。
MOCK_MODE=true の間は未使用。
"""

EQUIPMENT_SQL = """
SELECT serial_no, timestamp, axis_no, position, torque, feed
FROM equipment_raw
WHERE serial_no = :serial
  AND axis_no = :axis
ORDER BY timestamp
"""

MEASUREMENT_SQL = """
SELECT serial_no, measurement_time, profile_position, profile_deviation_um
FROM tooth_surface_measurement
WHERE serial_no = :serial
ORDER BY profile_position
"""

CHANGES_SQL = """
SELECT event_time, item_name, before_value, after_value, description
FROM change_history
WHERE serial_no = :serial
ORDER BY event_time
"""

TRACE_SQL = """
SELECT serial_no, assy_serial, machine_name, wheel_id, dress_count,
       production_time, lot_no
FROM traceability
WHERE serial_no = :serial
"""
