#!/usr/bin/env python3
"""
Auto-refresh Confluence cookies from Chrome browser
Uses AppleScript to extract cookies from Chrome's storage
"""

import os
import sys
import sqlite3
import subprocess
import platform
from pathlib import Path
import tempfile
import shutil
from urllib.parse import urlparse
from config import BASE_URL, SESSION_FILE


def get_open_command() -> str:
    system = platform.system()
    if system == 'Darwin':
        return 'open'
    elif system == 'Linux':
        return 'xdg-open'
    else:
        return 'start'
COOKIE_NAMES = ["JSESSIONID", "seraph.confluence", "confluence.browse.space.cookie"]

def find_chrome_cookies_db():
    """Find Chrome's Cookies database"""
    chrome_paths = [
        Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies",
        Path.home() / "Library/Application Support/Google/Chrome/Profile 1/Cookies",
    ]

    for path in chrome_paths:
        if path.exists():
            return path

    return None

def extract_cookies_from_chrome():
    """Extract Confluence cookies from Chrome's SQLite database"""
    cookies_db = find_chrome_cookies_db()

    if not cookies_db:
        return {}

    # Chrome locks the database, so we need to copy it first
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        temp_db = tmp_file.name

    try:
        # Copy the database
        shutil.copy2(cookies_db, temp_db)

        # Connect to the copy
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Query for Confluence cookies
        cursor.execute("""
            SELECT name, value, encrypted_value
            FROM cookies
            WHERE host_key LIKE ?
            ORDER BY creation_utc DESC
        """, (f'%{urlparse(BASE_URL).netloc}%',))

        rows = cursor.fetchall()
        conn.close()

        cookies = {}
        for name, value, encrypted_value in rows:
            if name in COOKIE_NAMES and name not in cookies:
                # Chrome stores unencrypted cookies with value field
                if value:
                    cookies[name] = value

        return cookies

    except Exception as e:
        print(f"! Database read error: {e}")
        return {}
    finally:
        # Clean up temp file
        if os.path.exists(temp_db):
            os.unlink(temp_db)

def open_chrome_to_confluence():
    """Open Chrome to Confluence page"""
    applescript = f'''
    tell application "Google Chrome"
        activate
        open location "{BASE_URL}"
    end tell
    '''

    try:
        subprocess.run(['osascript', '-e', applescript],
                      check=True,
                      capture_output=True,
                      timeout=5)
        return True
    except:
        return False

def save_cookies(cookies):
    """Save cookies to session file from config"""
    if len(cookies) < 3:
        print(f"\n⚠️  Warning: Only have {len(cookies)} cookies (need 3)")
        print(f"   Have: {', '.join(cookies.keys())}")
        print(f"   Missing: {', '.join(set(COOKIE_NAMES) - set(cookies.keys()))}")
        return False

    with open(SESSION_FILE, 'w') as f:
        for name in COOKIE_NAMES:
            if name in cookies:
                f.write(f"{name}={cookies[name]}\n")

    os.chmod(SESSION_FILE, 0o600)
    print(f"\n✅ Saved {len(cookies)} cookies to {SESSION_FILE}")
    return True

def manual_input():
    """Manually input cookies from user"""
    print("\n" + "="*60)
    print("Manual Cookie Input")
    print("="*60)
    print("\n📋 To get cookies from Chrome:")
    print("   1. Make sure you're logged into Confluence")
    print("   2. Press Cmd+Option+I (open DevTools)")
    print("   3. Click 'Application' tab")
    print(f"   4. Expand 'Cookies' → {urlparse(BASE_URL).netloc}")
    print("   5. Find and copy each cookie value below\n")

    cookies = {}
    for name in COOKIE_NAMES:
        while True:
            try:
                value = input(f"   {name}: ").strip()
                if value:
                    cookies[name] = value
                    break
                else:
                    print("      (cannot be empty, please try again)")
            except (EOFError, KeyboardInterrupt):
                print("\n\n⚠️  Input cancelled")
                sys.exit(1)

    return cookies

def show_guided_instructions():
    """Show instructions for guided mode"""
    print("\n" + "="*60)
    print("Guided Cookie Extraction")
    print("="*60)
    print("\n📋 Follow these steps:\n")
    print(f"1. Open Chrome to: {BASE_URL}")
    print("   (Make sure you're logged in)\n")
    print("2. Press Cmd+Option+I to open Chrome DevTools\n")
    print("3. Click 'Application' tab (top bar)\n")
    print("4. In left sidebar, expand:")
    print(f"   Cookies → {urlparse(BASE_URL).netloc}\n")
    print("5. Find these 3 cookies and copy their 'Value' column:")
    print("   - JSESSIONID")
    print("   - seraph.confluence")
    print("   - confluence.browse.space.cookie\n")
    print("="*60)
    print()

def main():
    print("="*60)
    print("Confluence Cookie Auto-Refresh")
    print("="*60)

    # Check command line mode
    mode = sys.argv[1] if len(sys.argv) > 1 else 'auto'

    if mode == '--manual':
        cookies = manual_input()
        if save_cookies(cookies):
            print("\n✅ Cookie refresh complete!")
        return

    elif mode == '--guided':
        print("\n🌐 Opening Chrome to Confluence...")
        if open_chrome_to_confluence():
            print("✓ Chrome opened")
            import time
            time.sleep(2)
        else:
            print("! Could not open Chrome automatically")

        show_guided_instructions()
        cookies = manual_input()
        if save_cookies(cookies):
            print("\n✅ Cookie refresh complete!")
        return

    # Auto mode (default)
    print("\n🔍 Attempting automated extraction from Chrome database...")

    try:
        cookies = extract_cookies_from_chrome()

        if len(cookies) == 3:
            print(f"✓ Found all {len(cookies)} cookies in Chrome database")
            if save_cookies(cookies):
                print("\n✅ Successfully auto-refreshed cookies!")
                return
        elif len(cookies) > 0:
            print(f"! Found only {len(cookies)}/3 cookies in database")
            print("  (Chrome may have encrypted the cookies)")
        else:
            print("! No cookies found in database")
            print("  (May need to log into Confluence in Chrome)")

    except Exception as e:
        print(f"! Automated extraction failed: {e}")

    # Fall back to guided mode
    print("\n💡 Switching to guided extraction mode...")
    print("\nOpening Chrome and showing instructions...")

    if open_chrome_to_confluence():
        print("✓ Chrome opened")
        import time
        time.sleep(2)

    show_guided_instructions()

    response = input("Ready to input cookies? [Y/n]: ").strip().lower()
    if response in ['', 'y', 'yes']:
        cookies = manual_input()
        if save_cookies(cookies):
            print("\n✅ Cookie refresh complete!")
    else:
        print("\n💡 You can run these modes later:")
        print("   ./refresh-auth --guided   # Guided extraction")
        print("   ./refresh-auth --manual   # Manual input only")

if __name__ == "__main__":
    main()
