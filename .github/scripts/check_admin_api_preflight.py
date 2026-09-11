#!/usr/bin/env python3
"""Check the unauthenticated preflight used by FAM's Manage permissions page."""

import argparse
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def check_preflight(url, frontend_url):
    frontend = urlsplit(frontend_url)
    if frontend.scheme not in {"http", "https"} or not frontend.netloc:
        raise ValueError("The frontend URL must have an HTTP(S) origin")
    origin = f"{frontend.scheme}://{frontend.netloc}"
    request = Request(url, method="OPTIONS", headers={
        "Origin": origin,
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "authorization,content-type",
    })
    with urlopen(request, timeout=30) as response:
        if not 200 <= response.status < 300:
            raise ValueError("Preflight must return a successful HTTP status")

        origins = response.headers.get_all("Access-Control-Allow-Origin", [])
        if len(origins) != 1 or origins[0].strip() not in {origin, "*"}:
            raise ValueError("Preflight does not allow the frontend origin")

        methods = {
            method.strip()
            for value in response.headers.get_all("Access-Control-Allow-Methods", [])
            for method in value.split(",")
        }
        if not methods.intersection({"GET", "*"}):
            raise ValueError("Preflight does not allow GET")

        headers = {
            header.strip().lower()
            for value in response.headers.get_all("Access-Control-Allow-Headers", [])
            for header in value.split(",")
        }
        # Fetch requires Authorization to be listed explicitly, even with '*'.
        # FAM's cross-origin Axios requests do not include browser cookies.
        if "authorization" not in headers:
            raise ValueError("Preflight does not explicitly allow Authorization")
        if not headers.intersection({"content-type", "*"}):
            raise ValueError("Preflight does not allow Content-Type")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Admin API URL ending in /admin-user-accesses")
    parser.add_argument("frontend_url", help="Frontend URL from Terraform outputs")
    args = parser.parse_args()
    try:
        check_preflight(args.url, args.frontend_url)
    except HTTPError as error:
        print(f"Admin API preflight failed: HTTP {error.code}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError, ValueError) as error:
        print(f"Admin API preflight failed: {error}", file=sys.stderr)
        return 1
    print("Admin API preflight succeeded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
