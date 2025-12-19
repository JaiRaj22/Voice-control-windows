import pytest
from unittest.mock import patch, MagicMock
import tkinter as tk
from src.main_app import VoiceControlApp
from speech_recognition import AudioSource

@pytest.fixture
def app():
    """
    Pytest fixture to create a VoiceControlApp instance for testing.
    This fixture patches the GUI and the listener thread to avoid starting them.
    """
    with patch('tkinter.Tk') as mock_tk, \
         patch('threading.Thread'), \
         patch('speech_recognition.Microphone') as mock_microphone:
        # Configure the mock to return a valid AudioSource object with all required attributes
        mock_audio_source = MagicMock(spec=AudioSource)
        mock_audio_source.stream = MagicMock()
        mock_audio_source.stream.read.return_value = b''  # Return bytes
        mock_audio_source.CHUNK = 1024
        mock_audio_source.SAMPLE_RATE = 44100
        mock_audio_source.SAMPLE_WIDTH = 2
        mock_microphone.return_value.__enter__.return_value = mock_audio_source
        root = mock_tk()
        app = VoiceControlApp(root)
        yield app

def test_app_initialization(app):
    """
    Test that the application initializes correctly.
    """
    app.root.title.assert_called_once_with("Voice Control System")
    app.listener_thread.start.assert_called_once()

@patch('src.main_app.VoiceControlApp.show_confirmation_popup', return_value=True)
def test_shutdown_command_with_confirmation(mock_popup, app):
    """
    Test that the shutdown command triggers the confirmation dialog and proceeds if confirmed.
    """
    with patch('os.system') as mock_os_system:
        app.command_handler.execute_command("shutdown")
        mock_popup.assert_called_once_with("Shutdown Confirmation", "Are you sure you want to shut down?")

@patch('src.main_app.VoiceControlApp.show_confirmation_popup', return_value=False)
def test_shutdown_command_without_confirmation(mock_popup, app):
    """
    Test that the shutdown command is cancelled if not confirmed.
    """
    with patch('os.system') as mock_os_system:
        app.command_handler.execute_command("shutdown")
        mock_popup.assert_called_once_with("Shutdown Confirmation", "Are you sure you want to shut down?")
        mock_os_system.assert_not_called()

@patch('src.main_app.VoiceControlApp.show_confirmation_popup', return_value=True)
def test_restart_command_with_confirmation(mock_popup, app):
    """
    Test that the restart command triggers the confirmation dialog and proceeds if confirmed.
    """
    with patch('os.system') as mock_os_system:
        app.command_handler.execute_command("restart")
        mock_popup.assert_called_once_with("Restart Confirmation", "Are you sure you want to restart?")

@patch('src.main_app.VoiceControlApp.show_confirmation_popup', return_value=False)
def test_restart_command_without_confirmation(mock_popup, app):
    """
    Test that the restart command is cancelled if not confirmed.
    """
    with patch('os.system') as mock_os_system:
        app.command_handler.execute_command("restart")
        mock_popup.assert_called_once_with("Restart Confirmation", "Are you sure you want to restart?")
        mock_os_system.assert_not_called()

def test_listening_loop_command_execution(app):
    """
    Test that a recognized command is executed in the listening loop.
    """
    # Make the listening loop run only once
    with patch.object(app.voice_recognizer, 'listen_for_command', side_effect=["open chrome", SystemExit]), \
         patch.object(app.command_handler, 'execute_command') as mock_execute:
        with pytest.raises(SystemExit):
            app.start_listening()
        mock_execute.assert_called_once_with("open chrome")
