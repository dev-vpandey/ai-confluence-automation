#!/usr/bin/env python3
"""
Unified Confluence Page Management
Handles create, update, read, and search operations

Usage:
    # Create new page
    python confluence_page.py create SPACE "Title" HTML_FILE [PARENT_ID]

    # Update existing page
    python confluence_page.py update PAGE_ID "Title" HTML_FILE

    # Read existing page
    python confluence_page.py read PAGE_ID

    # Search pages
    python confluence_page.py search "query" [SPACE]
"""

import sys
import requests
import os
import time
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from config import BASE_URL, SESSION_FILE

def is_cloud_instance() -> bool:
    return ".atlassian.net" in BASE_URL

def check_cookie_age(interactive=None):
    """Check if cookies are older than 12 hours and optionally prompt refresh

    Args:
        interactive: If None, auto-detect. If False, skip prompts. If True, always prompt.
    """
    session_file = SESSION_FILE

    if not session_file.exists():
        return False

    # Get file age in hours
    file_age_seconds = time.time() - session_file.stat().st_mtime
    file_age_hours = file_age_seconds / 3600

    if file_age_hours > 12:
        print(f"⚠️  Cookies are {file_age_hours:.1f} hours old (> 12 hours)")
        print("   Cookies may expire soon. Consider running: ./refresh-auth")
        print()

        # Auto-detect if we're in an interactive terminal
        if interactive is None:
            import sys
            interactive = sys.stdin.isatty()

        if interactive:
            try:
                response = input("   Refresh cookies now? [y/N]: ").strip().lower()
                if response == 'y':
                    print()
                    refresh_script = Path(__file__).parent.parent / "refresh-auth"
                    try:
                        subprocess.run([str(refresh_script)], check=True)
                        print()
                        return True
                    except subprocess.CalledProcessError:
                        print("   ❌ Cookie refresh failed. Continuing with old cookies...")
                        print()
                        return False
                else:
                    print("   Continuing with existing cookies...")
                    print()
            except (EOFError, KeyboardInterrupt):
                print("\n   Continuing with existing cookies...")
                print()
                return False
        else:
            # Non-interactive mode: just warn and continue
            print("   (Running in non-interactive mode - continuing with existing cookies)")
            print()

    return False

def load_cookies():
    """Load cookies from ~/.confluence-session"""
    if is_cloud_instance():
        print("❌ Cloud Confluence detected (atlassian.net).")
        print("   Cookie auth is not supported for Atlassian Cloud.")
        print("   Set CONFLUENCE_TOKEN in your shell profile and re-source it.")
        sys.exit(1)

    session_file = SESSION_FILE

    if not session_file.exists():
        print("❌ No cookies found.")
        print()
        print("Run: ./refresh-auth --manual")
        print("Or see: docs/AUTH_GUIDE.md")
        sys.exit(1)

    # Check cookie age
    check_cookie_age()

    cookies = {}
    with open(session_file) as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                cookies[key] = value

    return cookies

def create_session(cookies):
    """Create authenticated session"""
    session = requests.Session()
    for name, value in cookies.items():
        session.cookies.set(name, value, domain=urlparse(BASE_URL).netloc, path="/")
    return session

def _auth_hint():
    if os.environ.get('CONFLUENCE_TOKEN'):
        return (
            "   PAT invalid or expired.\n"
            "   Rotate CONFLUENCE_TOKEN in your shell profile and re-source it."
        )
    if is_cloud_instance():
        return (
            "   Atlassian Cloud requires a PAT.\n"
            "   Set CONFLUENCE_TOKEN in your shell profile and re-source it."
        )
    return (
        "   Your cookies have expired or are invalid.\n"
        "   Run: ./refresh-auth guided"
    )

def get_session():
    token = os.environ.get('CONFLUENCE_TOKEN')
    if token:
        session = requests.Session()
        session.headers.update({'Authorization': f'Bearer {token}'})
        return session
    cookies = load_cookies()
    return create_session(cookies)

def fix_html(html_content):
    """Fix common HTML issues"""
    html_content = html_content.replace(' & ', ' &amp; ')
    html_content = html_content.replace('>&<', '>&amp;<')
    return html_content

def create_page(space, title, html_file, parent_id=None):
    """Create new Confluence page"""
    session = get_session()

    # Load and fix HTML
    with open(html_file) as f:
        html_content = fix_html(f.read())

    # Build payload
    page_data = {
        "type": "page",
        "title": title,
        "space": {"key": space},
        "body": {
            "storage": {
                "value": html_content,
                "representation": "storage"
            }
        }
    }

    # Add parent if specified
    if parent_id:
        page_data["ancestors"] = [{"id": parent_id}]

    # Create
    print(f"Creating page: {title} in {space} space...")
    response = session.post(f"{BASE_URL}/rest/api/content", json=page_data)

    if response.status_code == 200:
        page_info = response.json()
        page_id = page_info["id"]
        page_url = f"{BASE_URL}/spaces/{space}/pages/{page_id}"
        print("\n" + "="*60)
        print("✅ SUCCESS!")
        print("="*60)
        print(f"URL: {page_url}")
        print(f"Page ID: {page_id}")
        return page_url
    else:
        print(f"❌ Failed: {response.status_code}")

        # Provide helpful error messages based on status code
        if response.status_code == 401:
            print("\n🔐 Authentication Error:")
            print(_auth_hint())
        elif response.status_code == 403:
            print("\n🚫 Permission Error:")
            print(f"   You don't have permission to create pages in space '{space}'")
            print("   Check your Confluence permissions or try a different space.")
        elif response.status_code == 404:
            print("\n❓ Not Found:")
            print(f"   Space '{space}' not found or parent page ID is invalid.")
            print(f"   Verify the space key and parent ID.")
        elif response.status_code == 400:
            print("\n⚠️  Bad Request:")
            print("   The page data is invalid. Check the HTML content and title.")

        print(f"\nResponse: {response.text[:500]}")
        sys.exit(1)

def update_page(page_id, title, html_file):
    """Update existing Confluence page"""
    session = get_session()

    # Get current version
    response = session.get(f"{BASE_URL}/rest/api/content/{page_id}?expand=version,space")
    if response.status_code != 200:
        print(f"❌ Failed to get page: {response.status_code}")
        sys.exit(1)

    page = response.json()
    current_version = page["version"]["number"]
    space = page["space"]["key"]

    # Load and fix HTML
    with open(html_file) as f:
        html_content = fix_html(f.read())

    # Update
    print(f"Updating page {page_id} (v{current_version} → v{current_version + 1})...")

    update_data = {
        "version": {"number": current_version + 1},
        "title": title,
        "type": "page",
        "body": {
            "storage": {
                "value": html_content,
                "representation": "storage"
            }
        }
    }

    response = session.put(f"{BASE_URL}/rest/api/content/{page_id}", json=update_data)

    if response.status_code == 200:
        page_url = f"{BASE_URL}/spaces/{space}/pages/{page_id}"
        print("\n" + "="*60)
        print("✅ SUCCESS!")
        print("="*60)
        print(f"URL: {page_url}")
        return page_url
    else:
        print(f"❌ Failed: {response.status_code}")

        # Provide helpful error messages based on status code
        if response.status_code == 401:
            print("\n🔐 Authentication Error:")
            print(_auth_hint())
        elif response.status_code == 403:
            print("\n🚫 Permission Error:")
            print(f"   You don't have permission to edit page {page_id}")
            print("   Check your Confluence permissions.")
        elif response.status_code == 404:
            print("\n❓ Not Found:")
            print(f"   Page {page_id} not found.")
            print("   Verify the page ID is correct.")
        elif response.status_code == 409:
            print("\n⚠️  Conflict:")
            print("   The page was modified by someone else.")
            print("   Try again - the script will get the latest version.")
        elif response.status_code == 400:
            print("\n⚠️  Bad Request:")
            print("   The page data is invalid. Check the HTML content and title.")

        print(f"\nResponse: {response.text[:500]}")
        sys.exit(1)

def read_page(page_id):
    """Read existing Confluence page content"""
    session = get_session()

    print(f"Reading page {page_id}...")

    # Get page with body content
    response = session.get(
        f"{BASE_URL}/rest/api/content/{page_id}",
        params={"expand": "body.storage,version,space"}
    )

    if response.status_code == 200:
        page = response.json()
        title = page["title"]
        space = page["space"]["key"]
        version = page["version"]["number"]
        html_content = page["body"]["storage"]["value"]
        page_url = f"{BASE_URL}/spaces/{space}/pages/{page_id}"

        print("\n" + "="*60)
        print("✅ Page Retrieved")
        print("="*60)
        print(f"Title: {title}")
        print(f"Space: {space}")
        print(f"Version: {version}")
        print(f"URL: {page_url}")
        print(f"Page ID: {page_id}")
        print("="*60)
        print("\nContent:\n")
        print(html_content)
        print("\n" + "="*60)
        return html_content
    else:
        print(f"❌ Failed to read page: {response.status_code}")

        if response.status_code == 401:
            print("\n🔐 Authentication Error:")
            print(_auth_hint())
        elif response.status_code == 403:
            print("\n🚫 Permission Error:")
            print(f"   You don't have permission to read page {page_id}")
        elif response.status_code == 404:
            print("\n❓ Not Found:")
            print(f"   Page {page_id} not found.")
            print("   Verify the page ID is correct.")

        print(f"\nResponse: {response.text[:500]}")
        sys.exit(1)

def search_pages(query, space=None):
    """Search Confluence pages"""
    session = get_session()

    # Build CQL query
    if space:
        cql = f"space={space} AND title~'{query}'"
    else:
        cql = f"title~'{query}'"

    print(f"Searching: {cql}")

    response = session.get(
        f"{BASE_URL}/rest/api/content/search",
        params={"cql": cql, "limit": 10}
    )

    if response.status_code == 200:
        results = response.json().get("results", [])
        print(f"\n✅ Found {len(results)} page(s):\n")

        for page in results:
            # Handle both content and search result formats
            space_key = page.get("space", {}).get("key", "")
            if not space_key and "_expandable" in page:
                # Search API returns different format
                space_key = page.get("_links", {}).get("webui", "").split("/spaces/")[1].split("/")[0] if "/spaces/" in page.get("_links", {}).get("webui", "") else "?"

            title = page["title"]
            page_id = page["id"]
            url = f"{BASE_URL}{page.get('_links', {}).get('webui', f'/spaces/{space_key}/pages/{page_id}')}"
            print(f"  [{space_key}] {title}")
            print(f"  → {url}\n")
    else:
        print(f"❌ Search failed: {response.status_code}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Create: python confluence_page.py create SPACE 'Title' HTML_FILE [PARENT_ID]")
        print("  Update: python confluence_page.py update PAGE_ID 'Title' HTML_FILE")
        print("  Read:   python confluence_page.py read PAGE_ID")
        print("  Search: python confluence_page.py search 'query' [SPACE]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) < 5:
            print("Usage: python confluence_page.py create SPACE 'Title' HTML_FILE [PARENT_ID]")
            sys.exit(1)

        space = sys.argv[2]
        title = sys.argv[3]
        html_file = sys.argv[4]
        parent_id = sys.argv[5] if len(sys.argv) > 5 else None

        create_page(space, title, html_file, parent_id)

    elif command == "update":
        if len(sys.argv) < 5:
            print("Usage: python confluence_page.py update PAGE_ID 'Title' HTML_FILE")
            sys.exit(1)

        page_id = sys.argv[2]
        title = sys.argv[3]
        html_file = sys.argv[4]

        update_page(page_id, title, html_file)

    elif command == "read":
        if len(sys.argv) < 3:
            print("Usage: python confluence_page.py read PAGE_ID")
            sys.exit(1)

        page_id = sys.argv[2]
        read_page(page_id)

    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: python confluence_page.py search 'query' [SPACE]")
            sys.exit(1)

        query = sys.argv[2]
        space = sys.argv[3] if len(sys.argv) > 3 else None

        search_pages(query, space)

    else:
        print(f"Unknown command: {command}")
        print("Available commands: create, update, read, search")
        sys.exit(1)

if __name__ == "__main__":
    main()
