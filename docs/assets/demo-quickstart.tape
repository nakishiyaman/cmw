# VHS documentation: https://github.com/charmbracelet/vhs

# Settings
Output demo-quickstart.gif
Set FontSize 18
Set Width 1200
Set Height 600
Set Shell bash
Set FontFamily "monospace"

# Demo: クイックスタート
Hide
Type "export PS1='$ '"
Enter
Sleep 100ms
Show
Type "# cmw クイックスタートデモ"
Enter
Sleep 1s

Type "cmw init --name todo-api"
Enter
Sleep 2s

Type "cd todo-api"
Enter
Sleep 500ms

# requirements.mdを編集済みのものに置き換え（非表示）
Hide
Type "cp /tmp/sample-requirements.md shared/docs/requirements.md"
Enter
Sleep 500ms
Show

Type "# requirements.mdを編集しました"
Enter
Sleep 500ms

Type "cat shared/docs/requirements.md | head -20"
Enter
Sleep 3s

Type "cmw task generate"
Enter
Sleep 4s

Type "cmw task list | head -25"
Enter
Sleep 4s

Type "# 17タスクが自動生成されました！"
Enter
Sleep 2s
