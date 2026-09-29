# 実践会DB V4

実践会DB（https://db.almacreation.workers.dev/）の数字を、このリポジトリで扱うためのV4スナップショットと表示ページ。

- `data_v4.json` … DB v198（2026-09-29 9:52時点の速報）から取った集計値。会員個人の氏名・メールは入れない
- `index.html` … `data_v4.json` を読んで表示する（同じフォルダに置いてHTTPで開く。例: `python3 -m http.server` → `/v4/`）

更新の流れ: DB（MCP `DB`）の `overview` / `get` で最新値を取り、`data_v4.json` の該当箇所と `meta.db_version` を書き換える。DBは読むだけ。取り直しは `request_update` で依頼する。
