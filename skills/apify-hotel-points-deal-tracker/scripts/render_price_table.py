#!/usr/bin/env python3
"""Render a travel price comparison as an email-ready HTML table plus Markdown.

Turns normalized rows (hotels, rentals, or flights) into two deliverables:
a standalone HTML file that renders correctly when pasted into Gmail or Outlook,
and a Markdown version for docs and chat. The HTML styling mirrors a working
lodging price table (navy headers, zebra striping, right-aligned numbers,
booking links), so the output is ready to send without extra formatting.

Stdlib only. No third-party dependencies.

Input JSON schema (pass a file with --in, or pipe on stdin):

{
  "title": "Trip lodging options",
  "subtitles": ["Dates: Thu Oct 15 to Mon Oct 19, 2026", "Party: 3 travelers"],
  "note": "Rates are per night for the party unless a column says total.",
  "sections": [
    {
      "heading": "Denver options (near airport)",
      "subheading": "Thursday, Oct 15 (arrival night)",   // optional H3
      "note": "Entire homes, priced as a 2-night total.",  // optional
      "columns": [
        {"key": "name",  "label": "Hotel", "link_key": "link"},
        {"key": "class", "label": "Class", "num": true},
        {"key": "rating","label": "Rating","num": true},
        {"key": "price", "label": "Per night", "num": true, "price": true}
      ],
      "rows": [
        {"name": "Example Inn", "link": "https://example.com", "class": "3",
         "rating": "4.1", "price": "$124"}
      ]
    }
  ],
  "footer": "Prices pulled from Google Hotels via johnvc/google-hotels-search-scraper. Verify before booking."
}

Usage:
  python3 render_price_table.py --in table.json --out /path/to/basename
    writes /path/to/basename.html and /path/to/basename.md
  python3 render_price_table.py --in table.json --format html
    prints HTML to stdout
"""

import argparse
import html
import json
import sys

CSS = """  body { font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #1a1a1a; background: #ffffff; margin: 0; padding: 24px; line-height: 1.45; }
  .wrap { max-width: 820px; margin: 0 auto; }
  h1 { font-size: 22px; margin: 0 0 4px; }
  h2 { font-size: 17px; margin: 30px 0 8px; padding-bottom: 5px; border-bottom: 2px solid #33526e; color: #33526e; }
  h3 { font-size: 14px; margin: 18px 0 6px; color: #333; }
  p.sub { margin: 0 0 6px; color: #444; }
  p.note { font-size: 13px; color: #555; margin: 6px 0 0; }
  table { border-collapse: collapse; width: 100%; margin: 8px 0 4px; font-size: 14px; }
  th, td { border: 1px solid #cccccc; padding: 7px 9px; text-align: left; vertical-align: top; }
  th { background: #33526e; color: #ffffff; font-weight: 600; }
  tbody tr:nth-child(even) { background: #f4f6f8; }
  td.num, th.num { text-align: right; white-space: nowrap; }
  .price { font-weight: 700; white-space: nowrap; }
  a { color: #1a5fb4; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .foot { font-size: 12px; color: #666; margin-top: 24px; border-top: 1px solid #ddd; padding-top: 10px; }"""


def _cell_text(row, col):
    val = row.get(col["key"], "")
    if val is None:
        val = ""
    return str(val)


def render_html(data):
    out = []
    out.append("<!DOCTYPE html>")
    out.append('<html lang="en">')
    out.append("<head>")
    out.append('<meta charset="utf-8">')
    out.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    out.append("<title>%s</title>" % html.escape(data.get("title", "Price table")))
    out.append("<style>")
    out.append(CSS)
    out.append("</style>")
    out.append("</head>")
    out.append("<body>")
    out.append('<div class="wrap">')
    out.append("")
    out.append("  <h1>%s</h1>" % html.escape(data.get("title", "")))
    for sub in data.get("subtitles", []):
        out.append('  <p class="sub">%s</p>' % html.escape(sub))
    if data.get("note"):
        out.append('  <p class="note">%s</p>' % html.escape(data["note"]))

    for section in data.get("sections", []):
        out.append("")
        out.append("  <h2>%s</h2>" % html.escape(section.get("heading", "")))
        if section.get("subheading"):
            out.append("  <h3>%s</h3>" % html.escape(section["subheading"]))
        cols = section.get("columns", [])
        out.append("  <table>")
        head = "    <thead><tr>"
        for col in cols:
            cls = ' class="num"' if col.get("num") else ""
            head += "<th%s>%s</th>" % (cls, html.escape(col.get("label", "")))
        head += "</tr></thead>"
        out.append(head)
        out.append("    <tbody>")
        for row in section.get("rows", []):
            line = "      <tr>"
            for col in cols:
                classes = []
                if col.get("num"):
                    classes.append("num")
                if col.get("price"):
                    classes.append("price")
                cls = ' class="%s"' % " ".join(classes) if classes else ""
                text = html.escape(_cell_text(row, col))
                link_key = col.get("link_key")
                href = row.get(link_key) if link_key else None
                if href:
                    cell = '<a href="%s">%s</a>' % (html.escape(str(href)), text)
                else:
                    cell = text
                line += "<td%s>%s</td>" % (cls, cell)
            line += "</tr>"
            out.append(line)
        out.append("    </tbody>")
        out.append("  </table>")
        if section.get("note"):
            out.append('  <p class="note">%s</p>' % html.escape(section["note"]))

    if data.get("footer"):
        out.append("")
        out.append('  <p class="foot">%s</p>' % html.escape(data["footer"]))
    out.append("")
    out.append("</div>")
    out.append("</body>")
    out.append("</html>")
    return "\n".join(out) + "\n"


def render_markdown(data):
    out = []
    out.append("# %s" % data.get("title", ""))
    out.append("")
    for sub in data.get("subtitles", []):
        out.append("**%s**  " % sub)
    if data.get("note"):
        out.append("")
        out.append("_%s_" % data["note"])
    for section in data.get("sections", []):
        out.append("")
        out.append("## %s" % section.get("heading", ""))
        if section.get("subheading"):
            out.append("")
            out.append("### %s" % section["subheading"])
        cols = section.get("columns", [])
        out.append("")
        out.append("| " + " | ".join(c.get("label", "") for c in cols) + " |")
        out.append("| " + " | ".join("---:" if c.get("num") else "---" for c in cols) + " |")
        for row in section.get("rows", []):
            cells = []
            for col in cols:
                text = _cell_text(row, col).replace("|", "\\|")
                link_key = col.get("link_key")
                href = row.get(link_key) if link_key else None
                if href:
                    cells.append("[%s](%s)" % (text, href))
                else:
                    cells.append(text)
            out.append("| " + " | ".join(cells) + " |")
        if section.get("note"):
            out.append("")
            out.append("_%s_" % section["note"])
    if data.get("footer"):
        out.append("")
        out.append("---")
        out.append("")
        out.append(data["footer"])
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Render a travel price table to HTML and Markdown.")
    ap.add_argument("--in", dest="infile", help="Input JSON file (default: stdin)")
    ap.add_argument("--out", dest="out", help="Output basename; writes .html and .md")
    ap.add_argument("--format", choices=["html", "md", "both"], default="both",
                    help="What to emit to stdout when --out is not given (default both)")
    args = ap.parse_args()

    raw = open(args.infile).read() if args.infile else sys.stdin.read()
    data = json.loads(raw)

    html_doc = render_html(data)
    md_doc = render_markdown(data)

    if args.out:
        with open(args.out + ".html", "w") as f:
            f.write(html_doc)
        with open(args.out + ".md", "w") as f:
            f.write(md_doc)
        print("Wrote %s.html and %s.md" % (args.out, args.out))
    else:
        if args.format in ("html", "both"):
            sys.stdout.write(html_doc)
        if args.format == "both":
            sys.stdout.write("\n")
        if args.format in ("md", "both"):
            sys.stdout.write(md_doc)


if __name__ == "__main__":
    main()
