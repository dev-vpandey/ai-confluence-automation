#!/usr/bin/env python3
"""
Confluence File Attachment Upload
Uploads files as attachments to Confluence pages
"""

import sys
import requests
from pathlib import Path
from confluence_page import load_cookies, create_session, BASE_URL

def attach_file(page_id, file_path, comment=""):
    """Attach a file to a Confluence page"""
    cookies = load_cookies()
    session = create_session(cookies)

    file_path = Path(file_path)
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    print(f"Uploading {file_path.name} to page {page_id}...")

    data = {
        'comment': comment,
        'minorEdit': 'true'
    }

    # Upload attachment
    url = f"{BASE_URL}/rest/api/content/{page_id}/child/attachment"

    # Check if attachment already exists
    response = session.get(url, params={'filename': file_path.name})

    with open(file_path, 'rb') as fh:
        files = {
            'file': (file_path.name, fh, 'application/octet-stream')
        }
        headers = {'X-Atlassian-Token': 'nocheck'}

        if response.status_code == 200:
            results = response.json().get('results', [])
            if results:
                attachment_id = results[0]['id']
                print(f"Attachment exists (ID: {attachment_id}), updating...")
                post_url = f"{BASE_URL}/rest/api/content/{attachment_id}/data"
                response = session.post(post_url, files=files, data=data, headers=headers)
            else:
                response = session.post(url, files=files, data=data, headers=headers)
        else:
            response = session.post(url, files=files, data=data, headers=headers)

    if response.status_code in [200, 201]:
        result = response.json()
        print("\n" + "="*60)
        print("✅ SUCCESS!")
        print("="*60)
        print(f"Attachment: {file_path.name}")
        print(f"Attachment ID: {result.get('id', 'N/A')}")
        return True
    else:
        print(f"\n❌ Failed: {response.status_code}")
        print(response.text[:500])
        sys.exit(1)

def main():
    if len(sys.argv) < 3:
        print("Usage: python attach_file.py PAGE_ID FILE_PATH [COMMENT]")
        print("\nExample:")
        print("  python attach_file.py 1050182299 diagram.drawio 'Architecture diagram'")
        sys.exit(1)

    page_id = sys.argv[1]
    file_path = sys.argv[2]
    comment = sys.argv[3] if len(sys.argv) > 3 else ""

    attach_file(page_id, file_path, comment)

if __name__ == "__main__":
    main()
