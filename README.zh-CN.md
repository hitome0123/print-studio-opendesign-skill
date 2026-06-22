# Print Studio OpenDesign：印刷厂 AI 系列设计打样 Skill

> 从客户给图，到选尺寸、选纸张、看材质预览、生成印刷文件与展示图，一个 Codex Skill 完成印刷厂接单打样的第一轮交付。
>
> 它不是单套日历模板，而是一套面向印刷厂销售、设计与打样流程的本地优先 AI 工作流：让销售可以快速出效果，让设计有规则可控，让生产文件和电商展示图分离管理。

---

## 什么是 Print Studio OpenDesign

Print Studio OpenDesign 是一个可安装到 Codex 的印刷品系列设计打样 Skill。它把“客户给一组插画/图片 → 印刷厂选择产品规格 → AI 在规则内排版 → 输出客户预览、印刷文件、白底图、氛围图、QC 报告、交付 ZIP”的流程固化成可重复运行的工作台。

它的定位是：

- **给印刷厂用**：服务日常接单、报价前确认、小批量定制、样稿沟通。
- **给 Codex 调用**：以 `SKILL.md`、脚本、预设、素材和规则的形式交付，安装后 Codex 可直接读取并执行。
- **给设计规则兜底**：AI 可以参与排版判断，但尺寸、出血、安全边距、日期、印刷导出和 QC 必须确定性执行。
- **给客户快速看效果**：先出材质/尺寸预览，再按需生成完整交付包，减少反复沟通。

一句话：

> 客户给图，印刷厂选规格，Codex 在规则内 5–30 分钟出一套可确认的印刷打样包。

---

## 产品速览

### 1 · 配置入口

通过 `config.example.json` 选择本次订单的核心信息：

- 客户与项目：`job.client_name`、`job.job_name`
- 系列结构：12 月日历、季度卡、节日套装、自定义 N 张
- 生产规格：尺寸、纸张、出血、安全边距、产品形态
- 内容规则：年份、真实日期、月份关键词、角落诗句、印章
- 输出类型：客户预览、印刷文件、电商图、白底图、氛围图

### 2 · 材质选择预览

运行：

```bash
python scripts/preview_config.py config.example.json --all-materials
```

生成：

- 当前尺寸版式预览
- 当前材质模拟图
- 印刷 guide 图
- 24 种客户纸张/PVC 材质选择页

材质页会模拟：

- 蓝芯 / 黑芯 / 白芯纸的侧边纸芯色条
- PVC 的塑料高光与磨砂/光面提示
- 珠光纸的轻微反光
- 布纹、蛋壳纹、皱纹等纹理增强
- 每种材质的销售提示，例如“小字谨慎 / 抗透光 / 浅色图需加深”

### 3 · 完整交付包

运行：

```bash
python scripts/run.py config.example.json
```

生成：

- `screen/`：客户预览版
- `print/`：300dpi 印刷版，含出血与裁切 guide
- `commerce/`：电商展示版、白底图、氛围图
- `qc_report.json`：自动质检报告
- `*_交付包.zip`：可交付压缩包

---

## 适用产品线

V1 以“插画日历卡 / 台历卡”为第一个稳定模板，同时按印刷厂业务预留产品线：

| 产品类型 | 当前状态 | 说明 |
| --- | --- | --- |
| 桌历卡 / 月历卡 | ✅ 已实现 | 12 个月真实日期，5×7 默认 |
| 贺卡 | 🟡 预设支持 | 可复用卡片版式，后续补独立模板 |
| 明信片 | 🟡 预设支持 | 支持 7×5 横版尺寸 |
| 挂历 | 🟡 预设支持 | 当前为产品形态预设，后续补装订规则 |
| 卡牌套装 | 🟡 预设支持 | 蓝芯/黑芯/PVC 材质已纳入 |
| 书签 | 🟡 预设支持 | 2×6 长条尺寸已纳入 |
| 感谢卡 / 邀请卡 / 包装插卡 / 吊牌 | 🟡 规划中 | 可作为后续模板扩展 |

---

## 材质系统

客户提供的 24 种材质已经内置为可选项：

- 300g 超白白卡纸
- 300g 牛皮卡纸
- 300g 冰白珠光纸
- 超白 / 雅白细莱妮纹、莱妮纹、彩石纹、雅典纹、皱纹、沙龙纹
- 30 丝 / 32 丝 PVC
- 300g / 350g / 400g 白芯纸
- 280g / 300g 蓝芯纸
- 310g / 330g 黑芯纸

每个材质预设包含：

- `paper_tone`：纸面色调
- `texture_level`：纹理强度
- `detail_retention`：细节保留程度
- `text_depth`：文字深浅建议
- `color_comp`：印刷补偿策略
- `use_case`：适合场景

注意：材质预览是屏幕模拟，不等于实物纸样。最终颜色、纹理、珠光、PVC 光泽、纸芯侧边效果，以纸样和打样为准。

---

## 平台兼容性

Print Studio OpenDesign 以 Codex Skill 形式交付。

| 平台 / Agent | 状态 | 使用方式 |
| --- | --- | --- |
| Codex Desktop / Codex CLI | ✅ 支持 | 复制到 `~/.codex/skills/print-studio-opendesign/` |
| Claude Code | 🟡 可迁移 | 需按 Claude Code Skill 目录规则适配 |
| OpenClaw / 其他本地 Agent | 🟡 可迁移 | 需让 Agent 能读取 `SKILL.md` 并执行 Python 脚本 |
| Web SaaS | ⏳ 未内置 | 可作为二期封装 |

V1 采用本地优先方式：配置、素材、输出都在本机文件系统里，不需要上传到外部服务。只有白底图/氛围图等 AI 生图环节可能调用配置中的图像模型后端。

---

## 快速开始

### 1 · 安装 Skill

将：

```text
print-studio-opendesign/
```

复制到：

```text
~/.codex/skills/print-studio-opendesign/
```

### 2 · 在 Codex 里调用

可以直接说：

```text
使用 print-studio-opendesign，给这组插画做 5×7 台历卡打样，先生成材质预览页。
```

或者：

```text
使用 print-studio-opendesign，把材质改成 300g 蓝芯纸，生成客户预览和印刷文件。
```

### 3 · 命令行快速演示

进入 Skill 目录：

```bash
cd ~/.codex/skills/print-studio-opendesign
```

生成材质预览：

```bash
python scripts/preview_config.py config.example.json --all-materials
```

生成完整交付包：

```bash
python scripts/run.py config.example.json
```

---

## 目录结构

```text
print-studio-opendesign/
├── SKILL.md                         # Codex 读取的 Skill 入口
├── agents/openai.yaml               # UI 元数据
├── config.example.json              # 示例订单配置
├── scripts/
│   ├── preview_config.py            # 快速预览 / 24 材质选择页
│   └── run.py                       # 完整交付入口
├── references/
│   └── operator-guide.md            # 操作与销售说明
└── assets/calendar_series/
    ├── engine/                      # 日历卡模板引擎
    ├── presets.json                 # 尺寸、材质、产品形态、语言、风格预设
    ├── example_illustrations/       # 内置示例插画
    └── references/                  # B/C/D/E 参考图
```

---

## 工作流

```text
客户图像 / 插画素材
        │
        ▼
配置订单 config.example.json
        │
        ├── 先跑 preview_config.py
        │      ├─ 当前尺寸版式预览
        │      ├─ 当前材质模拟
        │      ├─ 印刷 guide
        │      └─ 24 种材质选择页
        │
        ▼
客户确认尺寸 / 材质 / 风格
        │
        ▼
运行 scripts/run.py
        │
        ├─ screen 客户预览版
        ├─ print 印刷交付版
        ├─ commerce 电商展示版
        ├─ qc_report.json
        └─ *_交付包.zip
```

---

## 输出分层

| 输出层 | 用途 | 规则 |
| --- | --- | --- |
| `preview/` | 销售沟通、快速确认 | 不调用 AI，便宜快速 |
| `screen/` | 客户线上确认 | 柔和、轻盈、适合屏幕看 |
| `print/` | 印刷生产交付 | 300dpi、出血、安全区、饱和/对比补偿 |
| `commerce/` | 电商展示图 | 白底图、氛围图、更亮更通透 |
| `qc_report.json` | 交付前检查 | 检查尺寸、边距、日期、输出完整度 |

核心原则：展示图不能反向影响印刷源文件；印刷文件和电商 mockup 必须分离管理。

---

## 设计与印刷规则

- 屏幕图可以轻、灰、淡；印刷图不能太“仙”。
- 印刷会天然变暗、变灰，因此印刷版需要更高饱和与对比。
- 采用“高级饱和”：主体更鲜活，背景和文字仍克制。
- 日期字号不能为了美感过小。
- 细线、印章、手写小字不能低于可印刷识别阈值。
- 插画不能靠边太近，必须保留裁切安全区。
- 粉色、黄色、浅绿色、米白背景需要特别检查发灰风险。
- 黑色文字不建议纯黑，优先深棕、深灰棕，但要清楚。
- 材质未实测标定前，所有补偿均为预估，批量印刷前建议打样。

---

## V1 边界

已完成：

- Codex Skill 标准结构
- 12 个月真实日期日历卡模板
- 24 种材质预设与材质选择页
- 300dpi 印刷输出、出血、安全边距、裁切 guide
- 屏幕版 / 印刷版 / 电商版分离
- QC 报告与 ZIP 交付包
- 干净安装包，无缓存、无输出、无本机绝对路径依赖

暂不承诺：

- CMYK / ICC 真实色彩管理
- ERP / 报价系统 / 生产排期集成
- 烫金、UV、压纹等工艺的生产级模拟
- 多用户 Web 后台
- 所有产品线的独立模板族

---

## 路线图

- **Phase 1：印刷厂打样 Skill**
  - 稳定日历卡 / 卡片系列打样
  - 完善材质预览与销售提示
  - 打包成可安装 Codex Skill

- **Phase 2：更多印刷品模板**
  - 贺卡、明信片、书签、吊牌、包装插卡
  - 季度卡、节气卡、节日套装、自定义 N 张
  - 双面排版、圆角、装订与工艺字段

- **Phase 3：生产级增强**
  - CMYK / ICC 工作流
  - 实物打样标定后的纸张 profile
  - 报价规则、订单字段、批量接单目录
  - Web UI 或内部销售端封装

---

## 交付建议

给印刷厂客户交付时，建议只交付：

- `print-studio-opendesign/` Skill 文件夹
- `README.zh-CN.md`
- `delivery-guide.md`
- 示例配置与示例素材

不要交付：

- 开发过程聊天记录
- 本机绝对路径
- API token / OAuth token
- 临时输出、`.tmp`、`__pycache__`
- 未经客户授权的真实客户素材

---

## 许可证与责任说明

本 Skill 是面向印刷厂内部接单打样的自动化工具。材质、颜色、纹理、光泽、纸芯侧边、印刷补偿均用于屏幕预览和流程辅助；最终生产应以印刷厂实物纸样、设备 profile、打样结果和客户确认稿为准。
