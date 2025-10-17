# VHS documentation: https://github.com/charmbracelet/vhs

# Settings
Output demo-graph.gif
Set FontSize 18
Set Width 1200
Set Height 600
Set Shell bash

# Demo: 依存関係グラフ（10秒）
Type "# 依存関係グラフの可視化"
Enter
Sleep 1s

Type "cd todo-api"
Enter
Sleep 500ms

Type "cmw task graph"
Enter
Sleep 4s

Type "cmw task graph --stats"
Enter
Sleep 4s
