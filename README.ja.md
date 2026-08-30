<div align="center">

# NPU AI Video

**1枚の画像を、短い動画へ。AとBの間にある「ありえない途中」を作る。**

[![Windows](https://img.shields.io/badge/Windows-11-0078D4?logo=windows11)](https://www.microsoft.com/windows/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenVINO](https://img.shields.io/badge/OpenVINO-2025.4-5C2D91)](https://github.com/openvinotoolkit/openvino)
[![CI](https://github.com/taichiro20100723-droid/npu-motion-studio/actions/workflows/ci.yml/badge.svg)](https://github.com/taichiro20100723-droid/npu-motion-studio/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/code-MIT-4ce3d9)](LICENSE)

[リリースをダウンロード](https://github.com/taichiro20100723-droid/npu-motion-studio/releases) · [English](README.md) · [設計](docs/architecture.md) · [実測](docs/benchmarks.md)

</div>

<p align="center">
  <img src="examples/robot-to-dog/robot-to-dog.gif" width="820" alt="巨大ロボットが柴犬へ変身する実動画">
</p>

> **面白さの入口：** はじめと最後を決めるだけ。NPU AI Videoが、その間の不思議な変化をあなたのIntel PC内で描きます。

一般的な画像→動画AIは、1枚の絵を少し動かすものが中心です。このアプリは、見た人がもう一度再生したくなる変化を作るためのもの。**ロボット→犬、ラフ→完成品、廃墟→都市、文字→異星の記号**を、画像と短い一文から試せます。クラウド送信、アカウント、順番待ち、複雑なノード操作はありません。

## 3ステップで始める

1. [Releases](https://github.com/taichiro20100723-droid/npu-motion-studio/releases)からダウンロード、またはこのリポジトリをCloneします。
2. 初回だけ **`setup_windows.bat`** をダブルクリックします。環境・ローカルモデル・補間ツールを準備します。
3. **`run_windows.bat`** をダブルクリックし、モードを選んで短い動画を作ります。

初回セットアップでは画像モデル約1GB、フレーム補間ツール約230MBを取得します。モデル本体はGitに入りません。アプリは `127.0.0.1` だけで動き、動画は `.runtime/outputs/` に保存されます。

### 必要なもの

- Windows 11
- Python 3.12
- Intel AI Boost NPUを搭載したIntel Core Ultra
- Intel Arcグラフィックスと最新のIntelドライバー
- ランタイム、モデル、キャッシュ用に約3GBの空き容量

モデルなしでUIを試せる `mock` エンジンもあります。別のPCで画面やテストを確認するときに使えます。

## 何を作れる？

| モード | 入力 | 向いているもの |
| --- | --- | --- |
| **A → B 変身** | 画像2枚＋一文 | ビフォーアフター、MVの場面転換、ミーム |
| **画像を動かす** | 画像1枚または文章 | カメラ移動、風、ネオン、ループ、短い投稿 |
| **AI文字ステージ** | 文字または文字シート画像 | タイトル文字、変形グリフ、シェア素材 |
| **Motion Brush** | 画像＋赤/青のブラシ | 主役の動く場所と固定する背景を指定 |

迷ったら、まずこれを試してください。

- **ロボット→柴犬：** 「ロボットが装甲を開きながら、カメラへ走ってくる柴犬に変身する」
- **ネオンの夜：** 「雨の夜のネオン街。カメラが横へ流れ、光がきらめく」
- **文字→異星の記号：** 「文字が光の粒になり、異星の記号へ再構成される」

画面のカードを押すと、モードと文章が自動で入ります。動画はMP4で保存でき、AI文字ステージでは文字シートSVGもダウンロードできます。

## 速さとローカル実行

Intelチップ全体に役割を分けています。

```text
日本語 / Englishの一文
          │
          ▼
CPU：ローカル翻訳＋動きのタイムライン
          │
          ▼
NPU：文章に合わせた途中画像
          │
          ▼
Arc GPU：画像化＋フレーム補間
          │
          ▼
Intel Quick Sync：H.264 MP4
```

フル動画拡散モデルだとは説明していません。始点と終点を守り、途中の要所をNPUで描き、動きのワープと補間を組み合わせる、意図的に軽いハイブリッド方式です。大きく違うものへの変身では途中がシュールになることがあります。それも隠さず楽しむための設計です。

## 実動画と実測

リポジトリにはテストPCで作った実出力を含めています。

![ロボットから犬への変化](examples/robot-to-dog/robot-to-dog-contact-sheet.png)

[ロボット→犬のMP4](examples/robot-to-dog/robot-to-dog.mp4) · [Motion BrushのMP4](examples/motion-brush/robot-to-dog-motion-brush.mp4) · [1枚画像のループ](examples/showcase/one-image-loop.gif)

Core Ultra 7 258V / Intel AI Boost NPU / Arc 140V / OpenVINO 2025.4.1での実測です。

| 内容 | NPU | Arc GPU | 合計 |
| --- | ---: | ---: | ---: |
| 1枚、すぐ試す、3秒 / 47コマ | 3.13秒 | 1.27秒 | **5.80秒** |
| A→B、8枚、4秒 / 96コマ | 7.94秒 | 1.97秒 | **11.61秒** |
| ロボット→犬、12枚、5秒 / 120コマ | 15.25秒 | 3.99秒 | **20.69秒** |

1台のウォーム状態での実測で、すべてのPC・入力への保証値ではありません。NPUの初回コンパイルは数分かかることがあります。

## 開発者向け

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[production,dev]"
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest -q
node --check src/npu_motion_studio/web/app.js
```

モデルなしで起動するには：

```powershell
.\.venv\Scripts\python.exe -m npu_motion_studio
```

主な画面は `src/npu_motion_studio/web/`、APIはローカル専用です。変更を送る前に [CONTRIBUTING.md](CONTRIBUTING.md) を確認してください。

## 文化祭MV（実験モード）

`make_waseda_saga_festival_mv.bat` は、音量の山に合わせてカットとトランジションを作るローカル用レシピです。初期設定では顔のない背景を使います。公開する動画では、写真・曲・ロゴ・学校素材ごとに許可と利用条件を確認してください。

## 正直な限界とライセンス

AI画像間で顔、手、服、車体の細部が変わることがあります。複数人のやりとりや、道具を正確に持ち替える動作もまだ苦手です。結果は文章、画像、温度、ドライバー、モデルのバージョンで変わります。

アプリのコードはMIT Licenseです。OpenVINO、モデル、FFmpeg、RIFEにはそれぞれ別のライセンスがあります。再配布や商用利用の前に [MODEL_MANIFEST.json](MODEL_MANIFEST.json) を確認してください。

新しいIntel NPUの実測、利用条件を確認したサンプル、動きのアイデア、小さなバグ修正を歓迎します。
