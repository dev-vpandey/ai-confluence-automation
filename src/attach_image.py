#!/usr/bin/env python3
"""
Confluence Image Attachment Upload
Uploads image files (PNG, JPG, GIF) as attachments to Confluence pages
Works with cookie-based authentication
"""

import sys
import requests
from pathlib import Path
from urllib.parse import urlparse
from confluence_page import load_cookies, BASE_URL

def attach_image(page_id, image_path, comment=""):
    """Attach an image file to a Confluence page"""
    cookies = load_cookies()

    image_path = Path(image_path)
    if not image_path.exists():
        print(f"❌ File not found: {image_path}")
        sys.exit(1)

    # Validate image type
    valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg']
    if image_path.suffix.lower() not in valid_extensions:
        print(f"❌ Invalid image type: {image_path.suffix}")
        print(f"   Supported: {', '.join(valid_extensions)}")
        sys.exit(1)

    print(f"Uploading {image_path.name} to page {page_id}...")

    # Create session with cookies
    session = requests.Session()
    for name, value in cookies.items():
        session.cookies.set(name, value, domain=urlparse(BASE_URL).netloc, path="/")

    # Determine content type
    content_type_map = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml'
    }
    content_type = content_type_map.get(image_path.suffix.lower(), 'application/octet-stream')

    # CRITICAL: Add X-Atlassian-Token header to bypass XSRF check
    headers = {
        "X-Atlassian-Token": "nocheck"
    }

    # Check if attachment already exists
    check_url = f"{BASE_URL}/rest/api/content/{page_id}/child/attachment"
    response = session.get(check_url, params={'filename': image_path.name})

    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            # Attachment exists - update it
            attachment_id = results[0]['id']
            print(f"   Attachment exists (ID: {attachment_id}), updating...")

            # Update attachment data endpoint
            update_url = f"{BASE_URL}/rest/api/content/{attachment_id}/data"

            with open(image_path, 'rb') as f:
                files = {'file': (image_path.name, f, content_type)}
                data = {'comment': comment, 'minorEdit': 'true'}
                response = session.post(update_url, headers=headers, files=files, data=data)
        else:
            # Create new attachment
            with open(image_path, 'rb') as f:
                files = {'file': (image_path.name, f, content_type)}
                data = {'comment': comment, 'minorEdit': 'true'}
                response = session.post(check_url, headers=headers, files=files, data=data)
    else:
        # Create new attachment
        with open(image_path, 'rb') as f:
            files = {'file': (image_path.name, f, content_type)}
            data = {'comment': comment, 'minorEdit': 'true'}
            response = session.post(check_url, headers=headers, files=files, data=data)

    if response.status_code in [200, 201]:
        result = response.json()
        # Handle both single result and results array
        if isinstance(result, dict) and 'results' in result:
            attachment_id = result['results'][0].get('id', 'N/A')
        else:
            attachment_id = result.get('id', 'N/A')

        print("\n" + "="*60)
        print("✅ SUCCESS!")
        print("="*60)
        print(f"Attachment: {image_path.name}")
        print(f"Attachment ID: {attachment_id}")
        print(f"\nTo embed in page, use:")
        print(f'<ac:image><ri:attachment ri:filename="{image_path.name}"/></ac:image>')
        return attachment_id
    else:
        print(f"\n❌ Failed: {response.status_code}")
        if response.status_code == 403:
            print("XSRF check failed - ensure cookies are valid")
            print("Try: ./refresh-auth")
        elif response.status_code == 401:
            print("Authentication failed - cookies may be expired")
            print("Run: ./refresh-auth")
        else:
            print(response.text[:500])
        sys.exit(1)

def main():
    if len(sys.argv) < 3:
        print("Usage: python attach_image.py PAGE_ID IMAGE_FILE [COMMENT]")
        print("\nExample:")
        print("  python attach_image.py 1050182299 architecture.png 'System architecture diagram'")
        print("\nSupported formats: PNG, JPG, JPEG, GIF, SVG")
        sys.exit(1)

    page_id = sys.argv[1]
    image_path = sys.argv[2]
    comment = sys.argv[3] if len(sys.argv) > 3 else ""

    attach_image(page_id, image_path, comment)

if __name__ == "__main__":
    main()
