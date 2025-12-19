import pytest
from unittest.mock import patch, MagicMock
import sys
import importlib
import logging
from src.command_handler import CommandHandler

@pytest.fixture
def command_handler():
    """
    Pytest fixture to create a CommandHandler instance for testing.
    """
    with patch('src.command_handler.AppFinder'):
        handler = CommandHandler()
        yield handler

def test_open_application_success(command_handler):
    """
    Test that a known application can be opened.
    """
    command_handler.app_finder.find_app.return_value = "path/to/chrome.exe"
    # Patch os.startfile with create=True to avoid AttributeError on non-Windows systems
    with patch('os.startfile', create=True) as mock_startfile:
        command_handler.open_application("chrome")
        mock_startfile.assert_called_once_with("path/to/chrome.exe")

def test_open_application_not_found(command_handler, caplog):
    """
    Test that an unknown application is handled correctly.
    """
    command_handler.app_finder.find_app.return_value = None
    with caplog.at_level(logging.WARNING):
        command_handler.open_application("unknown_app")
    assert "Application 'unknown_app' not found." in caplog.text

def test_execute_command_open_application(command_handler):
    """
    Test that the 'open' command correctly triggers the open_application method.
    """
    with patch.object(command_handler, 'open_application') as mock_open:
        command_handler.execute_command("open chrome")
        mock_open.assert_called_once_with("chrome")

def test_volume_up_windows():
    """
    Test that the volume_up method increases the volume on Windows.
    """
    with patch('src.command_handler.CommandHandler._get_volume_interface') as mock_get_interface:
        mock_volume_interface = MagicMock()
        mock_volume_interface.GetMasterVolumeLevelScalar.return_value = 0.5
        mock_get_interface.return_value = mock_volume_interface

        handler = CommandHandler()
        handler.volume_up()

        mock_volume_interface.SetMasterVolumeLevelScalar.assert_called_with(0.6, None)

def test_volume_up_linux(caplog):
    """
    Test that volume control is not supported on Linux.
    """
    with patch('sys.platform', 'linux'):
        handler = CommandHandler()
        handler.volume_up()
    assert "Volume control is not supported on this OS." in caplog.text

@patch('os.system')
def test_shutdown_command(mock_os_system, command_handler):
    """
    Test that the shutdown command calls os.system with the correct arguments.
    """
    command_handler.shutdown(confirmation_callback=lambda: True)
    mock_os_system.assert_called_once_with("shutdown /s /t 1")

@patch('os.system')
def test_sleep_command(mock_os_system, command_handler):
    """
    Test that the sleep command calls os.system with the correct arguments.
    """
    command_handler.sleep()
    mock_os_system.assert_called_once_with("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def test_execute_command_unknown_command(command_handler):
    """
    Test that an unknown command does not trigger any action.
    """
    with patch.object(command_handler, 'open_application') as mock_open, \
         patch.object(command_handler, 'volume_up') as mock_volume_up:
        command_handler.execute_command("some unknown command")
        mock_open.assert_not_called()
        mock_volume_up.assert_not_called()

def test_execute_command_empty_input(command_handler):
    """
    Test that empty input is handled gracefully.
    """
    with patch.object(command_handler, 'open_application') as mock_open:
        command_handler.execute_command("")
        mock_open.assert_not_called()
