import os
import subprocess
import sys
import logging

class CommandHandler:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.commands = {
            "open": "open_application",
            "volume up": "volume_up",
            "volume down": "volume_down",
            "mute": "mute_volume",
            "shutdown": "shutdown",
            "restart": "restart",
            "sleep": "sleep",
        }
        self.app_paths = {
            "firefox": r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            "visual studio": r"D:\Microsoft VS Code\Code.exe",
        }

        self._volume_interface = self._get_volume_interface()

    def _get_volume_interface(self):
        if sys.platform == "win32":
            try:
                from pycaw.pycaw import AudioUtilities
                speakers = AudioUtilities.GetSpeakers()
                return speakers.EndpointVolume
            except Exception as e:
                self.logger.error(f"Failed to initialize volume control: {e}")
                return None
        return None

    def execute_command(self, command_text):
        if not command_text:
            return

        command_text = command_text.lower()
        # Remove common wake words like 'hey windows' or leading 'hey'
        if command_text.startswith("hey windows"):
            command_text = command_text[len("hey windows"):].strip()
        elif command_text.startswith("hey, windows"):
            command_text = command_text[len("hey, windows"):].strip()
        elif command_text.startswith("hey "):
            command_text = command_text[len("hey "):].strip()

        for keyword, action in self.commands.items():
            if command_text.startswith(keyword):
                if isinstance(action, str):
                    method = getattr(self, action)
                else:
                    method = action

                if keyword == "open":
                    app_name = command_text[len(keyword):].strip()
                    method(app_name)
                else:
                    method()
                return

    def open_application(self, app_name):
        if app_name in self.app_paths:
            try:
                subprocess.Popen(self.app_paths[app_name])
                self.logger.info(f"Opening {app_name}")
            except FileNotFoundError:
                self.logger.error(f"Could not find {app_name}")
        else:
            self.logger.warning(f"Application '{app_name}' not found.")

    def volume_up(self):
        if not self._volume_interface:
            self.logger.warning("Volume control is not supported on this OS.")
            return
        current_volume = self._volume_interface.GetMasterVolumeLevelScalar()
        new_volume = min(1.0, current_volume + 0.1)
        self._volume_interface.SetMasterVolumeLevelScalar(new_volume, None)
        self.logger.info(f"Volume set to {new_volume * 100:.0f}%")

    def volume_down(self):
        if not self._volume_interface:
            self.logger.warning("Volume control is not supported on this OS.")
            return
        current_volume = self._volume_interface.GetMasterVolumeLevelScalar()
        new_volume = max(0.0, current_volume - 0.1)
        self._volume_interface.SetMasterVolumeLevelScalar(new_volume, None)
        self.logger.info(f"Volume set to {new_volume * 100:.0f}%")

    def mute_volume(self):
        if not self._volume_interface:
            self.logger.warning("Volume control is not supported on this OS.")
            return
        self._volume_interface.SetMute(not self._volume_interface.GetMute(), None)
        self.logger.info("Mute toggled")

    def shutdown(self, confirmation_callback=None):
        if confirmation_callback and not confirmation_callback():
            self.logger.info("Shutdown cancelled.")
            return

        self.logger.info("Shutting down...")
        os.system("shutdown /s /t 1")

    def restart(self, confirmation_callback=None):
        if confirmation_callback and not confirmation_callback():
            self.logger.info("Restart cancelled.")
            return

        self.logger.info("Restarting...")
        os.system("shutdown /r /t 1")

    def sleep(self, confirmation_callback=None):
        """Put the system to sleep (cross-platform best-effort).

        If a confirmation_callback is provided and returns False, the action is cancelled.
        """
        if confirmation_callback and not confirmation_callback():
            self.logger.info("Sleep cancelled.")
            return

        self.logger.info("Sleeping...")
        try:
            if sys.platform == "win32":
                # Best-effort Windows sleep command
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            elif sys.platform.startswith("linux"):
                os.system("systemctl suspend")
            elif sys.platform == "darwin":
                os.system("pmset sleepnow")
            else:
                self.logger.warning("Sleep is not supported on this OS.")
        except Exception as e:
            self.logger.error(f"Failed to put system to sleep: {e}")