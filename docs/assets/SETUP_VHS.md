# VHS セットアップガイド

## ✅ 完了済み

- [x] VHS本体インストール（v0.10.0）
- [x] 録画スクリプト作成

## ⏳ 残りの手順

### 1. ffmpegをインストール

VHSはGIF生成にffmpegを使用します。以下のコマンドでインストールしてください：

```bash
sudo apt update
sudo apt install -y ffmpeg
```

インストール後、確認：
```bash
ffmpeg -version
```

### 2. 録画スクリプトを実行

```bash
# プロジェクトルートに移動
cd /path/to/claude-multi-worker-framework

# VHSのPATHを設定
export PATH=$PATH:~/go/bin

# docs/assetsディレクトリに移動
cd docs/assets

# 1. クイックスタートデモを録画
vhs demo-quickstart.tape

# 2. グラフデモを録画
vhs demo-graph.tape

# 3. ダッシュボードデモを録画
vhs demo-dashboard.tape
```

### 3. 生成されたGIFを確認

```bash
ls -lh docs/assets/*.gif
```

以下の3ファイルが生成されているはずです：
- `demo-quickstart.gif`
- `demo-graph.gif`
- `demo-dashboard.gif`

### 4. READMEに埋め込む

`docs/assets/README_DEMO_SECTION.md`の内容を、
`README.md`の「インストール」セクションの前（82行目あたり）に挿入してください。

### 5. コミット

```bash
git add docs/assets/*.gif docs/assets/*.tape
git commit -m "docs: デモGIF追加"
```

---

## トラブルシューティング

### ffmpegインストールエラー

パッケージが見つからない場合：
```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:savoury1/ffmpeg4
sudo apt update
sudo apt install -y ffmpeg
```

### VHSが見つからない

PATHを永続化：
```bash
echo 'export PATH=$PATH:~/go/bin' >> ~/.bashrc
source ~/.bashrc
```

### 録画が遅い/重い

`*.tape`ファイルの`Sleep`時間を調整してください。

### GIFが大きすぎる

解像度を下げる：
```tape
Set Width 800
Set Height 500
```

またはMP4形式で録画：
```tape
Output demo.mp4
```
