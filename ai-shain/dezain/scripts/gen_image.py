#!/usr/bin/env python3
"""OpenAIの画像生成モデルで画像を作り、img/ に保存して images.md に記録する。

使い方:
  export OPENAI_API_KEY=...
  python3 gen_image.py --out img/s01_fv_sp.png --size 1024x1536 --quality high \
      --prompt-file prompts/s01_fv_sp.txt
  案出し:   --model gpt-image-2.5-flare --quality low --n 3
  確認だけ: --dry-run（送信せず、送る内容を表示）

モデルは使う前に最新を確かめる（references/images.md）。
"""
import argparse
import base64
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request

DEFAULT_MODEL = "gpt-image-2.5-sunburst"  # 2026-10-02 時点の最新（本番用）
ENDPOINT = "https://api.openai.com/v1/images/generations"


def check_size(size):
    if size == "auto":
        return
    m = re.fullmatch(r"(\d+)x(\d+)", size)
    if not m:
        sys.exit(f"サイズの書き方が違います: {size}（例: 1024x1536）")
    w, h = int(m.group(1)), int(m.group(2))
    problems = []
    if w % 16 or h % 16:
        problems.append("幅と高さは16の倍数")
    if not (1 / 3 <= w / h <= 3):
        problems.append("縦横比は1:3〜3:1")
    if max(w, h) > 3840:
        problems.append("辺は3840px以下")
    if not (655_360 <= w * h <= 8_294_400):
        problems.append("総画素は655,360〜8,294,400")
    if problems:
        sys.exit(f"サイズ {size} は使えません: " + "、".join(problems))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="保存先（例: img/s01_fv_sp.png）。--n 2以上なら _1, _2 を付ける")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt")
    src.add_argument("--prompt-file")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--size", default="1024x1024")
    ap.add_argument("--quality", default="auto", choices=["low", "medium", "high", "xhigh", "max", "auto"])
    ap.add_argument("--background", default="auto", choices=["auto", "opaque", "transparent"])
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--log", default="images.md", help="記録ファイル")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    prompt = a.prompt if a.prompt else open(a.prompt_file, encoding="utf-8").read().strip()
    check_size(a.size)
    fmt = os.path.splitext(a.out)[1].lstrip(".").lower() or "png"
    if fmt == "jpg":
        fmt = "jpeg"
    if fmt not in ("png", "jpeg", "webp"):
        sys.exit("拡張子は png / jpg / webp")
    if a.background == "transparent" and fmt == "jpeg":
        sys.exit("透過背景は png か webp で")

    body = {"model": a.model, "prompt": prompt, "size": a.size, "quality": a.quality,
            "background": a.background, "output_format": fmt, "n": a.n}
    if a.dry_run:
        print(json.dumps(body, ensure_ascii=False, indent=2))
        return 0

    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("OPENAI_API_KEY が設定されていません")
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        sys.exit(f"生成に失敗しました（HTTP {e.code}）。プロンプトや入力を直してから再実行してください。\n{detail}")

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    base, ext = os.path.splitext(a.out)
    saved = []
    for i, d in enumerate(res.get("data", []), 1):
        path = a.out if a.n == 1 else f"{base}_{i}{ext}"
        with open(path, "wb") as f:
            f.write(base64.b64decode(d["b64_json"]))
        saved.append(path)

    today = datetime.date.today().isoformat()
    new_log = not os.path.exists(a.log)
    with open(a.log, "a", encoding="utf-8") as f:
        if new_log:
            f.write("# 画像の記録\n\n| ファイル | モデル | サイズ | 品質 | 作成日 | プロンプト |\n|---|---|---|---|---|---|\n")
        for p in saved:
            f.write(f"| {p} | {a.model} | {a.size} | {a.quality} | {today} | {prompt.replace('|', '／').replace(chr(10), ' ')} |\n")
    print("保存:", ", ".join(saved))
    return 0


if __name__ == "__main__":
    sys.exit(main())
