# Print Studio OpenDesign Plugin

> 一个面向印刷厂接单打样的 Codex 插件套件：把大工作流拆成多个小 Skill，让 Codex 可以按任务自动调用，而不是每次加载一个巨型 Skill。

## 交付形态

```text
plugins/print-studio-opendesign/
├── .codex-plugin/plugin.json
└── skills/
    ├── print-studio-order-intake/
    ├── print-studio-material-selector/
    ├── print-studio-layout-proof/
    ├── print-studio-calendar-series/
    ├── print-studio-commerce-mockup/
    ├── print-studio-prepress-qc/
    └── print-studio-runtime/
```

## Skill 拆分

| Skill | 负责什么 | 典型触发 |
| --- | --- | --- |
| `print-studio-order-intake` | 接单信息、产品类型、尺寸、材质、工艺字段 | “要做贺卡，帮我整理配置” |
| `print-studio-material-selector` | 24 种纸张/PVC 材质选择页、选择提示 | “生成材质预览用于选择” |
| `print-studio-layout-proof` | AI 规则内排版打样，支持贺卡/明信片/书签/吊牌等 | “用这组图做 5×7 卡片打样” |
| `print-studio-calendar-series` | 月历/季度/节气/节日套装 | “做 12 个月日历卡” |
| `print-studio-commerce-mockup` | 白底图、氛围图、电商展示图 | “再出白底图和氛围图” |
| `print-studio-prepress-qc` | 出血、安全边距、字号、对比、交付 ZIP | “检查能不能给印刷厂生产” |
| `print-studio-runtime` | 共用渲染引擎和脚本 | 其他 Skill 调用，不建议用户直接点 |

## 推荐使用方式

先让 Codex 走 `print-studio-order-intake` 建配置，再按需要进入材质、排版、展示、质检。

如果第一次使用，先读仓库根目录：

- `user-workflow/user-order-form.zh-CN.md`
- `user-workflow/customization-options.zh-CN.md`
- `user-workflow/conversation-examples.zh-CN.md`
- `user-workflow/user-acceptance-sop.zh-CN.md`

示例：

```text
使用 Print Studio OpenDesign，要做 5×7 贺卡，白色 300g 硬卡纸，先整理订单配置并生成材质预览。
```

```text
使用 Print Studio OpenDesign，把这组插画做成 12 个月月历卡，输出预览、印刷文件、白底图和氛围图。
```

```text
使用 Print Studio OpenDesign，做 8×12 挂历，顶部线圈装订，预留装订安全区。
```

## Claude Code

Claude Code 可直接使用本插件的 `skills/` 目录。仓库根目录提供安装脚本：

```bash
bash claude-code/install.sh
```

## 设计原则

- 插件负责“产品化入口”，小 Skill 负责“单一任务”。
- AI 可以参与审美判断，但尺寸、出血、安全区、日期、导出和 QC 走确定性脚本。
- 屏幕预览、印刷源文件、电商展示图分开管理，避免互相污染。
- 材质预览只用于沟通选择，最终批量印刷仍以纸样和打样为准。
