# 客户使用对话示例

> 这些不是技术文档，是给印刷厂老板、销售、客服、设计助理照着说的。

## 场景 1：客户要做 5×7 贺卡

客户说：

```text
使用 print-studio-order-intake。
客户要做一套 5×7 贺卡，300g 超白白卡纸，单面，圆角，素材在 ./客户A/花园贺卡/images。
先帮我生成配置，输出客户预览、印刷文件、材质选择页和 QC。
```

AI 应该做：

1. 复制 `examples/greeting-card-5x7.json`。
2. 改客户名、项目名、素材路径、材质、圆角。
3. 运行材质预览：

```bash
python scripts/preview_config.py <config.json> --all-materials
```

4. 等客户确认材质后运行：

```bash
python scripts/run.py <config.json>
```

5. 告诉客户看：

- `preview/materials.html`
- `screen/`
- `print/`
- `qc_report.json`
- `*_交付包.zip`

## 场景 2：客户只想先看材质效果

客户说：

```text
使用 print-studio-material-selector。
这套图客户还没确定纸张，先生成所有材质预览页。
重点让她比较 300g 白卡、300g 蓝芯纸、310g 黑芯纸、珠光纸和 PVC。
```

AI 应该做：

1. 检查 config 里尺寸和素材路径。
2. 运行：

```bash
python scripts/preview_config.py <config.json> --all-materials
```

3. 输出销售提示：

```text
白卡纸适合常规贺卡和日历。
蓝芯纸更适合卡牌和高挺度卡片，侧边会有蓝芯效果。
黑芯纸更高级、抗透光，但浅色图要注意对比。
珠光纸适合礼品和婚礼风格，小字谨慎。
PVC 适合防水卡片，需确认磨砂/光面。
```

## 场景 3：客户要做挂历

客户说：

```text
使用 print-studio-calendar-series。
客户要做 8×12 英寸挂历，12 个月，顶部线圈装订，300g 白卡纸。
年份 2027，周日开始。素材在 ./客户B/植物挂历/images。
先生成客户预览和印刷文件。
```

AI 应该做：

1. 复制 `examples/wall-calendar-8x12.json`。
2. 设置：

```text
preset.product_type = wall_calendar
preset.size = wall_cal_8x12
preset.product_form = wall_coil
production.binding = top_wire
production.binding_reserved_mm = 12
```

3. 运行：

```bash
python scripts/run.py <config.json>
```

4. 检查：

- 顶部线圈区是否可见。
- 日期是否完整。
- 重要内容是否避开顶部装订区。
- QC 是否 PASS。

## 场景 4：客户要做 4 张书签套装

客户说：

```text
使用 print-studio-layout-proof。
客户要做 4 张植物书签，2×6 英寸，300g 白卡纸，单面。
每张标题分别是 Spring、Summer、Autumn、Winter。
素材在 ./客户C/四季书签/images。
```

AI 应该做：

1. 复制 `examples/bookmark-2x6-set.json`。
2. 设置：

```text
series.count = 4
preset.product_type = bookmark
preset.size = bookmark_2x6
content.card_titles = ["Spring", "Summer", "Autumn", "Winter"]
```

3. 运行完整打样：

```bash
python scripts/run.py <config.json>
```

## 场景 5：客户要自定义尺寸

客户说：

```text
使用 print-studio-order-intake。
客户要做包装插卡，尺寸 9cm × 12cm，300g 雅白莱妮纹，双面，圆角 3mm。
素材在 ./客户D/包装插卡/images。
```

AI 应该做：

1. 选择最接近的产品：

```text
preset.product_type = packaging_insert
```

2. 设置自定义尺寸：

```json
"advanced": {
  "custom_size": {
    "w": 9,
    "h": 12,
    "unit": "cm"
  }
}
```

3. 设置生产规则：

```json
"production": {
  "double_sided": true,
  "round_corners": {
    "enabled": true,
    "radius_mm": 3
  }
}
```

4. 如果需要背面输出，确认：

```json
"outputs": {
  "types": ["single", "grid", "back"]
}
```

## 客户确认话术

生成预览后，可以这样回复客户：

```text
这版是客户确认预览，不是最终批量印刷承诺。
当前已包含：尺寸、材质模拟、出血、安全边距、印刷版文件和 QC 报告。
材质纹理、珠光、PVC 光泽、纸芯侧边效果以实物纸样和打样为准。
如果确认版式和材质，我们再出最终生产交付包。
```

