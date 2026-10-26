#!/usr/bin/env python3
"""Export Contact Scraper rows to a spreadsheet-oriented UTF-8 CSV."""
import argparse
import csv
from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path
import socket
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

ACTOR = 'signalfoundryhq~website-contact-extractor'
FIELDS = ('websiteUrl', 'pageUrl', 'pageTitle', 'emails', 'phones', 'socialLinks')
USER_AGENT = 'apify-awesome-skills/apify-source-linked-contacts-csv'


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def urlopen(request, *, timeout):
    return build_opener(NoRedirect).open(request, timeout=timeout)


def positive_usd(text):
    try:
        value = Decimal(text)
    except InvalidOperation:
        raise argparse.ArgumentTypeError('Use a positive USD amount.')
    if not value.is_finite() or value <= 0:
        raise argparse.ArgumentTypeError('Use a positive USD amount.')
    return value


def run_actor(websites, token, max_charge, max_pages=1, max_items=10, *, require_email=False, build='latest'):
    if not 1 <= len(websites) <= 25:
        raise ValueError('Provide 1 to 25 non-empty websites or contact-page URLs.')
    if not 1 <= max_pages <= 10 or not 1 <= max_items <= 250:
        raise ValueError('Use 1–10 pages per site and 1–250 delivered rows.')
    if not token:
        raise ValueError('Set APIFY_TOKEN to your own Apify API token.')
    query = urlencode({'maxTotalChargeUsd': format(max_charge, 'f'), 'memory': 256, 'timeout': 120, 'build': build})
    payload = {'websiteUrls': websites, 'maxPagesPerSite': max_pages, 'maxItems': max_items,
               'includeEmptyPages': False, 'onlyNew': False, 'stateKey': 'csv-export',
               'requireEmail': require_email}
    request = Request(
        f'https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items?{query}',
        data=json.dumps(payload).encode('utf-8'), method='POST',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json',
                 'User-Agent': USER_AGENT})
    # Do not automatically retry a paid POST: an interrupted response can hide a live run.
    with urlopen(request, timeout=150) as response:
        rows = json.load(response)
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError('Expected a JSON array of dataset records; no CSV was written.')
    if require_email and any(not row.get('emails') for row in rows):
        raise ValueError('The run returned a row without email despite requireEmail. Check the run and selected build in Console before retrying; no CSV was written.')
    return rows


def spreadsheet_cell(value):
    if value is None:
        text = ''
    elif isinstance(value, list):
        text = '; '.join(str(item) for item in value)
    else:
        text = str(value)
    # Quoting alone does not prevent spreadsheet formula interpretation.
    visible = text.lstrip(' \t\r\n\ufeff')
    if visible.startswith(('=', '+', '-', '@', '＝', '＋', '－', '＠')) or text.startswith(('\t', '\r', '\n')):
        return "'" + text
    return text


def write_csv(rows, output):
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError('Expected an array of dataset records.')
    with Path(output).open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: spreadsheet_cell(row.get(key)) for key in FIELDS})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--websites', type=Path, help='UTF-8 text file, one domain or URL per line')
    source.add_argument('--from-json', type=Path, help='Convert an existing dataset JSON array without a new run')
    parser.add_argument('--output', type=Path, default=Path('contacts.csv'))
    parser.add_argument('--max-charge', type=positive_usd, default=Decimal('0.03'))
    parser.add_argument('--max-pages', type=int, default=1)
    parser.add_argument('--max-items', type=int, default=10)
    parser.add_argument('--require-email', action='store_true', help='Keep only pages containing an extracted email; applied before result charging for a new run')
    args = parser.parse_args(argv)
    try:
        if args.from_json:
            rows = json.loads(args.from_json.read_text(encoding='utf-8-sig'))
            if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
                raise ValueError('Expected an array of dataset records.')
            if args.require_email:
                rows = [row for row in rows if row.get('emails')]
        else:
            sites = [line.strip() for line in args.websites.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
            rows = run_actor(sites, os.environ.get('APIFY_TOKEN', '').strip(), args.max_charge,
                             args.max_pages, args.max_items, require_email=args.require_email)
        write_csv(rows, args.output)
    except (HTTPError, URLError, TimeoutError, socket.timeout) as error:
        status = f' (HTTP {error.code})' if isinstance(error, HTTPError) else ''
        print(f'Request did not finish{status}. Check this Actor in Apify Console before retrying; a run may already exist. No automatic retry.', file=sys.stderr)
        return 1
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(f'Wrote {len(rows)} page records to {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
