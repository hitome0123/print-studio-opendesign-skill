# 客户验收 SOP

> 目标：客户拿到 Skill 后，能在 30 分钟内跑通第一套示例，并知道结果算不算成功。

## 1. 安装

### Codex

把插件目录放到 Codex 可识别的插件位置，或直接使用独立 Skill：

```text
print-studio-opendesign/
```

### Claude Code

在仓库根目录运行：

```bash
bash claude-code/install.sh
```

## 2. 跑第一个示例

进入 runtime：

```bash
cd plugins/print-studio-opendesign/skills/print-studio-runtime
```

运行贺卡示例：

```bash
python scripts/run.py examples/greeting-card-5x7.json
```

成功标准：

- 终端出现 `质检 ✅ PASS`
- 出现 `output/花园贺卡/`
- 出现 `花园贺卡_交付包.zip`

## 3. 跑材质选择页

```bash
python scripts/preview_config.py examples/greeting-card-5x7.json --all-materials
```

成功标准：

- 出现 `preview.html`
- 出现 `materials.html`
- `materials/` 下有 24 张材质图

## 4. 跑挂历示例

```bash
python scripts/run.py examples/wall-calendar-8x12.json
```

成功标准：

- 12 张月份图都生成。
- 顶部有线圈/装订区。
- `qc_report.json` 无 FAIL。

## 5. 客户修改自己的项目

建议客户先复制一个示例配置：

```bash
cp examples/greeting-card-5x7.json jobs/customer-a-card.json
```

然后改：

- `job.client_name`
- `job.job_name`
- `theme`
- `illustrations_dir`
- `preset.size`
- `preset.material`
- `series.count`
- `content`
- `outputs`
- `production`

## 6. 交付结果怎么看

| 文件夹 / 文件 | 用途 |
| --- | --- |
| `preview/preview.html` | 客户快速看尺寸、材质、印刷 guide |
| `preview/materials.html` | 24 种材质选择页 |
| `screen/` | 客户预览图 |
| `print/` | 300dpi 印刷文件 |
| `commerce/` | 白底图 / 氛围图 |
| `qc_report.json` | 自动质检 |
| `*_交付包.zip` | 交付压缩包 |

## 7. 验收结论

可以验收为 Beta 的条件：

- 安装成功。
- 至少一个贺卡示例 PASS。
- 至少一个材质选择页生成成功。
- 至少一个客户素材项目能生成预览。
- 客户理解 V1 不承诺 CMYK/ICC、生产级烫金 UV、ERP 报价系统。

