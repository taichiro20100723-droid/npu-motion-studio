# アーキテクチャ

## 目的

NPU Motion Studioは、ユーザーが技術用語を知らなくても「AとBを選ぶ → 小・中・大を選ぶ → 作成」できる体験を提供します。A→Bを既定にし、Motion Brush、品質別のNPU画像数、NPU/GPU並列処理を備えています。180秒は通常目標ではなく異常時の安全上限です。

## 構成

```text
Browser UI
   │  JSON API
   ▼
FastAPI app ── HardwareDetector
   │
   ▼
GenerationService ── JobStore
   │
   ├── DeadlineScheduler
   │
   ▼
EngineRegistry ── MockMotionEngine
              └── OpenVINOLCMEngine
                      ├── CPU text encoder
                      ├── NPU LCM UNet
                      ├── Arc GPU VAE
                      ├── CPU Japanese-to-English translator
                      ├── Action timeline / condition warp
                      ├── A/B endpoint lock / intermediate NPU redraw
                      ├── Motion Brush move / lock / direction masks
                      ├── Small / Medium / Large anchor presets
                      ├── NPU generation ↔ Arc GPU RIFE overlap queue
                      └── Endpoint lock / seamless loop / Quick Sync MP4
```

### UI

HTML/CSS/JavaScriptだけで構成し、ビルドツールを不要にしています。APIは同じ `127.0.0.1` のFastAPIから配信するため、外部サービスへ入力画像や文章を送信しません。

### GenerationService

HTTP処理から重い生成処理を切り離し、ジョブIDを即時に返します。現在はメモリ内キューとワーカースレッド1本です。共有メモリを使うNPU/GPUで複数生成を同時実行すると遅くなるため、初期値は直列です。

通常のUIは選んだ品質（8・12・20枚）を一度に生成します。旧クライアント向けに
`preview_first=true` と `POST /api/jobs/{id}/upgrade` のAPI互換は残しています。

### v0.5並列パイプライン

中・大品質では、NPUアンカーが1枚完成するたびに直前区間を1本のArc RIFEキューへ渡します。
NPUが次の画像を描いている間にGPUが前区間を補間するため、12枚の実測ではGPU仕事8.23秒のうち
NPU終了後に残った待ちは1.57秒でした。区間を順番に結合した後、Quick Syncへ一括投入します。
小品質ではRIFE起動時間の方が大きいため、軽量補間とQuick Syncで短時間化します。

### MotionEngine

UIとAIランタイムの境界です。エンジンは `probe()` で利用可能性を返し、`generate()` で成果物を生成します。本物のOpenVINO実装、DirectML実装、クラウド実装をUI変更なしで追加できます。

### SafetyScheduler

上限は「画像」「解析」「動き」「書き出し」「配信」の予算に分けます。通常はユーザーが選んだ小・中・大の枚数を生成します。180秒へ近づいた異常時だけ要点を減らし、画面には残り時間ではなく経過時間を表示します。

### 2つの作成方式

1枚方式はAを最初のアンカーに固定し、文章から判定した動作ごとの時系列promptでNPU再描画します。
ループ時はAを補間列の最後へ再投入し、書き出し直前の最終フレームもAに固定します。

A→B方式はAの縦横比を出力規約にし、Bをcontain配置して引き伸ばしません。途中ではA/Bの
smoothstep blend、動作別warp、時刻別promptを条件としてNPU再描画します。v0.4.1ではdenoise
strengthを中央で高く、両端へ急速に低くするベル型に変更しました。中央はロボット→犬のような
hybridを自由に描き、後半はB本来の形へ早く収束します。RIFE補間後にも先頭=A、最終=Bを
再固定してからMP4へ書き出します。

### FlowCacheコア

`flowcache` は時間方向のアルゴリズムをAIランタイムから分離した層です。NPU実装より先に
CPU上で再現性のあるテストができ、純粋な数値処理はOpenCV ABIやGPUドライバーに依存しません。
本番エンジンはこの考え方にOpenVINO LCMとOpenCV DISを接続しています。

処理は次の順です。

1. `route_motion()` が文章を7種類のmotion profileへ割り当てる。
2. `plan_flowcache()` が残り時間と実測コストから1〜4枚のアンカーを選ぶ。
3. `correlated_noise_fields()` が共有ノイズと個別ノイズを混合する。期待されるアンカー間
   相関を指定でき、dense fieldがあれば共有成分を先に移動する。
4. 外部backendがアンカーを生成する。backendが無い開発時はNumPy配列をfixtureとして使える。
5. 前進・後退fieldのcycle maskで信用できない対応を除外する。
6. forward splatのoccupancyからdisocclusionを検出する。
7. 時間があれば外部inpaint、RIFEを使い、なければbilinear/parallaxまたはsmart cutへ落とす。

#### Dense motion fieldの座標規約

`DenseMotionField.vectors[y, x] = (dx, dy)` です。対応点を調べる場合、画像Aの座標 `p` に
対して画像Bの対応点は `p + field[p]` です。往復判定は
`forward(p) + backward(p + forward(p)) ≈ 0` を使います。

`bilinear_warp()` だけはbackward samplingとして同じ配列を使い、出力座標 `p` が入力の
`p + field[p]` を読みます。この向きは関数docstringにも固定しています。将来OpenVINOやRIFEの
出力を渡すadapterは、各ランタイム固有の向きをこの規約へ変換しなければなりません。

#### 欠損と修復

`forward_backward_cycle_consistency_mask()` は `True` を信頼できる対応として返します。
画像外へ出た対応や、往復誤差が絶対・相対許容値を超えた対応は `False` です。

`disocclusion_mask()` はsource pixelをtargetへbilinear forward splatし、occupancyが閾値未満の
target pixelを `True` として返します。このmaskだけが `InpaintRepairBackend` へ渡るため、
画像全体を再生成せずに済みます。

### 差し替え可能な統合プロトコル

`flowcache/protocols.py` はNumPy画像を受け渡す3境界を定義します。

| Protocol | 責任 | 想定実装 | CPU fallback |
|---|---|---|---|
| `AnchorImageBackend` | txt2img/img2imgアンカー | OpenVINO SD1.5 INT8/LCM | fixtureまたは入力画像 |
| `InpaintRepairBackend` | disocclusionだけ修復 | OpenVINO inpaint | edge fill/smart cut |
| `FrameInterpolationBackend` | 任意中間フレーム | RIFE | bilinear/parallax |

外部backendはモデルのコンパイル、キャッシュ、デバイス選択を所有します。FlowCacheコアは
それらを知らず、固定形状のNumPy配列と秒単位の上限だけを渡します。これによりOpenVINOの
img2img/inpaintやRIFEを追加しても既存HTTP APIとUIは変わりません。

### Deadline適応計画

`FlowCacheCosts` はベンチで置き換えるウォームスタート目標値です。plannerは安全余裕を先に
引き、モード別の希望アンカー枚数（fast=2、fun=3、wow=4）から時間内へ縮退します。その後、
次の順で修復を追加します。

1. cycle consistency
2. disocclusion mask
3. 外部inpaint（fun/wow）
4. 外部interpolation（wow）

このplannerはV1互換とCPU fallbackの試験用に残しています。本番エンジンは小8枚・中12枚・大20枚を使い、安全上限へ近づいた異常時だけ枚数を減らします。

## V2の実機時間

| 試験 | 実測 |
|---|---:|
| fast、4 anchors、2秒、ループ、Quick Sync | 6.05秒 |
| fun、8 anchors、4秒、ダンス、ループ | 10.75秒 |
| wow、12 anchors、5秒、建築 | 15.39秒 |

ダンス試験ではNPU画像8枚が7.11秒、Arc GPU RIFE補間が2.10秒でした。ループ版95フレームの
先頭と末尾の平均画素差は1.427、通常隣接フレームの中央値は2.068で、継ぎ目が通常の動きより
小さいことを確認しました。初回コンパイルとアプリ起動時のモデル準備は生成前に行います。

## セキュリティ境界

- 既定の待受は `127.0.0.1` のみ
- 入力Data URLは5 MiB以下
- 出力ファイル名はサーバー生成UUIDのみ
- 成果物配信は設定済み出力フォルダ内に限定
- モックSVGへユーザー文章を埋め込む際はXMLエスケープ

## 品質機能の追加順

1. 局所inpaintによる手足・新規領域の修復
2. pose ControlNetをダンスと人物動作だけ起動
3. 被写体マスクと局所補修による顔・手・車体の一貫性
4. 音声やビートに合わせた動作タイムライン
5. 顔の一貫性、電力、30入力のp90評価

## モデルとライセンス

CPU FlowCacheはモデル不要です。本番のアンカー生成にはOpenVINO LCM Dreamshaper v7 INT8を
セットアップ時に取得します。候補と実装済みモデルはルートの `MODEL_MANIFEST.json` に記録し、
Gitリポジトリへ同梱しているか、用途、インターフェース、ライセンス確認状態を分けています。
