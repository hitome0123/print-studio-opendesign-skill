# Print Studio OpenDesign · 交付说明

## 交付内容

更完整的产品化说明请阅读：`README.zh-CN.md`。

本包交付两种 Codex 可调用形态：

- 独立 Skill：`print-studio-opendesign`
- 插件套件：`plugins/print-studio-opendesign`

它用于印刷厂接单打样：导入插画/图片，印刷厂选择产品类型、尺寸、纸张/材质、系列结构，Codex 在规则内生成预览、印刷文件、电商白底图/氛围图、QC 报告和交付包。

## 使用入口

首次上手时，优先打开：

- `user-workflow/user-order-form.zh-CN.md`
- `user-workflow/customization-options.zh-CN.md`
- `user-workflow/conversation-examples.zh-CN.md`
- `user-workflow/user-acceptance-sop.zh-CN.md`

使用者不需要先理解 JSON。先按接单表填写，再让 Codex / Claude Code 生成配置。

## 推荐交付方式

推荐优先使用插件套件，因为它更像一个完整产品：

| Skill | 用途 |
| --- | --- |
| `print-studio-order-intake` | 接单配置 |
| `print-studio-material-selector` | 材质选择预览 |
| `print-studio-layout-proof` | 卡片/书签/吊牌/明信片排版 |
| `print-studio-calendar-series` | 月历/季度/节日套装 |
| `print-studio-commerce-mockup` | 白底图与氛围图 |
| `print-studio-prepress-qc` | 印前质检与交付包 |
| `print-studio-runtime` | 共用渲染引擎 |

## Claude Code 支持

Claude Code 侧不依赖 Codex 插件 manifest，直接安装多个 `SKILL.md`：

```bash
bash claude-code/install.sh
```

安装位置：

`~/.claude/skills/`

## 安装方式

### 方式 A：独立 Skill

将文件夹：

`print-studio-opendesign/`

复制到 Codex skills 目录，例如：

`~/.codex/skills/print-studio-opendesign/`

然后在 Codex 中说：

“使用 print-studio-opendesign，给这组插画做 5×7 台历卡打样。”

### 方式 B：插件套件

将文件夹：

`plugins/print-studio-opendesign/`

作为 Codex Plugin 安装或放入团队插件仓库。插件内的小 Skill 会按任务自动触发。

### 方式 C：Claude Code

运行：

`bash claude-code/install.sh`

然后在 Claude Code 里说：

“使用 print-studio-order-intake，要做 8×12 挂历，顶部线圈装订，先生成配置。”

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

- 预览版：`screen/`
- 印刷交付版：`print/`
- 电商展示版：`commerce/`
- QC 报告：`qc_report.json`
- ZIP 交付包

## V1 范围

已支持：

- 12 个月真实日期日历卡模板
- 8×12 挂历模板，支持顶部线圈、挂孔、夹条装订安全区
- 5×7、5×5、7×5、塔罗牌、书签、Letter 等尺寸预设
- 已内置的 24 种纸张/PVC 材质预设
- 300dpi、出血、安全边距、印刷 guide
- 屏幕预览版 / 印刷版 / 电商展示版分离
- 材质选择预览页

暂不承诺：

- CMYK/ICC 真实色彩管理
- ERP/报价系统集成
- 烫金/UV/压纹的生产级模拟
- 多用户 Web 后台

## 重要说明

材质预览为屏幕模拟，仅用于沟通确认和初步选材；最终颜色、纹理、珠光、PVC 光泽、纸芯侧边效果，以实物纸样和打样为准。
