import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest import mock


def test_cloud_url_detected(monkeypatch):
    import config
    monkeypatch.setattr(config, 'BASE_URL', 'https://myorg.atlassian.net/wiki')
    import confluence_page
    import importlib
    importlib.reload(confluence_page)
    assert confluence_page.is_cloud_instance() is True


def test_server_url_not_cloud(monkeypatch):
    import config
    monkeypatch.setattr(config, 'BASE_URL', 'https://confluence.mycompany.com')
    import confluence_page
    import importlib
    importlib.reload(confluence_page)
    assert confluence_page.is_cloud_instance() is False


def test_cloud_blocks_cookie_auth(monkeypatch):
    import config
    monkeypatch.setattr(config, 'BASE_URL', 'https://myorg.atlassian.net/wiki')
    import confluence_page
    import importlib
    importlib.reload(confluence_page)
    with pytest.raises(SystemExit):
        confluence_page.load_cookies()


def test_auth_hint_no_zshrc(monkeypatch):
    import config
    monkeypatch.setattr(config, 'BASE_URL', 'https://confluence.mycompany.com')
    import confluence_page
    import importlib
    importlib.reload(confluence_page)
    monkeypatch.delenv('CONFLUENCE_TOKEN', raising=False)
    hint = confluence_page._auth_hint()
    assert '~/.zshrc' not in hint
