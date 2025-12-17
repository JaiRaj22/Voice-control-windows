import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
from functools import partial
import logging
from voice_recognition import VoiceRecognizer
from command_handler import CommandHandler

class ScrolledTextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.config(state='normal')
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.config(state='disabled')
        self.text_widget.see(tk.END)

class VoiceControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Control System")
        self.root.geometry("600x400")

        # Main frame
        main_frame = tk.Frame(root)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Log display
        log_label = tk.Label(main_frame, text="Real-time Log")
        log_label.pack(anchor=tk.W)

        self.log_display = scrolledtext.ScrolledText(main_frame, state='disabled', wrap=tk.WORD, height=15)
        self.log_display.pack(fill=tk.BOTH, expand=True)

        # Placeholder for application management
        app_management_frame = tk.LabelFrame(main_frame, text="Application Management")
        app_management_frame.pack(fill=tk.X, pady=10)

        placeholder_label = tk.Label(app_management_frame, text="Application configuration will be here.")
        placeholder_label.pack(padx=10, pady=10)

        # Set up logging
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Add the custom handler to the logger
        gui_handler = ScrolledTextHandler(self.log_display)
        gui_handler.setFormatter(formatter)
        self.logger.addHandler(gui_handler)

        self.logger.info("Application started. Initializing...")

        self.command_handler = CommandHandler(logger=self.logger)
        self.voice_recognizer = VoiceRecognizer(logger=self.logger)

        # Set up the shutdown command with the GUI confirmation
        self.command_handler.commands['shutdown'] = partial(
            self.command_handler.shutdown,
            confirmation_callback=lambda: self.show_confirmation_popup(
                "Shutdown Confirmation",
                "Are you sure you want to shut down?"
            )
        )
        self.command_handler.commands['restart'] = partial(
            self.command_handler.restart,
            confirmation_callback=lambda: self.show_confirmation_popup(
                "Restart Confirmation",
                "Are you sure you want to restart?"
            )
        )

        self.listener_thread = threading.Thread(target=self.start_listening, daemon=True)
        self.listener_thread.start()

    def start_listening(self):
        while True:
            command = self.voice_recognizer.listen_for_command()
            if command:
                self.command_handler.execute_command(command)

    def show_confirmation_popup(self, title, message):
        return messagebox.askyesno(title, message)

if __name__ == '__main__':
    root = tk.Tk()
    app = VoiceControlApp(root)
    root.mainloop()
