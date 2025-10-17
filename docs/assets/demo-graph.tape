# VHS documentation: https://github.com/charmbracelet/vhs

# Settings
Output demo-graph.gif
Set FontSize 16
Set Width 1000
Set Height 600
Set Shell bash

# Demo: 依存関係グラフ
Type "# cmwデモ: 依存関係グラフの可視化"
Enter
Sleep 1s

Type "cd /home/kishiyama-n/workspace/projects/todo-api"
Enter
Sleep 1s

Type "/home/kishiyama-n/workspace/claude-multi-worker-framework/venv/bin/cmw task graph"
Enter
Sleep 5s

Type "/home/kishiyama-n/workspace/claude-multi-worker-framework/venv/bin/cmw task graph --stats"
Enter
Sleep 3s
