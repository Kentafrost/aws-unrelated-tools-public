# Direct Game Input - Advanced Windows API

[日本語](#japanese) | [English](#english)

---

## <a id="japanese"></a>日本語

### 概要
本スクリプトは、通常の自動化ツールが効かないゲームに対して、複数のWindows APIメソッドを使用して
自動でボタンを押下するPythonスクリプトです。

RPGツクールで作成したゲーム等の録画のため、**自動で特定のボタンを押下したい際**などにお使いいただけます。

### 主な機能
- 🎮 **ゲーム対応**: 一般的な自動化を無視するゲームでも動作
- 🔄 **複数のAPIメソッド**: 4つの異なるWindows API手法を順次試行
- ⚙️ **自動パッケージ管理**: 必要なライブラリの自動インストール機能
- 🎯 **柔軟なキー選択**: Enter、Space、E、F キーに対応
- ⏱️ **カスタマイズ可能な間隔**: 秒単位での実行間隔設定
- 🔍 **ウィンドウ検索**: ゲームタイトルの部分一致でウィンドウを自動検出

### 使用されるWindows APIメソッド
1. **PostMessage**: ウィンドウメッセージキューに直接送信
2. **SendInput**: フォーカス取得後に入力送信
3. **SetKeyboardState**: キーボード状態を直接操作
4. **Combined Method**: 複数手法の組み合わせ + WM_CHAR

### 必要な環境
- **OS**: Windows
- **Python**: 3.6以上
- **必要パッケージ**: 
  - `keyboard` (自動インストール)
  - `pywin32` (Windowsに標準搭載)

### インストールと使用方法

#### 1. ファイルをダウンロード
```bash
git clone <repository-url>
cd record_video/record
```

#### 2. スクリプトを実行
```bash
python direct-game-input.py
```

#### 3. 設定手順
1. **ゲームタイトル入力**: 対象ゲームのウィンドウタイトルの一部を入力
2. **実行間隔設定**: キー押下の間隔を秒単位で設定（デフォルト: 5秒）
3. **キー選択**: 自動押下するキーを選択
   - 1: Enter（デフォルト）
   - 2: Space
   - 3: E
   - 4: F
4. **ウィンドウ選択**: 複数のマッチするウィンドウがある場合は番号で選択

#### 4. 実行と停止
- **開始**: 設定完了後、自動的にキー送信を開始
- **停止**: `ESC`キーを押して停止

### 使用例
```
=== Direct Game Input - Advanced Windows API ===
Enter a word in game window title (Example: Minecraft): Minecraft
Please set interval in seconds (default 5): 3
Choose key to press automatically:
1. Enter (default)
2. Space  
3. E
4. F
Enter choice (1-4): 2
Selected key: Space
Target: Minecraft 1.19.2
Press 'ESC' to stop
```

### 特徴
- **自動パッケージ管理**: 不足している`keyboard`パッケージを自動検出・インストール
- **エラーハンドリング**: 各APIメソッドの失敗を検出し、次の手法を自動試行
- **デバッグ情報**: 詳細なログでトラブルシューティングをサポート
- **安全な停止**: ESCキーでいつでも停止可能

### 注意事項
- このツールは個人使用を想定しています
- ゲームの利用規約を確認してから使用してください
- 一部のアンチチートシステムでは検出される可能性があります

### トラブルシューティング
- **ウィンドウが見つからない**: ゲームタイトルをより短く、一般的な部分で試してください
- **入力が効かない**: ゲームによっては特定のAPIメソッドのみ有効な場合があります
- **権限エラー**: 管理者として実行してみてください

---

## <a id="english"></a>English

### Overview
This script is a Python tool that uses multiple Windows API methods to automatically press buttons for games that typically ignore standard automation tools.

It can be used when you want to **automatically press specific buttons** for purposes such as recording games created with RPG Maker.

### Key Features
- 🎮 **Game Compatible**: Works with games that ignore regular automation
- 🔄 **Multiple API Methods**: Sequentially tries 4 different Windows API approaches
- ⚙️ **Auto Package Management**: Automatic installation of required libraries
- 🎯 **Flexible Key Selection**: Supports Enter, Space, E, F keys
- ⏱️ **Customizable Intervals**: Configurable execution intervals in seconds
- 🔍 **Window Detection**: Auto-detects game windows by partial title matching

### Windows API Methods Used
1. **PostMessage**: Direct sending to window message queue
2. **SendInput**: Input sending after focus acquisition
3. **SetKeyboardState**: Direct keyboard state manipulation
4. **Combined Method**: Multiple approaches + WM_CHAR messages

### Requirements
- **OS**: Windows
- **Python**: 3.6+
- **Required Packages**: 
  - `keyboard` (auto-installed)
  - `pywin32` (standard on Windows)

### Installation and Usage

#### 1. Download Files
```bash
git clone <repository-url>
cd record_video/record
```

#### 2. Run Script
```bash
python direct-game-input.py
```

#### 3. Configuration Steps
1. **Enter Game Title**: Input part of the target game's window title
2. **Set Interval**: Configure key press interval in seconds (default: 5)
3. **Select Key**: Choose which key to automatically press
   - 1: Enter (default)
   - 2: Space
   - 3: E
   - 4: F
4. **Window Selection**: If multiple matching windows exist, select by number

#### 4. Execution and Stopping
- **Start**: Automatically begins key sending after configuration
- **Stop**: Press `ESC` key to stop

### Usage Example
```
=== Direct Game Input - Advanced Windows API ===
Enter a word in game window title (Example: Minecraft): Minecraft
Please set interval in seconds (default 5): 3
Choose key to press automatically:
1. Enter (default)
2. Space  
3. E
4. F
Enter choice (1-4): 2
Selected key: Space
Target: Minecraft 1.19.2
Press 'ESC' to stop
```

### Features
- **Auto Package Management**: Automatically detects and installs missing `keyboard` package
- **Error Handling**: Detects API method failures and automatically tries next approach
- **Debug Information**: Detailed logging for troubleshooting support
- **Safe Stopping**: Can be safely stopped anytime with ESC key

### Important Notes
- This tool is intended for personal use
- Please check the game's terms of service before use
- May be detected by some anti-cheat systems

### Troubleshooting
- **Window Not Found**: Try shorter, more common parts of the game title
- **Input Not Working**: Some games may only respond to specific API methods
- **Permission Errors**: Try running as administrator

---

### License
This project is for personal use only. Please respect game terms of service and applicable laws.

### Contributing
Feel free to submit issues and enhancement requests!
