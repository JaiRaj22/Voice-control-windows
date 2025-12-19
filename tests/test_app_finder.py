import pytest
from unittest.mock import patch, MagicMock
import os
import sys
from src.app_finder import AppFinder

@patch('sys.platform', 'win32')
@patch('os.environ.get')
@patch('os.path.isdir')
@patch('os.walk')
def test_discover_apps_windows(mock_walk, mock_isdir, mock_environ_get):
    """
    Test that the AppFinder discovers applications correctly on Windows.
    """
    # Arrange
    user_profile = "C:\\Users\\TestUser"
    app_data = "C:\\Users\\TestUser\\AppData\\Roaming"
    program_data = "C:\\ProgramData"
    public = "C:\\Users\\Public"

    mock_environ_get.side_effect = lambda key, default="": {
        "USERPROFILE": user_profile,
        "APPDATA": app_data,
        "PROGRAMDATA": program_data,
        "PUBLIC": public
    }.get(key, default)
    mock_isdir.return_value = True

    # Mock the file system structure for all expected paths
    desktop_path = os.path.join(user_profile, "Desktop")
    public_desktop_path = os.path.join(public, "Desktop")
    start_menu_path = os.path.join(app_data, "Microsoft", "Windows", "Start Menu", "Programs")
    public_start_menu_path = os.path.join(program_data, "Microsoft", "Windows", "Start Menu", "Programs")

    walk_data = {
        desktop_path: [(desktop_path, [], ["Chrome.lnk", "Spotify.exe"])],
        public_desktop_path: [],
        start_menu_path: [(start_menu_path, [], ["Word.lnk"])],
        public_start_menu_path: [(public_start_menu_path, [], ["Excel.exe"])],
    }
    mock_walk.side_effect = lambda path: walk_data.get(path, [])

    # Act
    finder = AppFinder()

    # Assert
    assert len(finder.app_map) == 4
    assert finder.app_map["chrome"] == os.path.join(desktop_path, "Chrome.lnk")
    assert finder.app_map["word"] == os.path.join(start_menu_path, "Word.lnk")
    assert finder.find_app("spotify") is not None

@patch('sys.platform', 'linux')
def test_discover_apps_linux(caplog):
    """
    Test that the AppFinder handles non-Windows platforms gracefully.
    """
    # Act
    finder = AppFinder()

    # Assert
    assert len(finder.app_map) == 0
    assert "Could not find standard application directories" in caplog.text

def test_find_app_exact_match():
    finder = AppFinder()
    finder.app_map = {"chrome": "path/to/chrome.exe"}
    assert finder.find_app("chrome") == "path/to/chrome.exe"

def test_find_app_partial_match():
    finder = AppFinder()
    finder.app_map = {"google chrome": "path/to/google_chrome.exe"}
    assert finder.find_app("chrome") == "path/to/google_chrome.exe"

def test_find_app_no_match():
    finder = AppFinder()
    finder.app_map = {"firefox": "path/to/firefox.exe"}
    assert finder.find_app("chrome") is None
