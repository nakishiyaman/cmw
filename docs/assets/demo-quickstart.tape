# VHS documentation: https://github.com/charmbracelet/vhs

# Settings
Output demo-quickstart.gif
Set FontSize 16
Set Width 1000
Set Height 600
Set Shell bash

# Demo: クイックスタート
Type "# cmwデモ: requirements.mdから自動タスク生成"
Enter
Sleep 1s

Type "/home/kishiyama-n/workspace/claude-multi-worker-framework/venv/bin/cmw init demo-todo"
Enter
Sleep 2s

Type "cd demo-todo && cat shared/docs/requirements.md"
Enter
Sleep 3s

Type "/home/kishiyama-n/workspace/claude-multi-worker-framework/venv/bin/cmw tasks generate"
Enter
Sleep 3s

Type "/home/kishiyama-n/workspace/claude-multi-worker-framework/venv/bin/cmw tasks list"
Enter
Sleep 3s

Type "# タスクが自動生成されました！"
Enter
Sleep 2s
