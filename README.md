# git-mcp-test

GitHub MCPサーバー 統合デモ

## 概要
これは以下の技術で構築されたシンプルなToDoアプリケーションです：
- **FastAPI** (Python 3.12+)
- **SQLModel** (SQLite)
- **HTMX** (Hypermedia-driven frontend)
- **Vanilla CSS** (外部CSSフレームワークなし)

## セットアップ

```bash
uv run uvicorn app:app --reload
```

## 機能
- ページリロードなしでのToDo追加、完了切り替え、削除
- SQLiteを使用したデータの永続化
- CSS変数を使用したモダンなUI
