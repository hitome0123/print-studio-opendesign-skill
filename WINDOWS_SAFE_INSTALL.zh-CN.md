# Windows 安全安装说明

> 如果 Windows / PowerShell 弹出 `Invoke-WebRequest` 安全提醒，不代表这个 Skill 本身有病毒。它通常是 PowerShell 5.1 下载网页时的通用脚本解析提醒。

---

## 1. 看到这个弹窗怎么办

如果出现类似提示：

```text
Invoke-WebRequest 分析页面时可能会运行网页中的脚本代码，存在安全风险。
建议使用 "-UseBasicParsing" 开关来避免脚本代码执行。
是否继续执行？
```

建议选择：

```text
否
```

然后改用下面任意一种安装方式。

---

## 2. 推荐方式 A：浏览器下载 ZIP

这是给非技术使用者最稳妥的方式。

1. 打开 GitHub 仓库：

   ```text
   https://github.com/hitome0123/print-studio-opendesign-skill
   ```

2. 点击绿色按钮：

   ```text
   Code → Download ZIP
   ```

3. 解压 ZIP。

4. 把解压后的 Skill 文件夹交给 Codex / Claude Code 使用。

这种方式不会触发 `Invoke-WebRequest` 弹窗。

---

## 3. 推荐方式 B：用 Git 克隆

如果电脑装了 Git，推荐使用：

```bash
git clone https://github.com/hitome0123/print-studio-opendesign-skill.git
```

然后进入目录：

```bash
cd print-studio-opendesign-skill
```

这种方式也不会触发 PowerShell 的网页脚本解析提示。

---

## 4. 备选方式 C：必须用 PowerShell 下载时

如果必须在 Windows PowerShell 里下载 ZIP，请使用 `-UseBasicParsing`：

```powershell
$url = "https://github.com/hitome0123/print-studio-opendesign-skill/archive/refs/heads/main.zip"
$zip = "$env:TEMP\print-studio-opendesign-skill.zip"
Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $zip
Expand-Archive -Path $zip -DestinationPath "$env:USERPROFILE\Downloads" -Force
```

注意：

- 不建议复制来路不明的一键安装命令。
- 如果系统弹安全提示，看清来源；不确定就选“否”。
- 本仓库的运行方式是本地文件和 Python 脚本，不需要通过网页脚本执行安装。

---

## 5. 安装到 Codex

解压或克隆后，把这个文件夹复制到 Codex skills 目录：

```text
print-studio-opendesign/
```

复制到：

```text
~/.codex/skills/print-studio-opendesign/
```

然后在 Codex 里说：

```text
使用 print-studio-opendesign。
我给你一组图片，请先推荐产品、尺寸、材质和版式。
```

---

## 6. 安装到 Claude Code

在仓库根目录运行：

```bash
bash claude-code/install.sh
```

如果是在 Windows 上使用 Claude Code，建议优先在 Git Bash、WSL 或 macOS/Linux 环境运行这个命令。

---

## 7. 给客户的一句话解释

可以这样解释：

> 这个弹窗是 Windows PowerShell 下载网页时的通用安全提醒，不是项目文件报毒。为了避免误会，建议不要点“是”，改用 GitHub 页面里的 `Code → Download ZIP` 下载，或用 `git clone` 安装。
