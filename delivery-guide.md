# Print Studio OpenDesign · 交付说明

## 交付内容

更完整的产品化说明请阅读：`README.zh-CN.md`。

本包交付一个 Codex 可调用的 Skill：`print-studio-opendesign`。

它用于印刷厂接单打样：客户给插画/图片，印刷厂选择产品类型、尺寸、纸张/材质、系列结构，Codex 在规则内生成客户预览、印刷文件、电商白底图/氛围图、QC 报告和交付包。

## 安装方式

将文件夹：

`print-studio-opendesign/`

复制到 Codex skills 目录，例如：

`~/.codex/skills/print-studio-opendesign/`

然后在 Codex 中说：

“使用 print-studio-opendesign，给这组插画做 5×7 台历卡打样。”

## 快速演示

进入 Skill 目录后运行：

```bash
python scripts/preview_config.py config.example.json --all-materials
```

输出：

- `output/小兔子文具/preview/preview.html`
- `output/小兔子文具/preview/materials.html`
- 24 种材质模拟图

完整交付运行：

```bash
python scripts/run.py config.example.json
```

输出：

- 客户预览版：`screen/`
- 印刷交付版：`print/`
- 电商展示版：`commerce/`
- QC 报告：`qc_report.json`
- ZIP 交付包

## V1 范围

已支持：

- 12 个月真实日期日历卡模板
- 5×7、5×5、7×5、塔罗牌、书签、Letter 等尺寸预设
- 客户提供的 24 种纸张/PVC 材质预设
- 300dpi、出血、安全边距、印刷 guide
- 屏幕预览版 / 印刷版 / 电商展示版分离
- 材质选择预览页

暂不承诺：

- CMYK/ICC 真实色彩管理
- ERP/报价系统集成
- 烫金/UV/压纹的生产级模拟
- 多用户 Web 后台

## 重要说明

材质预览为屏幕模拟，仅用于销售沟通和初步选材；最终颜色、纹理、珠光、PVC 光泽、纸芯侧边效果，以实物纸样和打样为准。
