# VHS documentation: https://github.com/charmbracelet/vhs

# Settings
Output demo-graph.gif
Set FontSize 18
Set Width 1200
Set Height 600
Set Shell bash
Set FontFamily "DejaVu Sans Mono, Noto Color Emoji"

# Demo: 依存関係グラフ（10秒）
Hide
Type "export LANG=C.UTF-8"
Enter
Type "export LC_ALL=C.UTF-8"
Enter
Type "export PS1='$ '"
Enter
Sleep 100ms
Show
Type "# 依存関係グラフの可視化"
Enter
Sleep 1s

Type "cmw task graph | head -30"
Enter
Sleep 4s

Type "cmw task graph --stats"
Enter
Sleep 4s
