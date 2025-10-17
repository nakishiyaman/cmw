# VHS documentation: https://github.com/charmbracelet/vhs

# Settings
Output demo-quickstart.gif
Set FontSize 18
Set Width 1200
Set Height 600
Set Shell bash
Set FontFamily "DejaVu Sans Mono, Noto Color Emoji"

# Demo: 新しいクイックスタート - Claude Code統合
Hide
Type "export LANG=C.UTF-8"
Enter
Type "export LC_ALL=C.UTF-8"
Enter
Type "export PS1='$ '"
Enter
Type "export PATH=$PATH:~/go/bin"
Enter
Type "cd /tmp && rm -rf cmw-demo && mkdir cmw-demo && cd cmw-demo"
Enter
Type "source /home/kishiyama-n/workspace/cmw/venv/bin/activate"
Enter
Sleep 100ms
Show

Type "# cmw Quickstart - Claude Code Integration"
Enter
Sleep 1s

Type "cmw init --name demo-blog-api"
Enter
Sleep 2s

Type "cd demo-blog-api"
Enter
Sleep 500ms

Type "# Generate requirements with one command"
Enter
Sleep 500ms

Type "cmw requirements generate --with-claude --prompt 'Blog API'"
Enter
Sleep 3s

Type "# .cmw_prompt.md generated!"
Enter
Sleep 1s

Type "ls -la .cmw_prompt.md"
Enter
Sleep 2s

Type "# Pass to Claude Code -> requirements.md created"
Enter
Sleep 1s

# 事前準備したファイルをコピー
Hide
Type "cp /home/kishiyama-n/workspace/cmw/docs/assets/sample-requirements.md shared/docs/requirements.md 2>/dev/null || echo '# Blog API' > shared/docs/requirements.md"
Enter
Sleep 500ms
Show

Type "cat shared/docs/requirements.md | head -15"
Enter
Sleep 3s

Type "# Auto-generate tasks"
Enter
Sleep 500ms

Type "cmw task generate"
Enter
Sleep 3s

Type "cmw task list | head -15"
Enter
Sleep 4s

Type "# Tasks ready! Start coding with Claude Code"
Enter
Sleep 2s
