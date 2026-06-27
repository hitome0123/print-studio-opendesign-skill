# Print Studio OpenDesign：印刷厂 AI 系列设计打样 Skill

> 从导入图像，到选尺寸、选纸张、看材质预览、生成印刷文件与展示图，一个 Codex Skill 完成印刷厂接单打样的第一轮交付。
>
> 它不是单套日历模板，而是一套面向印刷厂使用者、设计与打样流程的本地优先 AI 工作流：让使用者可以快速出效果，让设计有规则可控，让生产文件和电商展示图分离管理。

---

## 什么是 Print Studio OpenDesign

Print Studio OpenDesign 是一个可安装到 Codex 的印刷品系列设计打样 Skill。它把“导入一组插画/图片 → 选择产品规格 → AI 在规则内排版 → 输出预览、印刷文件、白底图、氛围图、系列总览、4K 单张下载图、三模型预览、QC 报告、交付 ZIP”的流程固化成可重复运行的工作台。

它的定位是：

- **给印刷生产场景用**：服务日常接单、报价前确认、小批量定制、样稿沟通。
- **给 Codex 调用**：以 `SKILL.md`、脚本、预设、素材和规则的形式交付，安装后 Codex 可直接读取并执行。
- **给设计规则兜底**：AI 可以参与排版判断，但尺寸、出血、安全边距、日期、印刷导出和 QC 必须确定性执行。
- **快速查看效果**：先出材质/尺寸预览，再按需生成完整交付包，减少反复沟通。

一句话：

> 导入图像，印刷厂选规格，Codex 在规则内 5–30 分钟出一套可确认的印刷打样包。

---

## 使用者怎么用

如果使用者不想看 JSON，先看这 4 份操作文档：

| 文档 | 用途 |
| --- | --- |
| `PRINT_STUDIO_SHOWCASE.zh-CN.html` | 可直接打开的产品展示页，按案例讲清工作流、功能设计、参考方法和交付产物 |
| `plugins/print-studio-opendesign/skills/print-studio-runtime/demo/xiaotuzi_skill_showcase.html` | 小兔子文具真实案例展示页，展示图片理解、推荐逻辑、材质预览、完整排版、白底图、氛围图、参考方法和各子 Skill 用法 |
| `SKILL_OVERVIEW.zh-CN.md` | Skill 完整说明，先把定位、功能、输出和边界讲清楚 |
| `user-workflow/model-prompt-pack.zh-CN.md` | 给 Gemini、OpenAI GPT Image、GPT-Image2、即梦客户端使用的白底图/氛围图提示词包 |
| `user-workflow/user-order-form.zh-CN.md` | 使用配置表，接单人员照填 |
| `user-workflow/customization-options.zh-CN.md` | 可自定义项清单，说明哪些能改、哪些不建议乱改 |
| `user-workflow/conversation-examples.zh-CN.md` | Codex / Claude Code 对话示例 |
| `user-workflow/user-acceptance-sop.zh-CN.md` | 使用验收 SOP，30 分钟跑通示例 |

推荐使用流程：

1. 先提供图片文件夹。
2. 运行图片优先建议器，先从图片本身判断产品、尺寸、材质、排版和字体方向。
3. 再按建议选择产品规格，不要求一开始就把需求说完整。
4. 先生成材质选择页和版式预览。
5. 再生成预览、印刷文件、白底图、氛围图、4K 单张下载图。
6. 用 QC 报告判断是否能交付。

图片优先建议器：

```bash
python scripts/advise_project.py <图片文件夹>
```

它会输出一份 `print_studio_advice.md`，里面包含带理由的产品、尺寸、材质、排版、字体、模型预览和印刷检查建议。

---

## 产品速览

### 1 · 配置入口

通过 `config.example.json` 选择本次订单的核心信息：

- 项目方与项目：`job.client_name`、`job.job_name`
- 系列结构：12 月日历、季度卡、节日套装、自定义 N 张
- 生产规格：尺寸、纸张、出血、安全边距、产品形态
- 内容规则：年份、真实日期、月份关键词、角落诗句、印章
- 输出类型：预览、印刷文件、电商图、白底图、氛围图、系列总览、4K 单张下载图、三模型预览图

### 2 · 材质选择预览

运行：

```bash
python scripts/preview_config.py config.example.json --all-materials
```

生成：

- 当前尺寸版式预览
- 当前材质模拟图
- 印刷 guide 图
- 24 种纸张/PVC 材质选择页

材质页会模拟：

- 蓝芯 / 黑芯 / 白芯纸的侧边纸芯色条
- PVC 的塑料高光与磨砂/光面提示
- 珠光纸的轻微反光
- 布纹、蛋壳纹、皱纹等纹理增强
- 每种材质的选择提示，例如“小字谨慎 / 抗透光 / 浅色图需加深”

### 3 · 完整交付包

运行：

```bash
python scripts/run.py config.example.json
```

生成：

- `screen/`：预览版
- `print/`：300dpi 印刷版，含出血与裁切 guide
- `commerce/`：电商展示版、白底图、氛围图、系列总览图
- `download_4k/`：每张图单独保存的 4K 长边下载版，含 `index.html` 下载页
- `provider_previews/`：首轮可选的即梦 / Gemini / GPT-Image2 白底图与氛围图对比
- `design_plan.json`：多层设计计划，记录图片层、文字层、背景层、材质层、印刷安全层和 preset 选择理由
- `qc_report.json`：自动质检报告
- `prepress_report.zh-CN.md`：中文印前说明，解释为什么可进入下一步、哪些地方需人工确认
- `reports/`：随 ZIP 打包的报告文件
- `*_交付包.zip`：可交付压缩包

---

## 适用产品线

V1 以“插画日历卡 / 台历卡”为第一个稳定模板，同时按印刷厂业务预留产品线：

| 产品类型 | 当前状态 | 说明 |
| --- | --- | --- |
| 桌历卡 / 月历卡 | ✅ 已实现 | 12 个月真实日期，5×7 默认 |
| 贺卡 | ✅ 已实现 | `generic_card` 通用卡片模板，支持 5×7 / 4×6 |
| 明信片 | ✅ 已实现 | 7×5 横版，支持自定义套装张数 |
| 挂历 | ✅ 已实现 | `wall_calendar` 模板，支持顶部线圈/挂孔/夹条装订安全区 |
| 卡牌套装 | ✅ 已实现 | 通用卡片模板 + 蓝芯/黑芯/PVC 材质 |
| 书签 | ✅ 已实现 | 2×6 长条模板，支持系列套装 |
| 感谢卡 / 邀请卡 / 包装插卡 / 吊牌 | ✅ 已实现 | 通用卡片模板，吊牌支持打孔提示 |


### 可选模板示例

仓库内置了多个可直接复制修改的配置：

- `print-studio-opendesign/examples/greeting-card-5x7.json`：贺卡
- `print-studio-opendesign/examples/postcard-7x5-set.json`：明信片套装
- `print-studio-opendesign/examples/bookmark-2x6-set.json`：书签套装
- `print-studio-opendesign/examples/gift-tag-custom.json`：礼品吊牌
- `print-studio-opendesign/examples/wall-calendar-8x12.json`：8×12 挂历

贺卡、明信片、书签、吊牌示例走 `generic_card` 模板，支持 `series.count` 自定义张数。
挂历示例走 `calendar_series` 模板，并会在顶部预留装订区。

---

## 材质系统

系统内置 24 种材质可选：

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

Print Studio OpenDesign 支持两种交付形态：独立 Skill，以及更接近 OpenDesign 模式的“单插件 + 多 Skill”套件。

| 平台 / Agent | 状态 | 使用方式 |
| --- | --- | --- |
| Codex Desktop / Codex CLI | ✅ 支持 | 复制到 `~/.codex/skills/print-studio-opendesign/` |
| Codex Plugin | ✅ 支持 | 使用 `plugins/print-studio-opendesign/`，插件内含多个小 Skill |
| Claude Code | ✅ 支持 | 运行 `bash claude-code/install.sh`，复制小 Skill 到 `~/.claude/skills/` |
| OpenClaw / 其他本地 Agent | 🟡 可迁移 | 需让 Agent 能读取 `SKILL.md` 并执行 Python 脚本 |
| Web SaaS | ⏳ 未内置 | 可作为二期封装 |

V1 采用本地优先方式：配置、素材、输出都在本机文件系统里，不需要上传到外部服务。只有白底图/氛围图等 AI 生图环节可能调用配置中的图像模型后端。

---

## Plugin 套件模式

如果按 OpenDesign 式产品交付，推荐使用插件目录：

```text
plugins/print-studio-opendesign/
├── .codex-plugin/plugin.json
└── skills/
    ├── print-studio-order-intake        # 接单配置
    ├── print-studio-material-selector   # 材质选择预览
    ├── print-studio-layout-proof        # 卡片/书签/吊牌排版
    ├── print-studio-calendar-series     # 月历/季度/节日套装
    ├── print-studio-commerce-mockup     # 白底图/氛围图
    ├── print-studio-prepress-qc         # 印前质检/交付包
    └── print-studio-runtime             # 共用渲染引擎
```

这个结构的好处是：

- **入口清楚**：使用者看到的是一个插件，不是一堆散文件。
- **能力可组合**：Codex 可以按任务触发单个 Skill，例如只做材质预览或只做印前检查。
- **上下文更轻**：小 Skill 只加载当前步骤需要的规则，复杂脚本放在 runtime。
- **后续好扩展**：新增贴纸、包装盒、折页、名片等产品线时，只加新 Skill，不推翻整体。

---

## Claude Code 模式

Claude Code 不读取 Codex 的 `.codex-plugin/plugin.json`，但可以直接读取 `SKILL.md`。因此仓库提供了专门的安装脚本：

```bash
bash claude-code/install.sh
```

脚本会把：

```text
plugins/print-studio-opendesign/skills/*
```

复制到：

```text
~/.claude/skills/
```

安装后 Claude Code 可以按任务触发 `print-studio-order-intake`、`print-studio-material-selector`、`print-studio-layout-proof`、`print-studio-calendar-series`、`print-studio-commerce-mockup`、`print-studio-prepress-qc` 和 `print-studio-runtime`。

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
使用 print-studio-opendesign，把材质改成 300g 蓝芯纸，生成预览和印刷文件。
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
│   └── operator-guide.md            # 操作与使用说明
└── assets/calendar_series/
    ├── engine/                      # 日历卡模板引擎
    ├── presets.json                 # 尺寸、材质、产品形态、语言、风格预设
    ├── example_illustrations/       # 内置示例插画
    └── references/                  # B/C/D/E 参考图
```

---

## 工作流

```text
图像 / 插画素材
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
确认尺寸 / 材质 / 风格
        │
        ▼
运行 scripts/run.py
        │
        ├─ screen 预览版
        ├─ print 印刷交付版
        ├─ commerce 电商展示版
        ├─ download_4k 单张 4K 下载页
        ├─ provider_previews 三模型首轮预览
        ├─ design_plan.json 多层设计计划
        ├─ qc_report.json / prepress_report.zh-CN.md
        ├─ reports 报告打包目录
        └─ *_交付包.zip
```

---

## 输出分层

| 输出层 | 用途 | 规则 |
| --- | --- | --- |
| `preview/` | 沟通确认、快速确认 | 不调用 AI，便宜快速 |
| `screen/` | 线上确认 | 柔和、轻盈、适合屏幕看 |
| `print/` | 印刷生产交付 | 300dpi、出血、安全区、饱和/对比补偿 |
| `commerce/` | 电商展示图 | 白底图、氛围图、系列总览，更亮更通透 |
| `download_4k/` | 单张保存下载 | 4K 长边 JPG，适合逐张保存、发图确认、归档 |
| `provider_previews/` | 首轮模型比较 | 即梦 / Gemini / GPT-Image2 对比白底图与氛围图，方便选定后续模型 |
| `design_plan.json` | 设计计划 | 记录版式、字体、色彩 preset 与图层结构，方便复核和修改 |
| `qc_report.json` | 交付前检查 | 检查尺寸、边距、日期、输出完整度 |
| `prepress_report.zh-CN.md` | 印前说明 | 中文解释可印原因、风险与人工确认点 |
| `reports/` | 报告打包 | 把配置、设计计划、QC、印前说明放入 ZIP |

核心原则：展示图不能反向影响印刷源文件；印刷文件和电商 mockup 必须分离管理。

### 排版防改图原则

客户反馈的“把提示词喂给 ChatGPT 后出现自动裁切/改图”是合理风险。因此 V1 默认策略已经明确为：

- **最终排版不用生图模型生成**：`screen/`、`print/`、`design_plan.json` 必须来自确定性渲染器。
- **生图模型只做展示图变体**：白底图、氛围图可以用 AI，但不能作为印刷源文件。
- **默认展示图使用 `local_mockup`**：本地确定性 mockup 保证整张卡片完整可见，不裁切、不改文字、不重排。
- **AI mockup 只作为可选高级模式**：需要比较即梦 / Gemini / GPT-Image2 时再开启，并且如果出现裁切、改字、重构图，必须丢弃。
- **交付时以 `print/` 为准**：任何白底图、氛围图、4K 展示图都不能替代 `print/` 目录里的 300dpi 印刷文件。


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
- 白底图、氛围图、系列总览图与逐张 4K 下载页
- 即梦 / Gemini / GPT-Image2 首轮预览对比配置
- 字体 / 版式 / 色彩 preset 库
- `design_plan.json` 多层设计计划
- `prepress_report.zh-CN.md` 中文印前说明
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
  - 完善材质预览与选择提示
  - 打包成可安装 Codex Skill

- **Phase 2：更多印刷品模板**
  - 更多专用版式族：贺卡内页、明信片背面邮编区、更多挂历装订细节
  - 节气卡、节日套装的专属标题/日期规则
  - 双面排版、圆角、装订与工艺字段的生产级导出

- **Phase 3：生产级增强**
  - CMYK / ICC 工作流
  - 实物打样标定后的纸张 profile
  - 报价规则、订单字段、批量接单目录
  - Web UI 或内部使用端封装

---

## 交付建议

对外提供使用包时，建议只交付：

- `print-studio-opendesign/` Skill 文件夹
- `README.zh-CN.md`
- `delivery-guide.md`
- 示例配置与示例素材

不要交付：

- 开发过程聊天记录
- 本机绝对路径
- API token / OAuth token
- 临时输出、`.tmp`、`__pycache__`
- 未经授权的真实项目素材

---

## 许可证与责任说明

本 Skill 是面向印刷厂内部接单打样的自动化工具。材质、颜色、纹理、光泽、纸芯侧边、印刷补偿均用于屏幕预览和流程辅助；最终生产应以印刷厂实物纸样、设备 profile、打样结果和确认稿为准。
