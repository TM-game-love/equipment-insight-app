# 解析ガイド

## A. ビビり / 振動

注目:
- Torque RMS上昇
- Torqueの周期成分
- Feed Std上昇
- Position Error上昇
- 測定側Waviness上昇

設備波形と測定波形に似た周期性があるかを見る。

## B. 砥粒・切りくず巻き込み

注目:
- Torqueの瞬間Peak
- Spike回数
- 同時刻のFeed低下
- 同じ加工位置における歯面Profileの局所Peak

「時間」だけでなく「Position」を共通軸にして比較する。

## C. ガタ / バックラッシ

注目:
- Position Error
- 反転時のPosition揺れ
- Feedばらつき
- Torqueの低周波周期変動
- 測定側の低周波うねり

## D. 砥石摩耗

注目:
- Torque RMSの長期上昇
- Torque Peakの上昇
- Profile RMS / Wavinessの徐々悪化
- ドレッシング前後で特徴量が戻るか

## E. 品質との相関

以下の散布図を使う。

- Torque RMS vs Profile RMS
- Torque Peak vs Profile P-V
- Feed Std vs Waviness
- Position Error vs Profile RMS

相関が強い軸・特徴量を絞り込み、1サイクル波形で原因箇所を確認する。

## F. 5msデータの限界

5ms = 200Hz sampling。
Nyquist上限は100Hz。

100Hzより高い研削振動を本格的に見るには、
加速度センサ等をより高速で取得する。
