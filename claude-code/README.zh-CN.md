# Claude Code 支持

Print Studio OpenDesign 同时支持 Codex 和 Claude Code。

## 安装到 Claude Code

在仓库根目录运行：

```bash
bash claude-code/install.sh
```

脚本会把插件内的小 Skill 复制到：

```text
~/.claude/skills/
```

安装后 Claude Code 可以按任务触发这些 Skill：

- `print-studio-order-intake`
- `print-studio-material-selector`
- `print-studio-layout-proof`
- `print-studio-calendar-series`
- `print-studio-commerce-mockup`
- `print-studio-prepress-qc`
- `print-studio-runtime`

## 使用示例

```text
使用 print-studio-order-intake，客户要做 8×12 挂历，300g 白卡纸，顶部线圈装订，先生成配置。
```

```text
使用 print-studio-calendar-series，根据 wall-calendar 示例生成客户预览和印刷文件。
```

## 注意

- Claude Code 使用 `SKILL.md` 作为技能入口，不读取 Codex 的 `.codex-plugin/plugin.json`。
- 所以 Claude Code 侧安装的是 `plugins/print-studio-opendesign/skills/` 下的多个 Skill。
- 复杂渲染脚本、预设和示例集中在 `print-studio-runtime`，其他小 Skill 负责引导任务。

