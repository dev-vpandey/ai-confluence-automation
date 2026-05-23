#!/usr/bin/env python3
"""
Confluence Automation Client
Clean, maintainable implementation following SOLID principles
"""

import sys
import subprocess
import requests
from http.cookiejar import Cookie
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from config import BASE_URL, SESSION_FILE, TIMEOUT_HEALTH, TIMEOUT_SEARCH, TIMEOUT_CREATE


# ============================================================================
# Authentication Layer
# ============================================================================

class AuthProvider(ABC):
    """Abstract authentication provider"""

    @abstractmethod
    def is_valid(self) -> bool:
        pass

    @abstractmethod
    def get_session(self) -> requests.Session:
        pass

    @abstractmethod
    def refresh(self) -> bool:
        pass


class SessionCookieAuth(AuthProvider):
    """Session-based authentication using JSESSIONID cookie"""

    def __init__(self, base_url: str, session_file: Path):
        self.base_url = base_url
        self.session_file = session_file
        self.cookie_value: Optional[str] = None
        self._session: Optional[requests.Session] = None

    def is_valid(self) -> bool:
        """Check if current authentication is valid"""
        if not self._load_cookie():
            return False

        try:
            session = self.get_session()
            response = session.get(f'{self.base_url}/rest/api/space?limit=1', timeout=TIMEOUT_HEALTH)
            return response.status_code == 200
        except:
            return False

    def get_session(self) -> requests.Session:
        """Get authenticated session"""
        if not self._session:
            self._session = self._create_session()
        return self._session

    def refresh(self) -> bool:
        """Refresh authentication by getting new cookie"""
        print("\n" + "="*60)
        print("  Authentication Required")
        print("="*60)
        print("\nOpening Confluence in browser...")

        subprocess.run(['open', self.base_url], check=False)

        print("\nSteps:")
        print("  1. Login with Microsoft SSO")
        print("  2. F12 → Application → Cookies")
        print("  3. Copy 'JSESSIONID' value")
        print("="*60)

        cookie = input("\nPaste JSESSIONID: ").strip().strip('"').strip("'")

        if not cookie:
            return False

        self._save_cookie(cookie)
        self._session = None  # Force recreation
        return self.is_valid()

    def _load_cookie(self) -> bool:
        """Load cookie from file"""
        if not self.session_file.exists():
            return False

        try:
            with open(self.session_file) as f:
                content = f.read().strip()
                self.cookie_value = content.split('=', 1)[1] if '=' in content else content
            return True
        except:
            return False

    def _save_cookie(self, cookie_value: str):
        """Save cookie to file"""
        with open(self.session_file, 'w') as f:
            f.write(f"JSESSIONID={cookie_value}")
        self.session_file.chmod(0o600)
        self.cookie_value = cookie_value

    def _create_session(self) -> requests.Session:
        """Create requests session with cookie"""
        session = requests.Session()
        cookie = Cookie(
            version=0, name='JSESSIONID', value=self.cookie_value,
            port=None, port_specified=False,
            domain=urlparse(self.base_url).netloc,
            domain_specified=True, domain_initial_dot=False,
            path='/', path_specified=True, secure=True,
            expires=None, discard=True,
            comment=None, comment_url=None, rest={}, rfc2109=False
        )
        session.cookies.set_cookie(cookie)
        return session


# ============================================================================
# Content Conversion Layer
# ============================================================================

class ContentConverter:
    """Convert content between formats"""

    @staticmethod
    def markdown_to_confluence(md_text: str) -> str:
        """Convert Markdown to Confluence storage format with TOC"""
        lines = md_text.split('\n')
        html = []
        in_code = False
        in_list = False
        list_type = None
        headers = []

        # First pass: collect headers for TOC
        for line in lines:
            if line.startswith('#') and not line.startswith('```'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                if 1 <= level <= 3:  # Only H1-H3 in TOC
                    headers.append((level, title))

        # Add TOC if there are headers
        if len(headers) > 2:
            html.append('<ac:structured-macro ac:name="toc">')
            html.append('<ac:parameter ac:name="maxLevel">3</ac:parameter>')
            html.append('</ac:structured-macro>')
            html.append('')

        # Second pass: convert content
        for line in lines:
            # Code blocks with proper macro
            if line.startswith('```'):
                if not in_code:
                    lang = line[3:].strip() or 'none'
                    html.append(
                        f'<ac:structured-macro ac:name="code">'
                        f'<ac:parameter ac:name="language">{lang}</ac:parameter>'
                        f'<ac:plain-text-body><![CDATA['
                    )
                    in_code = True
                else:
                    html.append(']]></ac:plain-text-body></ac:structured-macro>')
                    in_code = False
                continue

            if in_code:
                html.append(line)
                continue

            # Close lists when needed
            if in_list and not (line.startswith(('- ', '* ')) or (line and line[0].isdigit())):
                html.append(f'</{list_type}>')
                in_list = False
                list_type = None

            # Headers
            if line.startswith('#### '):
                html.append(f'<h4>{line[5:]}</h4>')
            elif line.startswith('### '):
                html.append(f'<h3>{line[4:]}</h3>')
            elif line.startswith('## '):
                html.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('# '):
                html.append(f'<h1>{line[2:]}</h1>')
            # Lists
            elif line.startswith(('- ', '* ')):
                if not in_list or list_type != 'ul':
                    if in_list:
                        html.append(f'</{list_type}>')
                    html.append('<ul>')
                    in_list = True
                    list_type = 'ul'
                html.append(f'<li>{line[2:]}</li>')
            elif line.strip() and line[0].isdigit() and '. ' in line:
                if not in_list or list_type != 'ol':
                    if in_list:
                        html.append(f'</{list_type}>')
                    html.append('<ol>')
                    in_list = True
                    list_type = 'ol'
                html.append(f'<li>{line.split(". ", 1)[1]}</li>')
            # Regular content
            elif line.strip():
                # Handle bold
                if '**' in line:
                    parts = line.split('**')
                    result = []
                    for i, part in enumerate(parts):
                        result.append(f'<strong>{part}</strong>' if i % 2 == 1 else part)
                    line = ''.join(result)
                html.append(f'<p>{line}</p>')
            else:
                html.append('')

        if in_list:
            html.append(f'</{list_type}>')

        return '\n'.join(html)


# ============================================================================
# API Client Layer
# ============================================================================

class ConfluenceAPI:
    """Low-level Confluence REST API client"""

    def __init__(self, base_url: str, auth: AuthProvider):
        self.base_url = base_url
        self.auth = auth

    def create_page(self, space_key: str, title: str, content: str) -> Dict[str, Any]:
        """Create a page"""
        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }

        try:
            session = self.auth.get_session()
            response = session.post(
                f'{self.base_url}/rest/api/content',
                json=payload,
                timeout=TIMEOUT_CREATE
            )

            if response.status_code in [200, 201]:
                page = response.json()
                return {
                    'success': True,
                    'id': page['id'],
                    'title': page['title'],
                    'url': f"{self.base_url}{page['_links']['webui']}"
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text[:200]}"
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def search_pages(self, query: str, space_key: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Search for pages"""
        try:
            session = self.auth.get_session()

            # Build CQL query
            cql = f'type=page AND text~"{query}"'
            if space_key:
                cql += f' AND space={space_key}'

            params = {
                'cql': cql,
                'limit': limit,
                'expand': 'space'
            }

            response = session.get(
                f'{self.base_url}/rest/api/content/search',
                params=params,
                timeout=TIMEOUT_SEARCH
            )

            if response.status_code == 200:
                data = response.json()
                results = []
                for page in data.get('results', []):
                    results.append({
                        'id': page['id'],
                        'title': page['title'],
                        'space': page['space']['key'],
                        'url': f"{self.base_url}{page['_links']['webui']}"
                    })
                return {
                    'success': True,
                    'count': len(results),
                    'results': results
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}


# ============================================================================
# High-Level Service Layer
# ============================================================================

class ConfluenceService:
    """High-level Confluence operations"""

    def __init__(self, api: ConfluenceAPI, converter: ContentConverter):
        self.api = api
        self.converter = converter

    def create_page_from_markdown(self, space_key: str, title: str, md_file: Path) -> Dict[str, Any]:
        """Create page from markdown file"""
        if not md_file.exists():
            return {'success': False, 'error': f'File not found: {md_file}'}

        with open(md_file) as f:
            md_content = f.read()

        html_content = self.converter.markdown_to_confluence(md_content)
        return self.api.create_page(space_key, title, html_content)

    def create_simple_page(self, space_key: str, title: str) -> Dict[str, Any]:
        """Create simple page with default content"""
        content = f"<h1>{title}</h1><p>Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
        return self.api.create_page(space_key, title, content)

    def search(self, query: str, space_key: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Search for pages"""
        return self.api.search_pages(query, space_key, limit)


# ============================================================================
# CLI Layer
# ============================================================================

class CLI:
    """Command-line interface"""

    def __init__(self, service: ConfluenceService, auth: AuthProvider):
        self.service = service
        self.auth = auth

    def run(self, args: list):
        """Run CLI command"""
        if len(args) < 2:
            self._print_usage()
            sys.exit(1)

        command = args[1]

        if command == 'create':
            self._handle_create(args[2:])
        elif command == 'search':
            self._handle_search(args[2:])
        else:
            self._print_usage()
            sys.exit(1)

    def _handle_create(self, args: list):
        """Handle create command"""
        if len(args) < 2:
            print("Usage: confluence.py create <space> <title> [file]")
            sys.exit(1)

        space = args[0]
        title = args[1]
        md_file = Path(args[2]) if len(args) > 2 else None

        # Ensure authenticated
        print("🔐 Checking authentication...")
        if not self._ensure_auth():
            sys.exit(1)

        print(f"📝 Creating page '{title}' in {space}...")

        # Create page
        if md_file:
            result = self.service.create_page_from_markdown(space, title, md_file)
        else:
            result = self.service.create_simple_page(space, title)

        self._print_result(result)

    def _handle_search(self, args: list):
        """Handle search command"""
        if len(args) < 1:
            print("Usage: confluence.py search <query> [space] [limit]")
            sys.exit(1)

        query = args[0]
        space = args[1] if len(args) > 1 else None
        limit = int(args[2]) if len(args) > 2 else 10

        # Ensure authenticated
        print("🔍 Searching...")
        if not self._ensure_auth():
            sys.exit(1)

        result = self.service.search(query, space, limit)

        if result['success']:
            if result['count'] == 0:
                print(f"\n❌ No pages found for '{query}'")
            else:
                print(f"\n✅ Found {result['count']} page(s):\n")
                for page in result['results']:
                    print(f"  [{page['space']}] {page['title']}")
                    print(f"  → {page['url']}\n")
        else:
            print(f"\n❌ Search failed: {result['error']}")
            sys.exit(1)

    def _ensure_auth(self) -> bool:
        """Ensure authentication is valid"""
        if self.auth.is_valid():
            return True

        print("⚠️  Session expired, refreshing...")
        if self.auth.refresh():
            print("✅ Authentication successful!\n")
            return True
        else:
            print("❌ Authentication failed")
            return False

    def _print_result(self, result: Dict[str, Any]):
        """Print operation result"""
        if result['success']:
            print(f"\n✅ SUCCESS!")
            print(f"   {result['url']}\n")
        else:
            print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}\n")
            sys.exit(1)

    def _print_usage(self):
        """Print usage information"""
        print("""
Confluence Automation
====================

Usage:
    python confluence.py create <space> <title> [file]
    python confluence.py search <query> [space] [limit]

Commands:
    create   - Create a new page
    search   - Search for pages

Examples:
    python confluence.py create BI "API Docs" README.md
    python confluence.py create BI "Quick Note"
    python confluence.py search "authentication" BI
    python confluence.py search "API" BI 20
""")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Application entry point"""
    # Dependency injection
    auth = SessionCookieAuth(BASE_URL, SESSION_FILE)
    converter = ContentConverter()
    api = ConfluenceAPI(BASE_URL, auth)
    service = ConfluenceService(api, converter)
    cli = CLI(service, auth)

    # Run CLI
    cli.run(sys.argv)


if __name__ == "__main__":
    main()
