import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from unittest import mock


def test_open_command_macos():
    with mock.patch('platform.system', return_value='Darwin'):
        import refresh_cookies
        import importlib
        importlib.reload(refresh_cookies)
        assert refresh_cookies.get_open_command() == 'open'


def test_open_command_linux():
    with mock.patch('platform.system', return_value='Linux'):
        import refresh_cookies
        import importlib
        importlib.reload(refresh_cookies)
        assert refresh_cookies.get_open_command() == 'xdg-open'


def test_open_command_windows():
    with mock.patch('platform.system', return_value='Windows'):
        import refresh_cookies
        import importlib
        importlib.reload(refresh_cookies)
        assert refresh_cookies.get_open_command() == 'start'
