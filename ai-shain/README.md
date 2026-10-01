# AI社員（下書き置き場）

クラウドのセッションで作ったAI社員の下書きです。正本はMac側の `~/.claude/skills/` なので、確認できたら移します。

## dezain（デザイン担当）
コピー担当の確定原稿 → ヒアリング → Codex向け指示書 → Codexが実装 → 検品 → UTAGE反映手順。

Macに入れる:
```
cp -R ai-shain/dezain ~/.claude/skills/dezain
```
入れた後に `~/CLAUDE.md` の社員名簿へ「デザイン担当＝dezain」を追加し、コピー担当（harada-sales-letter 等）の納品末尾に「検品済みになったら dezain へ」と一行足す。

土台＝`references/design-base.md` と `kit/`（動き・テキストの見せ方・部品。`kit/demo.html` で全部品を確認できる）。見本＝`references/samples/`（初版 tac9th。見本は今後追加していく）。
