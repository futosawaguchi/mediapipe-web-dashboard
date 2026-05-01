# mediapipe-web-dashboard

MediaPipe と Flask を使ったリアルタイム手のジェスチャー認識・顔の向き推定のWebダッシュボードです。

---

## 機能

- **手のジェスチャー認識**：グー・チョキ・パー・ポインティング・グッドの5種類を認識
- **手のランドマーク表示**：21点のランドマークと骨格ラインをリアルタイム表示（ON/OFF切り替え可能）
- **指の方向推定**：人差し指の向きを水平・垂直・奥行きの3軸で推定
- **矢印オーバーレイ**：指の向きを画面上に矢印でリアルタイム表示（ON/OFF切り替え可能）
- **顔の向き推定**：Yaw・Pitch・Rollの3軸で顔の向きをリアルタイム推定（ON/OFF切り替え可能）

---

## 技術スタック

| カテゴリ | 技術 |
|---|---|
| Backend | Python / Flask / Flask-SocketIO |
| Computer Vision | MediaPipe Tasks API / OpenCV |
| Frontend | HTML / CSS / JavaScript / Socket.IO |
| 設定管理 | python-dotenv |

---

## 動作環境

- Python 3.10 以上
- Webカメラ（内蔵・外付け問わず）
- Chrome）

---

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/futosawaguchi/mediapipe-web-dashboard.git
cd mediapipe-web-dashboard
```

### 2. 仮想環境の作成・有効化

```bash
python -m venv venv
source venv/bin/activate
```

### 3. パッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env` ファイルをプロジェクトルートに作成してください：
```
SECRET_KEY=任意のランダムな文字列
```

### 5. アプリの起動

```bash
python app.py
```

ブラウザで `http://localhost:5002` を開いてください。

> **Note**  
> 初回起動時はMediaPipeのモデルファイルが自動でダウンロードされます（数十MB）。

---

## 使い方

### ジェスチャー認識

カメラに手をかざすと、画面下部にジェスチャー名がリアルタイムで表示されます。

| ジェスチャー | 判定条件 |
|---|---|
| Guu（グー） | 全指を握る・親指を中指付け根に近づける |
| Choki（チョキ） | 人差し指・中指を伸ばす・親指を薬指付け根に近づける |
| Paa（パー） | 全指を開く |
| Pointing（ポインティング） | 人差し指だけ伸ばす・親指を中指付け根に近づける |
| Good（グッド） | 親指だけ伸ばす |

### ON/OFFトグル

左サイドバーのトグルで各機能を切り替えられます。

| トグル | 機能 |
|---|---|
| Hand Landmark | 手のランドマーク・骨格ラインの表示 |
| Face Orientation | 顔の向き推定（Yaw / Pitch / Roll） |
| Arrow Overlay | 指の向きを示す矢印の表示 |

### 指の方向推定

`POINTING DIRECTION` パネルに3軸の角度がリアルタイムで表示されます。

| 項目 | 説明 |
|---|---|
| HORIZ | 水平角度（右が正・左が負） |
| VERT | 垂直角度（上が正・下が負） |
| DEPTH | 奥行き角度（カメラ方向が正・背後方向が負）※推定値 |

---

## ディレクトリ構成

mediapipe-web-dashboard/
├── app.py                  # Flaskメインアプリ
├── config.py               # 設定値
├── camera.py               # カメラ制御・フレーム取得
├── requirements.txt        # 依存パッケージ
├── .env                    # 環境変数（Gitには含まれない）
├── gestures/               # ジェスチャー定義
│   ├── base.py             # 基底クラス・共通関数
│   ├── rock.py             # グー
│   ├── scissors.py         # チョキ
│   ├── paper.py            # パー
│   ├── pointing.py         # ポインティング
│   └── good.py             # グッド
├── detectors/              # 検出器
│   ├── hand_detector.py    # 手のランドマーク・ジェスチャー・方向推定
│   └── face_detector.py    # 顔の向き推定
├── static/
│   ├── css/style.css       # スタイル
│   └── js/main.js          # SocketIO通信・UI制御
├── templates/
│   └── index.html          # メインページ
└── tests/
├── test_hand.py        # 手のランドマーク動作確認
└── test_face.py        # 顔のランドマーク動作確認

---

## ジェスチャーの追加方法

`gestures/` フォルダに新しいファイルを追加するだけで拡張できます。

### 1. ジェスチャーファイルを作成

```python
# gestures/peace.py の例
from .base import BaseGesture, get_finger_states

class PeaceGesture(BaseGesture):
    name = "peace"
    label = "Peace"

    @staticmethod
    def detect(landmarks) -> bool:
        f = get_finger_states(landmarks)
        return f["index"] and f["middle"] and not f["ring"] and not f["pinky"]
```

### 2. `gestures/__init__.py` に追加

```python
from .peace import PeaceGesture

GESTURE_LIST = [
    RockGesture,
    ScissorsGesture,
    PaperGesture,
    PointingGesture,
    GoodGesture,
    PeaceGesture,  # 追加
]
```

---

## 設定

`config.py` で各種パラメータを変更できます。

| 設定値 | デフォルト | 説明 |
|---|---|---|
| `CAMERA_ID` | `0` | カメラデバイスID |
| `FRAME_WIDTH` | `640` | フレーム幅 |
| `FRAME_HEIGHT` | `480` | フレーム高さ |
| `HAND_DETECTION_CONFIDENCE` | `0.7` | 手の検出信頼度しきい値 |
| `FACE_DETECTION_CONFIDENCE` | `0.5` | 顔の検出信頼度しきい値 |
| `FLASK_PORT` | `5002` | Flaskのポート番号 |

---