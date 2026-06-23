# Print Studio OpenDesign · Plugin Delivery TODO

- [x] 明确目标：在独立 Skill 之外，补一个 Codex Plugin 交付形态。
- [x] 参考 OpenDesign 式产品文档，把插件说明讲成“印刷厂 AI 打样工作台”。
- [x] 创建 `.codex-plugin/plugin.json` 与内置多个小 Skill。
- [x] 验证插件 manifest、内置 Skill、示例配置运行。
- [ ] 推送到 GitHub，作为客户可安装交付包。

## Review

- 已把原先“大 Skill”补充为 `plugins/print-studio-opendesign/` 插件套件。
- 插件内拆出 6 个面向业务动作的小 Skill，并保留 `print-studio-runtime` 作为共用渲染引擎。
- 已通过插件 manifest 校验、7 个 Skill 校验、材质预览和吊牌示例运行。
- 2026-06-23：追加 Claude Code 安装脚本与挂历顶部装订安全区。
