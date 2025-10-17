# VHS documentation: https://github.com/charmbracelet/vhs

# Settings
Output demo-dashboard.gif
Set FontSize 16
Set Width 1000
Set Height 700
Set Shell bash

# Demo: 進捗ダッシュボード
Type "# cmwデモ: リアルタイム進捗ダッシュボード"
Enter
Sleep 1s

Type "cd /home/kishiyama-n/workspace/projects/todo-api"
Enter
Sleep 1s

Type "/home/kishiyama-n/workspace/claude-multi-worker-framework/venv/bin/cmw status"
Enter
Sleep 5s
