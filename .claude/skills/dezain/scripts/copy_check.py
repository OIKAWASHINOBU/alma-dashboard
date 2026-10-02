#!/usr/bin/env python3
"""原稿(copy.md)とCodexが作ったHTMLの文言が一致しているかを確かめる。

使い方: python3 copy_check.py copy.md index.html
- 欠落: 原稿にあるのにHTMLに無い行
- 追加: HTMLにあるのに原稿に無い文言（Codexが足したもの）
どちらも0なら終了コード0。
"""
import re
import sys
from html.parser import HTMLParser

SKIP_TAGS = {"script", "style", "noscript", "template", "svg"}
MIN_LEN = 4  # これより短い断片（「▼」「×」など）は判定しない


def norm(s):
    return re.sub(r"[\s　]+", "", s)


def md_lines(text):
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)  # frontmatter
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out = []
    for line in text.splitlines():
        line = re.sub(r"^\s*(#{1,6}\s+|>\s*|[-*+]\s+|\d+\.\s+)", "", line)
        line = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", line)
        line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
        line = re.sub(r"(\*\*|__|\*|_|~~|`|==)", "", line)
        line = line.strip().strip("|")
        if re.fullmatch(r"[-:| ]*", line):
            continue
        for cell in line.split("|"):
            if len(norm(cell)) >= MIN_LEN:
                out.append(cell.strip())
    return out


class TextBlocks(HTMLParser):
    BLOCK = {"p", "div", "section", "h1", "h2", "h3", "h4", "h5", "h6", "li",
             "td", "th", "dt", "dd", "blockquote", "figcaption", "a", "button",
             "header", "footer", "article", "br", "tr"}

    def __init__(self):
        super().__init__()
        self.skip = 0
        self.blocks = [""]

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip += 1
        elif tag in self.BLOCK:
            self.blocks.append("")

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
        elif tag in self.BLOCK:
            self.blocks.append("")

    def handle_data(self, data):
        if not self.skip:
            self.blocks[-1] += data


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        lines = md_lines(f.read())
    p = TextBlocks()
    with open(sys.argv[2], encoding="utf-8") as f:
        p.feed(f.read())
    html_all = norm("".join(p.blocks))
    copy_all = norm("".join(lines))

    missing = [l for l in lines if norm(l) not in html_all]
    added = [b.strip() for b in p.blocks
             if len(norm(b)) >= MIN_LEN and norm(b) not in copy_all]

    print(f"欠落 {len(missing)}件 / 追加 {len(added)}件")
    for l in missing:
        print(f"  [欠落] {l}")
    for b in added:
        print(f"  [追加] {b}")
    return 0 if not missing and not added else 1


if __name__ == "__main__":
    sys.exit(main())
