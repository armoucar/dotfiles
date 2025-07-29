#!/usr/bin/env python3
import argparse
import subprocess
import sys
from urllib.parse import urlparse


def approve_pr(pr_url: str, body: str = "LGTM") -> bool:
    """
    Calls `gh pr review <pr_url> --approve --body "<body>"`.
    Returns True on success, False on failure.
    """
    try:
        # Run: gh pr review <URL> --approve --body "LGTM"
        result = subprocess.run(
            ["gh", "pr", "review", pr_url, "--approve", "--body", body],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print(f"[OK] Approved {pr_url}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to approve {pr_url}:\n{e.stderr}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Approve one or more GitHub PRs via `gh` CLI with an LGTM review."
    )
    parser.add_argument(
        "pr_urls", nargs="+", help="One or more GitHub pull request URLs to approve."
    )
    parser.add_argument(
        "--body", default="LGTM", help="Review body to post (default: %(default)s)."
    )
    args = parser.parse_args()

    # Basic validation of URLs
    for url in args.pr_urls:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or "github.com" not in parsed.netloc:
            print(f"[ERROR] Invalid GitHub URL: {url}", file=sys.stderr)
            sys.exit(1)

    # Approve each PR
    failed = 0
    for url in args.pr_urls:
        if not approve_pr(url, body=args.body):
            failed += 1
    if failed:
        sys.exit(failed)  # Exit with number of failures as code


if __name__ == "__main__":
    main()
