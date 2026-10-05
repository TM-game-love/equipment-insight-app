# Equipment Insight 仕様書

## 1. 対象設備

歯車の歯面を研削する設備。

設備側では6軸の以下を取得する。

- Position
- Torque
- Feed
- Serial
- Timestamp

5msサンプリング、1サイクル約100秒を想定。

測定器では加工後の歯面をなぞり、歯面形状・表面状態を測定する。

## 2. 想定する不具合

- 歯面のガタつき/周期的なうねり
- 砥粒や切りくずの巻き込み
- 形状不良
- 加工中の振動/ビビり
- 軸のガタ/バックラッシ
- 砥石摩耗による徐々悪化

## 3. 解析方針

### 1サイクル解析

- 6軸を切替
- Position / Torque / Feed を同一時間軸で表示
- Position-Torque XY
- 歯面プロファイル
- 変化点
- トレサビ

### 期間解析

1サイクルごとに特徴量化する。

設備特徴量:
- Torque RMS
- Torque Peak
- Torque Spike
- Feed Std
- Position Error
- Dominant Frequency

品質特徴量:
- Profile RMS
- Peak-to-Valley
- Waviness
- OK/NG

期間解析では、設備特徴量と品質特徴量を同じシリアルで紐付ける。

## 4. ドリルダウン

期間解析
→ 異常シリアルを発見
→ クリック
→ 1サイクル解析へ移動
→ 5ms波形と歯面測定波形を確認

## 5. 4DB

DB1: 生設備データ  
DB2: 変化点履歴  
DB3: 歯面測定データ  
DB4: トレサビ

FastAPIが各DBを統合する。
