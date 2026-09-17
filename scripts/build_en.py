#!/usr/bin/env python3
"""Generate the English pages under en/ from the Spanish source pages.

The Spanish pages are the source of truth. English copy lives next to it in attributes:

  data-en="..."          replaces the element's text
  data-en-html="..."     replaces the element's inner HTML
  data-en-<attr>="..."   replaces <attr> (alt, content, href, aria-label, lang...)
  data-es-only           the element is dropped from the English page
  <template data-en-only>  its content is inserted only in the English page

Relative href/src URLs are rewritten to work from en/, unless they come from a data-en-<attr>
override, which is used as written. All data-es* / data-en* attributes are stripped.

Usage:  python3 scripts/build_en.py          # write en/*.html
        python3 scripts/build_en.py --check  # exit 1 if en/ is out of date (used in CI)
"""
import html
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["index.html", "privacy-policy.html"]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
ABSOLUTE = re.compile(r"^([a-zA-Z][a-zA-Z0-9+.-]*:|#|/|\.\./)")


def fmt_tag(tag, attrs, self_closing=False):
    parts = [tag]
    for name, value in attrs:
        parts.append(name if value is None else '%s="%s"' % (name, html.escape(value, quote=True)))
    return "<%s%s>" % (" ".join(parts), " /" if self_closing else "")


def relocate(url):
    if ABSOLUTE.match(url):
        return url
    return "../" + (url[2:] if url.startswith("./") else url)


class EnglishBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.out = []
        self.skip_tag = None  # while set, drop everything until this element closes
        self.skip_depth = 0
        self.keep_close = False  # emit the closing tag once skipping ends
        self.unwrap = []  # stack: True for <template data-en-only> whose tags we don't emit

    def emit(self, text):
        if self.skip_tag is None:
            self.out.append(text)

    def start_skipping(self, tag, keep_close):
        if tag not in VOID:
            self.skip_tag, self.skip_depth, self.keep_close = tag, 1, keep_close

    def handle_starttag(self, tag, attrs, self_closing=False):
        if self.skip_tag is not None:
            if tag == self.skip_tag:
                self.skip_depth += 1
            return
        names = {n for n, _ in attrs}
        if "data-es-only" in names:
            self.start_skipping(tag, keep_close=False)
            return
        if tag == "template":
            self.unwrap.append("data-en-only" in names)
            if self.unwrap[-1]:
                return

        values = dict(attrs)
        overridden = {n[len("data-en-"):] for n in names if n.startswith("data-en-") and n != "data-en-html"}
        new_attrs = []
        for name, value in attrs:
            if name.startswith("data-es") or name.startswith("data-en"):
                continue
            if name in overridden:
                value = values["data-en-" + name]
            elif name in ("href", "src") and value is not None:
                value = relocate(value)
            new_attrs.append((name, value))
        existing = {n for n, _ in new_attrs}
        new_attrs += [(n, values["data-en-" + n]) for n in sorted(overridden - existing)]

        original = self.get_starttag_text()
        changed = new_attrs != attrs
        self.out.append(fmt_tag(tag, new_attrs, self_closing) if changed else original)

        if "data-en-html" in names:
            self.out.append(values["data-en-html"])
            self.start_skipping(tag, keep_close=True)
        elif "data-en" in names:
            self.out.append(html.escape(values["data-en"], quote=False))
            self.start_skipping(tag, keep_close=True)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs, self_closing=True)

    def handle_endtag(self, tag):
        if self.skip_tag is not None:
            if tag == self.skip_tag:
                self.skip_depth -= 1
                if self.skip_depth == 0:
                    self.skip_tag = None
                    if self.keep_close:
                        self.out.append("</%s>" % tag)
            return
        if tag == "template" and self.unwrap and self.unwrap.pop():
            return
        self.out.append("</%s>" % tag)

    def handle_data(self, data):
        self.emit(data)

    def handle_entityref(self, name):
        self.emit("&%s;" % name)

    def handle_charref(self, name):
        self.emit("&#%s;" % name)

    def handle_comment(self, data):
        self.emit("<!--%s-->" % data)

    def handle_decl(self, decl):
        self.emit("<!%s>" % decl)


def build(source):
    builder = EnglishBuilder()
    builder.feed(source)
    builder.close()
    return "".join(builder.out)


def main():
    check = "--check" in sys.argv[1:]
    stale = []
    for page in PAGES:
        with open(os.path.join(ROOT, page), encoding="utf-8") as f:
            result = build(f.read())
        target = os.path.join(ROOT, "en", page)
        current = open(target, encoding="utf-8").read() if os.path.exists(target) else None
        if current == result:
            continue
        stale.append("en/" + page)
        if not check:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(result)
    if check and stale:
        print("Out of date: %s. Run: python3 scripts/build_en.py" % ", ".join(stale))
        return 1
    print(("Wrote: " + ", ".join(stale)) if stale else "en/ is up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
