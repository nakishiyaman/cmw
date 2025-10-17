# VHS documentation: https://github.com/charmbracelet/vhs

# Settings
Output demo-dashboard.gif
Set FontSize 18
Set Width 1200
Set Height 800
Set Shell bash
Set FontFamily "monospace"

# Demo: 進捗ダッシュボード（5秒）
Hide
Type "export LANG=ja_JP.UTF-8"
Enter
Type "export LC_ALL=ja_JP.UTF-8"
Enter
Type "export PS1='$ '"
Enter
Sleep 100ms
Show
Type "# 進捗ダッシュボード"
Enter
Sleep 1s

Type "cmw status"
Enter
Sleep 5s
