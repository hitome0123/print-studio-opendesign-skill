# Print Studio OpenDesign · Plugin Delivery TODO

- [x] 明确目标：在独立 Skill 之外，补一个 Codex Plugin 交付形态。
- [x] 参考 OpenDesign 式产品文档，把插件说明讲成“印刷厂 AI 打样工作台”。
- [x] 创建 `.codex-plugin/plugin.json` 与内置多个小 Skill。
- [x] 验证插件 manifest、内置 Skill、示例配置运行。
- [ ] 推送到 GitHub，作为可安装使用包。

## Review

- 已把原先“大 Skill”补充为 `plugins/print-studio-opendesign/` 插件套件。
- 插件内拆出 6 个面向业务动作的小 Skill，并保留 `print-studio-runtime` 作为共用渲染引擎。
- 已通过插件 manifest 校验、7 个 Skill 校验、材质预览和吊牌示例运行。
- 2026-06-23：追加 Claude Code 安装脚本与挂历顶部装订安全区。
- 2026-06-23：gstack 交付体检评分 8.0/10，结论为 Beta 可交付，生产级仍需补 SOP/PDF/ICC 边界。
- 2026-06-23：补使用配置表、可自定义项清单、对话示例和验收 SOP，用于模拟真实使用者上手。
- 2026-06-23：补 `SKILL_OVERVIEW.zh-CN.md`，用于先把 Skill 的定位、功能、输出、配置和 V1 边界讲清楚。
- 2026-06-27：新增 A/B/C 版式候选、`layout_lock` 锁版配置和批量渲染验证；小兔子案例已跑通“选 B → 12 张稳定输出”。
- 2026-06-28：补交互式项目向导、A/B/C 候选 HTML 选择页、交付包首页 `交付说明.html`，小兔子案例已验证 ZIP 内含候选页、4K 下载页和印前报告。
- 2026-06-28：新增 `layout_ai` API 版式顾问层，支持 auto/openai/gemini/local；API 只输出受限 JSON 建议，候选 A 使用 API/规则推荐种子，最终仍由本地渲染器锁版输出。
- 2026-06-28：新增 `run_project_flow.py` 一键引导流程，从图片文件夹自动跑图片建议、材质预览、版式候选、锁版和完整交付包；交付首页/ZIP 已包含材质预览和图片建议报告。
