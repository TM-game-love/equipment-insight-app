# Mock Data

期間: 2026-07-05 ～ 2026-10-05  
600サイクル/日  
合計: 55,800

## 異常モード

- normal
- chatter
- chip_entrapment
- backlash

## 期間特徴量CSV

`backend/mock_data/period_features_3months.csv`

1サイクル1行。

6軸それぞれ:
- torque_rms
- torque_peak
- feed_std
- position_error
- dominant_freq_hz

品質:
- profile_rms_um
- profile_pv_um
- waviness_um
- judgment
- anomaly_score

## 5ms RAW

3ヶ月分を全部保存すると巨大になるため、
選択されたSerial + AxisについてFastAPIが20,000点を再現生成する。
