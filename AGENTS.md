# GitHub Copilot エージェント設定

このドキュメントは、プロジェクトの開発環境とエージェント設定について説明します。

## プロジェクト概要

- **ターゲットボード**: Raspberry Pi Pico
- **言語**: MicroPython
- **IDE**: Visual Studio Code

## 開発環境

### ハードウェア
ハードウェア構成の詳細については、[HARDWARE.md](HARDWARE.md) を参照してください。

### ソフトウェアスタック
- **プログラミング言語**: MicroPython
- **ファームウェア**: Raspberry Pi Pico用MicroPythonファームウェア
- **開発ツール**: 
  - VS Code + MicroPico拡張機能
  - USB経由のシリアル通信

## MicroPython の詳細

### 主要機能
- Python 3.4+構文との互換性
- RP2040用ハードウェア抽象化レイヤー
- 組み込みモジュール: `machine`, `time`, `sys`, `gc`
- GPIO, PWM, I2C, SPI, UARTのサポート

### よく使用するモジュール
```python
from machine import Pin, PWM, I2C, SPI, UART
import time
import sys
```

### GPIO制御
```python
# LED制御の例
led = Pin(25, Pin.OUT)  # Pin 25はオンボードLED
led.on()
led.off()
led.toggle()
```

## プロジェクト構造

```
.
├── AGENTS.md           # このファイル - エージェント設定
├── HARDWARE.md         # ハードウェア構成と使用例
├── pyrightconfig.json # Python型チェック設定
├── ruff.toml          # Ruffリンター設定
├── projects/          # 各プロジェクトディレクトリ
│   └── [プロジェクト]/
└── tests/             # テストファイル
    ├── color_test.py
    ├── st7735.py
    └── main.py
```

### プロジェクトの構成

各プロジェクトは`projects/`ディレクトリ下に独立したディレクトリとして配置されます:
- 各プロジェクトディレクトリには`main.py`をエントリーポイントとして配置
- プロジェクト固有のモジュールやライブラリは同じディレクトリに配置
- 各プロジェクトには`README.md`でドキュメントを記述

## コーディングガイドライン

### MicroPython ベストプラクティス
1. **メモリ管理**: RAMの制約（264KB）に注意
2. **ピン番号**: 物理ピン番号ではなく、GPIO番号（0-28）を使用
3. **インポート**: メモリを節約するため、必要なモジュールのみをインポート
4. **エラー処理**: ハードウェア操作にはtry-exceptを使用
5. **スリープ関数**: 遅延には`time.sleep()`または`time.sleep_ms()`を使用

### よく使うパターン

#### デジタル出力
```python
pin = Pin(pin_number, Pin.OUT)
pin.value(1)  # HIGH
pin.value(0)  # LOW
```

#### デジタル入力
```python
button = Pin(pin_number, Pin.IN, Pin.PULL_UP)
state = button.value()
```

#### PWM（パルス幅変調）
```python
pwm = PWM(Pin(pin_number))
pwm.freq(1000)  # 周波数を設定
pwm.duty_u16(32768)  # 50%デューティサイクル (0-65535)
```

#### アナログ入力（ADC）
```python
from machine import ADC
adc = ADC(Pin(26))  # ADC0
value = adc.read_u16()  # 0-65535
```

## 開発ワークフロー

1. **コード作成**: VS Codeで`.py`ファイルを作成・編集
2. **アップロード**: MicroPico拡張機能を使用してPicoにアップロード
3. **テスト**: REPLまたはボードのリセットでコードを実行
4. **デバッグ**: シリアルコンソールで出力を監視

## エージェント向けの指示

このプロジェクトで作業する際は以下に注意してください:

1. **プロジェクト構成**:
   - 各プロジェクトは`projects/`ディレクトリ下に独立したフォルダとして作成
   - プロジェクトフォルダには`main.py`をエントリーポイントとして配置
   - 共通ライブラリやモジュールはプロジェクトフォルダ内に配置
   - 新しいプロジェクトを作成する際は`projects/プロジェクト名/`の形式で作成

2. **ハードウェアの制約を常に考慮**:
   - 限られたRAM（264KB）
   - 限られたフラッシュ（2MB）
   - RP2040デュアルコアARM Cortex-M0+

3. **MicroPython構文を使用**:
   - すべてのPythonライブラリが利用可能ではありません
   - ハードウェアアクセスには`machine`モジュールを使用
   - 外部ライブラリよりも組み込み関数を優先

4. **ピン配置の把握**:
   - GPIO 25: オンボードLED
   - GPIO 26-28: ADC対応
   - ピン割り当ての詳細については [HARDWARE.md](HARDWARE.md) を参照

5. **コード例は以下であること**:
   - メモリ効率的
   - 適切にコメント付き
   - ハードウェア上ですぐに実行可能

6. **よくあるタスク**:
   - TFTディスプレイグラフィックス（ST7735R、SPI経由）
   - チャタリング防止付きボタン入力（方向＋アクションボタン）
   - 音声生成（パッシブブザー、PWM使用）
   - ゲームループの実装
   - スプライトレンダリングとアニメーション
   - 衝突検出
   - スコア追跡と表示

## リソース

- [MicroPython ドキュメント](https://docs.micropython.org/)
- [Raspberry Pi Pico ドキュメント](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)
- [MicroPython Pico SDK](https://docs.micropython.org/en/latest/rp2/quickref.html)
- [Pico ピン配置図](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html#pinout-and-design-files)

## 注記

- REPL（Read-Eval-Print Loop）はUSBシリアル接続経由でアクセス可能
- `main.py`は存在する場合、起動時に自動実行されます
- `Ctrl+C`でREPL内の実行中のコードを中断
- `Ctrl+D`でボードをソフトリセット
