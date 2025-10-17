# VHS documentation: https://github.com/charmbracelet/vhs

# Settings
Output demo-quickstart.gif
Set FontSize 18
Set Width 1200
Set Height 600
Set Shell bash
Set FontFamily "monospace"

# Demo: クイックスタート（15秒）
Type "# cmw クイックスタートデモ"
Enter
Sleep 1s

Type "cmw init todo-api"
Enter
Sleep 2s

Type "cd todo-api"
Enter
Sleep 500ms

Type "cat shared/docs/requirements.md | head -20"
Enter
Sleep 2s

Type "cmw tasks generate"
Enter
Sleep 3s

Type "cmw tasks list | head -25"
Enter
Sleep 3s

Type "# 17タスクが自動生成されました！"
Enter
Sleep 2s
