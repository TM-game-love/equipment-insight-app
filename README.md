# Equipment Insight - Gear Grinding Analytics

解析MVPです。

## 主な機能

- 1サイクル解析
  - 6軸の Position / Torque / Feed
  - 5msサンプリング、100秒
  - Position-Torque解析
  - 測定器の歯面プロファイル
  - 変化点履歴
  - トレサビ
- 期間解析
  - 期間 / 設備 / 軸でフィルタ
  - Torque RMS / Peak
  - Feedばらつき
  - Position誤差
  - 歯面Profile RMS / P-V / Waviness
  - NG率
  - 異常シリアルランキング
  - 設備特徴量と品質の相関
  - 異常シリアルから1サイクルへドリルダウン

## Mock期間

- 2026-07-05 ～ 2026-10-05
- 600サイクル/日
- 合計 55,800サイクル
- シリアル: `GYYYYMMDD-NNNN`

## 起動

```powershell
docker compose up -d --build
```

Web:

```text
http://localhost:3000
```

FastAPI Swagger:

```text
http://localhost:8000/docs
```

## 実DBへの切替

`backend/.env`

```env
MOCK_MODE=false

DB1_URL=postgresql+asyncpg://...
DB2_URL=postgresql+asyncpg://...
DB3_URL=postgresql+asyncpg://...
DB4_URL=postgresql+asyncpg://...
```

実DB接続用のSQLは `backend/app/repositories.py` に集約しています。

## 注意

5msサンプリングは200Hzなので、理論上100Hz未満の変動を見る用途です。
より高周波の研削振動を本格解析する場合は、別途振動センサ/高速DAQの追加を推奨します。
