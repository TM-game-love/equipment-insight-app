# 実DB想定マッピング

## DB1 equipment_raw

```text
serial_no
timestamp
axis_no
position
torque
feed
```

## DB2 change_history

```text
serial_no
event_time
item_name
before_value
after_value
description
```

## DB3 tooth_surface_measurement

```text
serial_no
measurement_time
profile_position
profile_deviation_um
profile_rms_um
profile_pv_um
waviness_um
judgment
```

## DB4 traceability

```text
serial_no
assy_serial
machine_name
wheel_id
dress_count
production_time
lot_no
```
