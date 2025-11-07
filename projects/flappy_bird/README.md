# Flappy Bird for Raspberry Pi Pico

Raspberry Pi PicoとTFTディスプレイを使用したフラッピーバードゲームです。

## ハードウェア要件

- Raspberry Pi Pico (RP2040)
- 1.8インチ TFT液晶ディスプレイ (ST7735R、128x160ピクセル)
- タクトスイッチ 1個 (Aボタン - ジャンプ用)
- パッシブブザー 1個

## ピン配線

### TFTディスプレイ (SPI)
- SCK: GPIO 2
- MOSI: GPIO 3
- MISO: GPIO 4
- CS: GPIO 5
- DC: GPIO 6
- RST: GPIO 7
- VCC: 3.3V
- GND: GND

### ボタン
- Aボタン (ジャンプ): GPIO 8 (プルアップ、GNDに接続)

### ブザー
- パッシブブザー: GPIO 22

## ファイル構成

```
├── flappy_bird.py      # メインゲームファイル
├── st7735.py           # TFTディスプレイドライバ
├── main.py             # 自動起動用エントリーポイント
├── README.md           # このファイル
├── HARDWARE.md         # ハードウェア詳細とピン配置
├── AGENTS.md           # 開発環境とエージェント設定
├── pyrightconfig.json  # Python型チェック設定
└── ruff.toml           # Pythonリンター設定
```

## インストール方法

1. Raspberry Pi PicoにMicroPythonファームウェアをインストール
2. `st7735.py`と`flappy_bird.py`をPicoにアップロード
3. `flappy_bird.py`を実行

VS Code + MicroPico拡張機能を使用している場合:
- ファイルを右クリック → "Upload current file to Pico"
- 実行: `flappy_bird.py`を開いて "Run current file on Pico"

## 遊び方

1. **色テスト画面**: 起動時に色の表示確認（Aボタンで次へ）
2. **タイトル画面**: Aボタンを押してゲームスタート
3. **ゲーム中**: Aボタンを押して鳥をジャンプさせる
4. **目的**: パイプの間を通り抜けてスコアを稼ぐ
5. **ゲームオーバー**: パイプや地面に当たるとゲーム終了
6. **リスタート**: ゲームオーバー画面でAボタンを押すと再スタート

## ゲーム特徴

- シンプルな操作（ワンボタン）
- スムーズなアニメーション（約33fps）
- 効果音付き（ジャンプ、スコア、ゲームオーバー）
- リアルタイムスコア表示
- ランダムに生成されるパイプ
- RGB/BGR自動対応（色テスト画面付き）
- Viperネイティブコードによる高速描画

## カスタマイズ

`flappy_bird.py`内の定数を変更することで、ゲームの難易度を調整できます：

```python
PIPE_SPEED = 2        # パイプの速度（大きいほど難しい）
PIPE_GAP = 40         # パイプの隙間（小さいほど難しい）
GRAVITY = 1           # 重力（大きいほど難しい）
JUMP_STRENGTH = -6    # ジャンプ力（絶対値が大きいほど高く飛ぶ）
```

## トラブルシューティング

### ディスプレイが表示されない
- 配線を確認してください
- SPIの通信速度を下げてみてください（`baudrate=10000000`など）

### 色が正しく表示されない（赤が青く見える等）
- 起動時の色テスト画面で確認
- `flappy_bird.py`の`display`初期化部分で`bgr`パラメータを変更：
  ```python
  # デフォルトはbgr=True（ほとんどのST7735モジュール）
  # 色が入れ替わる場合
  display = st7735.ST7735R(..., bgr=False)
  ```
- 詳細は`HARDWARE.md`の「色設定のトラブルシューティング」セクションを参照

### ボタンが反応しない
- プルアップ抵抗が有効になっているか確認
- ボタンがGNDに正しく接続されているか確認
- 正しいGPIOピン（GPIO 8）に接続されているか確認

### 動作が遅い
- `time.sleep_ms(30)`の値を大きくしてフレームレートを下げる
- ディスプレイの更新頻度を調整

## ライセンス

このプロジェクトは教育目的で作成されました。自由に改変・配布できます。

## 参考資料

- [MicroPython Documentation](https://docs.micropython.org/)
- [Raspberry Pi Pico Documentation](https://www.raspberrypi.com/documentation/microcontrollers/)
- [ST7735 Datasheet](https://www.displayfuture.com/Display/datasheet/controller/ST7735.pdf)
