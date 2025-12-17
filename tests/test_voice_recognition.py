import pytest
from unittest.mock import patch, MagicMock
import speech_recognition as sr
from src.voice_recognition import VoiceRecognizer

@patch('speech_recognition.Microphone')
@patch('speech_recognition.Recognizer')
def test_listen_for_command_detected(mock_recognizer_class, mock_microphone_class):
    """
    Test that a command is correctly detected and extracted.
    """
    # Arrange
    mock_recognizer_instance = MagicMock()
    mock_recognizer_instance.recognize_google.return_value = "hey system open chrome"
    mock_recognizer_class.return_value = mock_recognizer_instance

    recognizer = VoiceRecognizer()

    # Act
    command = recognizer.listen_for_command("hey system")

    # Assert
    assert command == "open chrome"
    mock_recognizer_instance.adjust_for_ambient_noise.assert_called_once()
    mock_recognizer_instance.listen.assert_called_once()
    mock_recognizer_instance.recognize_google.assert_called_once()

@patch('speech_recognition.Microphone')
@patch('speech_recognition.Recognizer')
def test_listen_for_command_no_wake_word(mock_recognizer_class, mock_microphone_class):
    """
    Test that a command is ignored if the wake word is not present.
    """
    # Arrange
    mock_recognizer_instance = MagicMock()
    mock_recognizer_instance.recognize_google.return_value = "open notepad"
    mock_recognizer_class.return_value = mock_recognizer_instance

    recognizer = VoiceRecognizer()

    # Act
    command = recognizer.listen_for_command("hey system")

    # Assert
    assert command is None

@patch('speech_recognition.Microphone')
@patch('speech_recognition.Recognizer')
def test_listen_for_command_unknown_value_error(mock_recognizer_class, mock_microphone_class):
    """
    Test that the system handles an UnknownValueError gracefully.
    """
    # Arrange
    mock_recognizer_instance = MagicMock()
    mock_recognizer_instance.recognize_google.side_effect = sr.UnknownValueError()
    mock_recognizer_class.return_value = mock_recognizer_instance

    recognizer = VoiceRecognizer()

    # Act
    command = recognizer.listen_for_command()

    # Assert
    assert command is None
