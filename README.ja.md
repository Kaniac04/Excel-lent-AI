
<p align="center">
  <a href="README.md">English</a> | <strong>日本語</strong>
</p>

<h1 align="center">Excel-lent AI Interview Platform</h1>

<p align="center">
AI を活用した技術面接プラットフォームです。対話型インタビューを通じて、さまざまな技術分野における知識や理解度を評価できます。
</p>

<p align="center">
  <img src="assets/japanese_excel_ai_flowchart.svg" alt="システムアーキテクチャ" width="900">
</p>

---

## 📖 技術設計書

システムアーキテクチャ、設計方針、および実装の詳細については、以下をご参照ください。
- **English:** [Technical Design Document](assets/English_Excel_AI_TDD.md)
- **日本語:** [設計書](assets/Japanese_Excel_AI_設計書.md)

## システム要件

- **CPU**: 8 コア以上（ローカル LLM の実行には推奨）
- **メモリ**: 最低 16GB（32GB 推奨）
- **GPU**: NVIDIA GPU（VRAM 8GB 以上推奨）
- **ストレージ**: LLM モデル用に 20GB 以上の空き容量
- **対応 OS**: macOS、Windows、Linux

---

## 前提条件

### 1. LM Studio

- [LM Studio](https://lmstudio.ai/) をダウンロードしてインストールします。
- LM Studio を起動し、推奨モデルをダウンロードします。
  - Qwen3 8B（または同程度の 8～12B パラメータモデル）
- ローカル推論サーバーを起動します（デフォルトポート: `1234`）。

### 2. Python

- Python 3.9 以上
- pip（Python パッケージマネージャー）

---

## インストール

### 1. リポジトリをクローン

```bash
git clone https://github.com/kaniac04/Excel-lentAI.git
cd Excel-lentAI
```

### 2. 仮想環境を作成

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
.\venv\Scripts\activate
```

### 3. 必要なライブラリをインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数を設定

以下の値を設定してください。

```text
API_URL=http://localhost:8000
LLM_URL=http://localhost:1234/v1/chat/completions
LLM_MODEL=qwen3:8b
TAVILY_API_KEY=your_tavily_api_key
```

---

## アプリケーションの起動

### 1. LM Studio を起動

- LM Studio を起動します。
- 使用するモデルを読み込みます。
- ローカル推論サーバーを開始します。

### 2. バックエンドを起動

```bash
python main.py
```

### 3. Streamlit フロントエンドを起動

```bash
streamlit run streamlit_ui.py
```

### 4. アプリケーションへアクセス

ブラウザで以下を開いてください。

```
http://localhost:8501
```

---

## 主な機能

- 複数フェーズによる技術面接
- コンテキスト取得のためのリアルタイム Web 検索
- ストリーミング応答
- インタラクティブなチャットインターフェース
- セッション管理
- カラー対応ログ出力
- コンテンツモデレーション

---

## アーキテクチャ

- **フロントエンド**: Streamlit
- **バックエンド**: FastAPI
- **LLM インターフェース**: ローカル LM Studio サーバー
- **Web 検索**: Tavily API
- **セッション管理**: インメモリストレージ
- **ログ**: カスタムカラー対応ロガー

---

## 注意事項

- アプリケーションを起動する前に LM Studio が実行されていることを確認してください。
- 面接品質は使用する LLM モデルによって異なります。
- より大規模なモデルほど高品質な結果が期待できますが、より多くの計算資源が必要です。
- Web 検索機能を利用するため、安定したインターネット接続が必要です。

---

## ライセンス

MIT License