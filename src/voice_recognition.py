import speech_recognition as sr
import logging

class VoiceRecognizer:
    def __init__(self, logger=None):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.logger = logger or logging.getLogger(__name__)
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

    def listen_for_command(self, wake_word="hey windows"):
        with self.microphone as source:
            self.logger.info(f"Listening for command with wake word '{wake_word}'...")
            try:
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio)
                if text.lower().startswith(wake_word):
                    self.logger.info(f"Command recognized: {text}")
                    command = text[len(wake_word):].strip()
                    return command
            except sr.UnknownValueError:
                self.logger.warning("Could not understand audio")
            except sr.RequestError as e:
                self.logger.error(f"Could not request results; {e}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    recognizer = VoiceRecognizer(logger)
    command = recognizer.listen_for_command()
    if command:
        logger.info(f"You said: {command}")
