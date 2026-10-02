# 引き継ぎメモ：デザイン担当（dezain）の新設

作成日: 2026-10-02 ／ リポジトリ: `oikawashinobu/alma-dashboard` ／ ブランチ: `claude/gracious-faraday-59yock`（main には未マージ・PR未作成）

## 1. 経緯
1. 社長の問い「AI社員にデザイン担当（LP・セールスレター）はいたか」→ 見える範囲（Notion・このリポジトリ・クラウド側のスキル）にはいなかった。コピー担当（`harada-sales-letter`・`seminar-slide-formula`）はいるが、どちらも見た目は担当外。※社員名簿の本体（Macの `~/CLAUDE.md`・`~/.claude/skills/`）はクラウドから見えないため未確認
2. 社長の方針「デザインはCodexに任せ、その橋渡しをする担当を入れる。コピー担当の原稿が仕上がったらデザインにする流れ」→ スキル `dezain` を作成
3. 基本の型＝ https://ipspub.com/lp/tac9th/ （The Authors' Club 第9期募集LP）。最初はクラウドのネットワーク制限で開けず、社長が環境のネットワーク許可を変えたあとに実測（スマホ390px・PC1280pxの全体スクショ、HTML・CSS・JS）
4. 社長の指示「アニメーション・テキストの見せ方・フェードインはこの見本をベースに。見本は今後追加していく」→ 見本の動きを部品（kit）として固定し、見本を足せる構成にした
5. 社長の指示「LPのコーディングはCodex、画像・インフォグラフィックはGPTの最新画像生成モデル」→ 画像の手順とスクリプトを追加
6. 社長の指示「スキルとして覚えておいて」→ リポジトリの `.claude/skills/dezain/` に置き、claude.ai アップロード用の `dezain.zip` を渡した

## 2. 決まったこと
**分担**
| 担当 | やること | やらないこと |
|---|---|---|
| コピー担当（harada-sales-letter 等） | 原稿・見出し・CTA文言・法令表記 | 見た目 |
| デザイン担当（dezain） | ヒアリング、構成の当てはめ、Codex指示書・画像指示、検品、UTAGE反映手順 | 原稿の書き換え（変えたい時はコピー担当へ差し戻す） |
| Codex | LPのコーディング、インフォグラフィックの文字・数字の重ね | 文言の変更・追加・削除、画像の自作 |
| GPTの最新画像生成モデル | 画像・インフォグラフィックの絵の部分 | 原稿の文字・数字を描くこと |

**流れ**: 原稿が `status: 検品済み` になったら受け取る → ヒアリング → 画像（案出し→社長が選ぶ→本番）→ Codex指示書 → Codexが実装 → 検品（文言一致・スマホ/PC・法令表記・動き・画像）→ /kensa → UTAGE反映手順。納品末尾に計測4行。

**土台（毎回は聞かない）**: 動き・フェードイン・テキストの見せ方・部品は tac9th 由来の kit に固定。
- FVは上から順に出る（1秒・0.8秒ずつずらす）／スクロールで下20pxからふわっと（0.75秒）／数字カード・推薦の声は左右交互／区切り・手紙はフェード
- 黄マーカーは1段落1か所まで／下線は主張の言い切り／赤で大きくはページで1〜2か所
- CTAは見本どおりなら「本文中に置かず最後に集約＋固定ボタン」。ただし案件ごとにヒアリングで決める

**毎回ヒアリングするもの**: 使う見本／FV／色（`:root` の変数）／CTAの出し方／写真素材。動きは「外したい・足したい」時だけ。

**画像のルール**
- 使う前に最新モデルを公式ガイドで確認（ https://developers.openai.com/api/docs/guides/image-generation ）。2026-10-02時点＝本番 `gpt-image-2.5-sunburst`、案出し `gpt-image-2.5-flare`
- 原稿の文言・数字・注記は画像に描かせない（公式ガイドも文字配置が苦手と明記）。文字はHTMLで重ねる
- 実在の人物・お客様・受賞・会場は生成しない（受領写真を使う）。他社ロゴ・参照LPの画像に似せない
- APIキー（`OPENAI_API_KEY`）はファイルに書かない

## 3. 作ったファイル（すべて `.claude/skills/dezain/` 配下）
| ファイル | 中身 |
|---|---|
| `SKILL.md` | 役割・分担・流れ（0受け取り〜5 UTAGE反映）・検品項目 |
| `references/design-base.md` | 全案件共通の土台（動き・テキストの見せ方・余白・部品の一覧） |
| `references/samples/README.md` | 見本の一覧と、見本の足し方（実測→記録→土台と比較→kitへ取り込み） |
| `references/samples/tac9th.md` | 見本1本目。上から15ブロックの骨格、CTAの出し方、色・書体の実測値、動きの実測とkitの対応 |
| `references/hearing.md` | ヒアリングシート（見本→FV→色→CTA→素材） |
| `references/images.md` | 画像・インフォグラフィックの作り方（モデル・サイズ・文字の扱い・禁止事項・流れ） |
| `kit/base.css` / `kit/base.js` | 土台の実体。依存なし（jQuery・GSAP不要）、動きを減らす設定の人には自動で止める |
| `kit/demo.html` | 全部品の見本ページ（文言はダミー） |
| `templates/codex-brief.md` | Codex向け指示書のひな形（ブロック対応表・CTA・色・画像） |
| `templates/image-brief.md` | 画像1枚ごとの指示のひな形 |
| `codex/AGENTS.md` | Codex側のルール（文言を変えない・kitで組む・画像は自作しない・1ファイル納品） |
| `scripts/copy_check.py` | 原稿とHTMLの文言を照合（欠落・追加を一覧） |
| `scripts/gen_image.py` | 画像生成（サイズ条件の事前チェック、`img/` 保存、`images.md` に自動記録、`--dry-run` あり） |

ほか: `ai-shain/README.md`（置き場所と導入手順）、`.gitignore`（`__pycache__` 除外）、このメモ。

## 4. 確認済みのこと／未確認のこと
- 確認済み: `copy_check.py`（正しいページは通過、書き換え1文・追加1文を検出）／`kit/demo.html` をスマホ幅390pxで表示（動く要素20個すべて表示、FVの順次表示、固定ボタン、横流れ、続きを読む、横はみ出しなし、エラーなし、動きを減らす設定で停止）／`gen_image.py`（偽サーバー相手に保存と記録まで、サイズ・透過の入力チェック）
- 未確認: **本物のOpenAI APIでの画像生成**（クラウドにAPIキーが無い）／**Codexに実際に指示書を渡して作らせること**／kit のPC幅（1280px）の見た目と、Webフォント読み込み時の見た目（検証時はGoogle Fontsを止めて代替フォントで表示した）

## 5. 残っている作業
**社長の操作が必要**
1. `dezain.zip` を claude.ai の 設定 → 機能 → スキル からアップロード（どの会話でも使えるようにする）。zipはこの会話で渡し済み。作り直しは `cd .claude/skills && zip -r dezain.zip dezain -x '*/__pycache__/*'`
2. `OPENAI_API_KEY` を画像を作る環境に設定（Macのターミナル、またはクラウド環境の設定）
3. 最初の題材を決める（例: 進行中のLP案件）

**次のセッションでやること**
4. APIキーが入ったら、`gen_image.py` で1枚作って本物のAPIで動作確認（モデル名をまず公式ガイドで再確認）
5. 最初の題材で通しの試運転: コピー担当の確定原稿 → ヒアリング → 指示書 → Codex → 検品 → 反映手順。気づいた点をスキルに反映
6. kit をPC幅とWebフォントありで確認
7. Mac側: `~/CLAUDE.md` の社員名簿に「デザイン担当＝dezain」を追加。コピー担当（harada-sales-letter）の納品末尾に「検品済みになったら dezain へ」の一行を追加（account skill なのでMac側か claude.ai 側で編集）
8. ブランチ `claude/gracious-faraday-59yock` を main に取り込むか決める（PR未作成）
9. 任意: Notion「📁 案件管理」に本件の行を作るか、「OIKAWA AI COMPANY OS 統合」の行に追記

**今後も続くこと**
- 新しい参考LPを渡されたら `references/samples/README.md` の手順で見本を追加し、使う見せ方は kit と `design-base.md` に取り込む。直したら zip を作り直して再アップロード

## 6. 環境メモ
- このクラウド環境は、社長がネットワーク許可を変えたので ipspub.com に接続できる。他のサイトは止められることがある（WebFetch・curlが403なら環境の Network access で許可を足してもらう）
- クラウドのセッションからは Claude in Chrome・Macのファイルに手が届かない（Chromeで開いたページや `~/` を扱う作業はローカルのセッションで）
- Chromium で外部サイトを撮る時は、プロキシ証明書の関係でリクエストをNode経由で通す必要があった（`NODE_USE_ENV_PROXY=1 NODE_EXTRA_CA_CERTS=/root/.ccr/ca-bundle.crt`、Playwright の `page.route` で fetch して fulfill）
