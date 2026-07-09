# 正弦焊接轨迹核对报告

结论：你指出的问题是对的。前面的 B1/B2 结果只是短时间链路验证，并没有完成“沿 X 方向焊完整板”的效果。

## 当前 UDF 轨迹

- `x_center(t) = v * t`
- `y_center(t) = A * sin(2*pi*freq*t)`
- `v = 0.003 m/s`
- `A = 0.003 m`
- `freq = 2.0 Hz`

所以正弦轨迹本身已经写进 UDF，但前面只跑到 `0.35 s`：

- 已前进距离：`1.05 mm`
- 100 mm 全板需要：`33.33 s`
- 30 mm 局部板需要：`10.00 s`
- 空间波长：`v/f = 1.50 mm`
- 100 mm 全板约有 `66.7` 个正弦周期
- 30 mm 局部板约有 `20.0` 个正弦周期

## 输出文件

- 轨迹 CSV：`private-run/sinusoidal_weld_path_100mm.csv`
- 轨迹 SVG：`private-run/sinusoidal_weld_path_100mm.svg`
- 轨迹 PNG：`private-run/sinusoidal_weld_path_100mm.png`

## 修正建议

如果要在 Fluent 结果里真正看到“正弦焊缝沿板前进”的效果，下一步应单独建立 `Stage A3_full_track`：

1. 使用完整 `100 mm x 30 mm x 10 mm` 或至少当前 `30 mm` 局部板的长时间热传导模型。
2. 让热源从入口前进到出口，而不是只跑 0.35 s。
3. 增加一个轨迹累积 UDM 或导出多时刻温度图，这样后处理里可以直接看到蛇形热影响带。
4. 若保持物理速度，100 mm 全板至少需要 `33.33 s` 物理时间；这会比 B1/B2 的短验证慢很多，不能拿 0.35 s 截图冒充全板焊接。
