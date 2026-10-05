export type EquipmentPoint = {
  timestamp: string;
  time_ms: number;
  position: number;
  torque: number;
  feed: number;
};

export type DailyPoint = {
  date: string;
  count: number;
  ng_rate: number;
  torque_rms: number;
  torque_peak: number;
  feed_std: number;
  position_error: number;
  profile_rms_um: number;
  waviness_um: number;
};

export type AnomalyRow = {
  serial_no: string;
  production_time: string;
  machine_name: string;
  anomaly_type: string;
  judgment: string;
  anomaly_score: number;
  torque_rms: number;
  torque_peak: number;
  feed_std: number;
  position_error: number;
  profile_rms_um: number;
  waviness_um: number;
};

export type ScatterPoint = {
  serial_no: string;
  x: number;
  y: number;
  judgment: string;
  anomaly_type: string;
};
