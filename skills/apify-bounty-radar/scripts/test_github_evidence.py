"""Regression cases for missing late payout comments and incomplete API evidence."""

import io
import unittest
import urllib.error
from unittest.mock import Mock

from github_evidence import API, Client, EvidenceError, api_url, collect, evidence, search_issues


class FakeClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.urls = []

    def get(self, url):
        self.urls.append(url)
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


class EvidenceTests(unittest.TestCase):
    def test_late_payout_in_124_comments_is_not_lost(self):
        comments = [{"id": i, "body": "/bounty $75" if i == 1 else "attempt"}
                    for i in range(1, 125)]
        comments[-1].update(body="Maintainer: paid; this reward is no longer available",
                            html_url="https://github.com/example/repo/issues/1#issuecomment-124")
        nxt = API + "/repos/example/repo/issues/1/comments?page=2"
        client = FakeClient([(comments[:100], {"Link": f'<{nxt}>; rel="next"'}),
                             (comments[100:], {})])
        result = collect(client, API + "/first", 5)
        self.assertTrue(result["complete"])
        self.assertEqual(len(result["items"]), 124)
        self.assertIn("paid", result["items"][-1]["body"])
        self.assertEqual(client.urls[-1], nxt)

    def test_page_cap_keeps_partial_evidence_unverified(self):
        nxt = API + "/page2"
        result = collect(FakeClient([([{"id": 1, "body": "/bounty $75"}],
                                      {"Link": f'<{nxt}>; rel="next"'})]), API + "/page1", 1)
        self.assertFalse(result["complete"])
        self.assertEqual(result["next"], nxt)
        self.assertEqual(len(result["items"]), 1)

    def test_rate_limit_preserves_first_page(self):
        client = FakeClient([([{"id": 1}], {"Link": f'<{API}/page2>; rel="next"'}),
                             EvidenceError("GitHub HTTP 403; X-RateLimit-Reset=123")])
        result = collect(client, API + "/page1", 5)
        self.assertFalse(result["complete"])
        self.assertEqual(result["items"], [{"id": 1}])
        self.assertIn("403", result["errors"][0])

    def test_incomplete_search_is_not_empty_proof(self):
        client = FakeClient([({"items": [], "total_count": 0, "incomplete_results": True}, {})])
        result = search_issues(client, "label:bounty", 1)
        self.assertFalse(result["coverage"]["complete"])
        self.assertIn("is%3Apublic", client.urls[0])
        self.assertIn("is%3Aissue", client.urls[0])

    def test_search_1000_result_ceiling_is_explicit(self):
        client = FakeClient([({"items": [{"id": 1}], "total_count": 2000,
                               "incomplete_results": False}, {})])
        self.assertFalse(search_issues(client, "bounty", 10)["coverage"]["complete"])

    def test_search_refuses_private_or_pr_mode(self):
        for query in ("is:private bounty", "is:pr bounty", "type:pr bounty"):
            with self.assertRaises(EvidenceError):
                search_issues(FakeClient([]), query, 1)

    def test_next_link_cannot_send_token_to_another_host(self):
        client = FakeClient([([{"id": 1}], {"Link": '<https://example.com/leak>; rel="next"'})])
        result = collect(client, API + "/page1", 5)
        self.assertFalse(result["complete"])
        self.assertEqual(len(client.urls), 1)
        for url in ("http://api.github.com/x", "https://api.github.com@evil.example/x"):
            with self.assertRaises(EvidenceError):
                api_url(url)

    def test_private_repository_is_rejected_before_issue_fetch(self):
        client = FakeClient([({"private": True}, {})])
        with self.assertRaises(EvidenceError):
            evidence(client, "example/repo", 1, 5)
        self.assertEqual(len(client.urls), 1)

    def test_closed_pr_is_not_assumed_merged(self):
        issue = {"state": "closed", "comments": 0, "updated_at": "2026-09-30", "pull_request": {}}
        client = FakeClient([({"private": False}, {}), (issue, {}), ([], {}), ([], {}),
                             ({"merged": False, "merged_at": None}, {}),
                             ([], {}), ([], {}), (issue, {})])
        result = evidence(client, "example/repo", 1, 5)
        self.assertTrue(result["coverage"]["complete"])
        self.assertFalse(result["pull_request"]["merged"])
        self.assertFalse(result["competition_checked"])

    def test_changed_issue_invalidates_snapshot(self):
        issue = {"state": "open", "comments": 0, "updated_at": "old"}
        latest = dict(issue, comments=1, updated_at="new")
        client = FakeClient([({"private": False}, {}), (issue, {}), ([], {}), ([], {}), (latest, {})])
        self.assertFalse(evidence(client, "example/repo", 1, 5)["coverage"]["complete"])

    def test_http_failure_never_echoes_token_or_response_body(self):
        client = Client("secret-test-value")
        client.opener = Mock()
        client.opener.open.side_effect = urllib.error.HTTPError(
            API + "/test", 429, "secret-test-value", {"Retry-After": "60"},
            io.BytesIO(b"secret-test-value"))
        with self.assertRaises(EvidenceError) as error:
            client.get(API + "/test")
        self.assertNotIn("secret-test-value", str(error.exception))
        self.assertIn("Retry-After=60", str(error.exception))
        with self.assertRaises(EvidenceError):
            client.get(API + "/second")
        self.assertEqual(client.opener.open.call_count, 1)

    def test_request_budget_prevents_network_call(self):
        client = Client(max_requests=1)
        client.requests = 1
        client.opener = Mock()
        with self.assertRaises(EvidenceError):
            client.get(API + "/test")
        client.opener.open.assert_not_called()


if __name__ == "__main__":
    unittest.main()
