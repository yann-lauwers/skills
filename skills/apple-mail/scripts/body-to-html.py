#!/usr/bin/env python3
"""Turn a plain-text mail body into the HTML Apple Mail's compose window expects.

Reads the body file, writes two siblings the caller pastes as one pasteboard item:
an HTML flavour and a plain-text fallback. Called by mail-draft.sh; not a general
Markdown renderer, and deliberately small — the conventions below are the whole set.

    blank line          paragraph break
    "- " at line start  a list item; consecutive ones become one <ul>
    everything else     a paragraph, verbatim

No font, colour or size is emitted. The compose window applies its own default to
pasted HTML that specifies none, so the new text matches the account's compose
font instead of freezing whatever this script guessed.
"""
import html
import sys


def render(text):
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    while lines and lines[-1] == '':
        lines.pop()

    out = []
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append('</ul>')
            in_list = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- ') or stripped == '-':
            item = html.escape(stripped[2:]) if stripped != '-' else ''
            if not in_list:
                out.append('<ul>')
                in_list = True
            out.append('<li>%s</li>' % item)
            continue
        close_list()
        if stripped == '':
            out.append('<div><br></div>')
        else:
            out.append('<div>%s</div>' % html.escape(line))
    close_list()
    return ''.join(out)


def main():
    if len(sys.argv) != 4:
        sys.exit('usage: body-to-html.py <body-file> <html-out> <text-out>')
    body_path, html_out, text_out = sys.argv[1:4]
    with open(body_path, encoding='utf-8') as fh:
        text = fh.read()
    with open(html_out, 'w', encoding='utf-8') as fh:
        fh.write(render(text))
    with open(text_out, 'w', encoding='utf-8') as fh:
        fh.write(text)


if __name__ == '__main__':
    main()
