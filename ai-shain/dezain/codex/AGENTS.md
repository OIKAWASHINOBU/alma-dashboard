# AGENTS.md（Codex用・デザイン実装）

このフォルダはLP／セールスレターのデザイン実装用です。指示は `brief.md`、文言は `copy.md`、見た目の型は `design-base.md` にあります。

## 絶対に守ること
1. **文言を変えない。** `copy.md` の文章は一字一句そのまま使う。言い換え・要約・追加・削除・順番の入れ替えをしない。見出しを足したい・削りたいと思ったら、実装せず `notes.md` に提案として書く。
2. **brief.md に書いていない決定をしない。** 色・FV・アニメーションは brief の値を使う。brief に無ければ `design-base.md` に従い、それでも決まらなければ控えめな方を選んで `notes.md` に書く。
3. **スマホ優先。** 375px幅で崩れない・横スクロールが出ないこと。次に1280px幅で確認。
4. **アニメーションはCSS中心で控えめに。** `prefers-reduced-motion: reduce` のときは止める。文字が読めない時間を作らない。
5. **1ファイル納品。** `index.html` にCSS/JSを内包。外部読み込みはGoogle Fontsのみ。画像は `img/` 配下の相対パス。
6. 各セクションに `data-block="S01"` などのブロック番号を付ける（検品とUTAGE反映で使う）。

## 終わったら
- `images.md` と `notes.md` を書く
- 自分で `python3 copy_check.py copy.md index.html` を実行し、欠落0・追加0を確認してから終える（このフォルダにある場合）
