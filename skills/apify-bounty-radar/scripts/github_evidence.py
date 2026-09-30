#!/usr/bin/env python3
"""Bounded, read-only public GitHub evidence. No claimability inference or writes."""

import argparse
import datetime
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request


API = "https://api.github.com"


class EvidenceError(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Do not forward credentials; inspect renamed resources explicitly.


def api_url(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != "api.github.com" or parsed.fragment:
        raise EvidenceError("Refused a URL outside the GitHub API")
    return url


class Client:
    def __init__(self, token=None, max_requests=30):
        self.token = token
        self.max_requests = max_requests
        self.requests = 0
        self.stopped = None
        self.opener = urllib.request.build_opener(NoRedirect())

    def get(self, url):
        api_url(url)
        if self.stopped:
            raise EvidenceError(self.stopped)
        if self.requests >= self.max_requests:
            raise EvidenceError("Request limit reached; evidence is incomplete")
        headers = {"Accept": "application/vnd.github+json",
                   "X-GitHub-Api-Version": "2026-03-10",
                   "User-Agent": "apify-awesome-skills/apify-bounty-radar"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        self.requests += 1
        try:
            with self.opener.open(urllib.request.Request(url, headers=headers), timeout=20) as response:
                return json.load(response), response.headers
        except urllib.error.HTTPError as exc:
            # Do not print request headers, token values, or arbitrary response bodies.
            self.stopped = "GitHub HTTP " + str(exc.code)
            for key in ("Retry-After", "X-RateLimit-Reset"):
                value = exc.headers.get(key, "")
                if value.isdigit():
                    self.stopped += f"; {key}={value}"
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            self.stopped = "GitHub network/TLS/JSON error; no automatic retry"
        raise EvidenceError(self.stopped)


def next_link(headers):
    for part in headers.get("Link", "").split(","):
        match = re.search(r'<([^>]+)>;\s*rel="next"', part)
        if match:
            return api_url(match.group(1))
    return None


def collect(client, url, max_pages, search=False):
    result = {"items": [], "pages": 0, "complete": False, "next": url, "errors": []}
    if search:
        result.update(total_count=None, incomplete_results=False)
    seen = set()
    try:
        while result["next"] and result["pages"] < max_pages:
            payload, headers = client.get(result["next"])
            items = payload.get("items") if search and isinstance(payload, dict) else payload
            if not isinstance(items, list):
                raise EvidenceError("Unexpected API collection shape")
            if search:
                result["total_count"] = payload.get("total_count")
                result["incomplete_results"] |= bool(payload.get("incomplete_results"))
            for item in items:
                key = item.get("id")
                if key is None or key not in seen:
                    result["items"].append(item)
                if key is not None:
                    seen.add(key)
            result["pages"] += 1
            result["next"] = next_link(headers)
        if result["next"]:
            result["errors"].append("Page limit reached; follow the remaining next page")
        if search and (result["incomplete_results"] or
                       (result["total_count"] or 0) > len(result["items"])):
            result["errors"].append("Search is incomplete; narrow the query")
        result["complete"] = not result["next"] and not result["errors"]
    except EvidenceError as exc:
        result["errors"].append(str(exc))
    return result


def search_issues(client, query, max_pages):
    if re.search(r"\b(?:is:private|is:pr|type:pr)\b", query, re.IGNORECASE):
        raise EvidenceError("Discovery supports public issues only")
    query = query + " is:public is:issue"
    url = API + "/search/issues?" + urllib.parse.urlencode(
        {"q": query, "sort": "updated", "order": "desc", "per_page": 100})
    result = collect(client, url, min(max_pages, 10), search=True)
    return {"query": query, "search": result, "coverage": {"complete": result["complete"]}}


def evidence(client, repo, number, max_pages):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or number < 1:
        raise EvidenceError("Expected OWNER/REPO and a positive issue/PR number")
    root = API + "/repos/" + repo
    repository, _ = client.get(root)
    if repository.get("private") is not False:
        raise EvidenceError("This helper only collects public repository evidence")
    issue_url = root + "/issues/" + str(number)
    issue, _ = client.get(issue_url)
    result = {"repository": {k: repository.get(k) for k in
                             ("full_name", "html_url", "private", "archived", "disabled")},
              "issue": issue, "coverage": {"complete": False, "errors": []},
              "competition_checked": False}
    collections = ("comments", "timeline")
    for kind in collections:
        result[kind] = collect(client, issue_url + "/" + kind + "?per_page=100", max_pages)
    if "pull_request" in issue:
        try:
            result["pull_request"], _ = client.get(root + "/pulls/" + str(number))
        except EvidenceError as exc:
            result["coverage"]["errors"].append(str(exc))
        for kind, suffix in (("reviews", "reviews"), ("review_comments", "comments")):
            result[kind] = collect(client, root + f"/pulls/{number}/{suffix}?per_page=100", max_pages)
        collections += ("reviews", "review_comments")
    for kind in collections:
        result["coverage"]["errors"].extend(kind + ": " + err for err in result[kind]["errors"])
    if len(result["comments"]["items"]) != issue.get("comments"):
        result["coverage"]["errors"].append("Retrieved comment count differs from issue metadata")
    try:
        latest, _ = client.get(issue_url)
        result["issue_latest"] = latest
        if any(latest.get(k) != issue.get(k) for k in ("updated_at", "comments", "state")):
            result["coverage"]["errors"].append("Issue changed during collection; recheck before deciding")
    except EvidenceError as exc:
        result["coverage"]["errors"].append(str(exc))
    result["coverage"]["complete"] = not result["coverage"]["errors"]
    return result


def positive(value):
    value = int(value)
    if value < 1:
        raise argparse.ArgumentTypeError("must be positive")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    search = commands.add_parser("search")
    search.add_argument("query")
    issue = commands.add_parser("evidence")
    issue.add_argument("repo")
    issue.add_argument("number", type=positive)
    for command in (search, issue):
        command.add_argument("--max-pages", type=positive, default=5)
        command.add_argument("--max-requests", type=positive, default=30)
    args = parser.parse_args()
    client = Client(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"), args.max_requests)
    try:
        result = (search_issues(client, args.query, args.max_pages) if args.command == "search"
                  else evidence(client, args.repo, args.number, args.max_pages))
    except EvidenceError as exc:
        result = {"coverage": {"complete": False, "errors": [str(exc)]}}
    result["checked_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result["requests"] = client.requests
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["coverage"]["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
