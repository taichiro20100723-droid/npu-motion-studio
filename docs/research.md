# 技術調査と設計判断

## 採用

- [OpenVINO GenAI](https://github.com/openvinotoolkit/openvino.genai): 画像生成、NPU runtime、
  CPU text encoder / NPU UNet / GPU VAEのheterogeneous構成を公式サンプルが提供。
- [Latent Consistency Models](https://arxiv.org/abs/2310.04378): 2〜4 stepsの少数反復生成。
- [OpenVINO LCM Dreamshaper v7 INT8](https://huggingface.co/OpenVINO/LCM_Dreamshaper_v7-int8-ov):
  512角のOpenVINO IR。モデルカード上はMIT。
- [OpenCV DIS Optical Flow](https://docs.opencv.org/4.x/de/d4f/classcv_1_1DISOpticalFlow.html):
  Arc GPU補間に失敗した場合のCPU fallback。
- [rife-ncnn-vulkan](https://github.com/nihui/rife-ncnn-vulkan): RIFE v4.6をIntel Arc 140Vの
  Vulkanで実行。任意フレーム数とループ終端の補間に使用。
- [Helsinki OPUS-MT ja-en](https://huggingface.co/Helsinki-NLP/opus-mt-ja-en): 日本語promptを
  ローカルで英訳。既知の動作語は規則ベース英語も併記し、誤訳を補う。

## 今回の新しい組み合わせ

FlowCache Motion V2は、一つの新規学習済みモデルではなく、次を組み合わせる
アプリケーションアルゴリズムです。

- 前画像を変形して次のimg2img条件へ再利用
- 動作別の時系列promptで4・8・12枚のNPUアンカーを生成
- 低〜中strengthと同じseedで全体のidentityと色を保持
- RIFE v4.6でアンカー間をArc GPU補間
- ループ時は最初のアンカーを終端へ追加し、補間後の重複1フレームを外す
- 180秒の安全上限へ近づいた異常時だけ追加アンカーを中止

単純な2.5Dは風景fallbackとして残せますが、標準生成はNPUが複数時点を再描画します。

## 将来の品質モード

- masked inpaint: 新しく見えた領域や手足周辺だけ再生成
- ControlNet pose/depth: 人物の骨格やカメラ奥行きを明示
- 音声・ビート解析: ダンスのポーズ位相を音へ同期
- AnimateLCM: 本物の時間モデルを使う別モード。ただし258V NPUでの変換と速度を要検証
- identity embedding: 人物や製品の同一性保持

## 今回は標準にしないもの

- LTX-Video / AnimateDiff / SVDの全動画拡散: 品質は高いが、NPUとArc 140Vでの実装・
  モデル容量・待ち時間が別製品級になるため、V2標準にはしない。
- FLUX: この32GB共有メモリ環境で多数のアンカーを連続生成するにはモデルが大きい。
- 独立したAI画像を大量生成してcross-fade: 同一性が崩れ、補間の破綻が増える。
- Depth-only parallax: 速いが、被写体そのものの変形を表せず汎用性が低い。

## 公開時の注意

コードと学習済み重みのライセンスは別です。モデル本体をGitへ含めず、
`MODEL_MANIFEST.json` に入手先と確認状態を記録します。FFmpegの同梱形態とcodec設定も、
配布前にライセンスを確認します。
