import sys
import speech_recognition as sr
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QScrollArea, QStackedWidget, QToolBar, QAction, QMenu, 
    QComboBox, QSlider, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor
from basic import speak, take_voice_input, take_text_input, show_date_time, get_weather, system_info, open_file, take_screenshot, web_search, send_email, set_reminder, check_reminders, add_task, show_tasks, clear_tasks, open_notepad, save_note, control_media, add_shortcut, execute_shortcut, open_quick_access, get_meaning
from advanced import BruceAdvanced
import webbrowser
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QUrl    
from PyQt5.QtGui import QBrush, QPalette, QPixmap
from PyQt5.QtCore import Qt


class BruceAssistantUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.advanced_assistant = BruceAdvanced(gui_callback=self.displayResponse)
        self.current_mode = "Basic"

    def initUI(self):
        # Main Window Configuration
        self.setWindowTitle("Bruce - Your Virtual Assistant")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            background-color: #f0f0f0;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
        """)

        # Header Section
        header = QWidget(self)
        header.setStyleSheet("""
            background-color: #0078d4;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        header_layout = QHBoxLayout()

        logo = QLabel()
        logo_pixmap = QPixmap('background.').scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(logo_pixmap)
        logo.setFixedSize(40, 40)

        title = QLabel("Bruce - Your Virtual Assistant")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            margin-left: 10px;
        """)

        mode_toggle = QComboBox()
        mode_toggle.addItems(["Basic Mode", "Advanced Mode"])
        mode_toggle.setStyleSheet("""
            background-color: black;
            padding: 5px;
            border-radius: 5px;
            font-size: 14px;
        """)
        mode_toggle.currentTextChanged.connect(self.switchMode)

        header_layout.addWidget(logo)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(mode_toggle)
        header.setLayout(header_layout)

        # Left Panel for Quick Access Buttons
        left_panel = QWidget()
        left_panel.setStyleSheet("""
            background-color: #e3e3e3;
            padding: 10px;
            border-radius: 5px;
        """)
        left_panel_layout = QVBoxLayout()

        quick_access_buttons = {
            "Tasks": self.show_tasks,
            "Reminders": self.check_reminders,
            "Notes": self.open_notepad,
        }
        for btn_text, callback in quick_access_buttons.items():
            button = QPushButton(btn_text)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 14px;
                    margin: 5px;
                }
                QPushButton:hover {
                    background-color: #005bb5;
                }
            """)
            button.clicked.connect(callback)
            left_panel_layout.addWidget(button)

        left_panel_layout.addStretch()
        left_panel.setLayout(left_panel_layout)

        # Input Area
        input_area = QWidget()
        input_layout = QHBoxLayout(input_area)

        # Create a background label
        background = QLabel(input_area)
        background.setScaledContents(True)
        try:
            pixmap = QPixmap("bg.png")
            if not pixmap.isNull():
                background.setPixmap(pixmap)
            else:
                print("Warning: Background image not loaded properly")
        except Exception as e:
            print(f"Error loading background image: {e}")

        background.lower()

        # Input Box
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type your command here...")
        self.input_box.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #0078d4;
                border-radius: 10px;
                font-size: 16px;
                color: black;
                background-color: white;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 2px solid #005bb5;
            }
        """)

        # Microphone Button with SVG support
        mic_button = QPushButton()
        try:
            # Using QSvgRenderer for proper SVG support
            from PyQt5.QtSvg import QSvgRenderer
            from PyQt5.QtGui import QPainter
            
            renderer = QSvgRenderer("mic_icon.svg")
            if renderer.isValid():
                # Create a pixmap from the SVG
                svg_pixmap = QPixmap(24, 24)
                svg_pixmap.fill(Qt.transparent)
                painter = QPainter(svg_pixmap)
                renderer.render(painter)
                painter.end()
                mic_button.setIcon(QIcon(svg_pixmap))
            else:
                raise Exception("Invalid SVG file")
        except Exception as e:
            print(f"Error loading SVG icon: {e}")
            # Fallback to text if SVG fails
            mic_button.setText("🎤")

        mic_button.setIconSize(QSize(24, 24))
        mic_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(64, 163, 238);
                border-radius: 20px;
                padding: 10px;
                min-width: 40px;
                min-height: 40px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgb(64, 144, 224);
            }
        """)
        mic_button.clicked.connect(self.handleVoiceInput)

        # Submit Button
        submit_button = QPushButton("Submit")
        submit_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                padding: 10px 15px;
                border-radius: 10px;
                font-size: 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
        """)
        submit_button.clicked.connect(self.handleTextInput)

        # Add Widgets to Layout
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(mic_button)
        input_layout.addWidget(submit_button)

        # Ensure the background resizes with the widget
        def resizeEvent(event):
            background.setGeometry(0, 0, input_area.width(), input_area.height())
            QWidget.resizeEvent(input_area, event)
            
        input_area.resizeEvent = resizeEvent
        # Right Panel for Conversation History
        right_panel = QScrollArea()
        right_panel.setStyleSheet("""
            background-color: white;
            border: 1px solid #cccccc;
            border-radius: 5px;
        """)
        right_panel.setWidgetResizable(True)

        self.history_widget = QWidget()
        self.history_layout = QVBoxLayout()
        self.history_widget.setLayout(self.history_layout)

        history_title = QLabel("Conversation History")
        history_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            margin: 10px;
        """)
        self.history_layout.addWidget(history_title)

        right_panel.setWidget(self.history_widget)

        # Footer Section
        footer = QWidget(self)
        footer.setStyleSheet("""
            background-color: #0078d4;
            color: white;
            padding: 5px;
            border-radius: 5px;
        """)
        footer_layout = QHBoxLayout()

        footer_buttons = {
            "About": self.show_about,
            "Settings": self.open_settings,
            "Help": self.show_help,
            "Exit": self.close,
        }
        for btn_text, callback in footer_buttons.items():
            button = QPushButton(btn_text)
            button.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #0078d4;
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-size: 14px;
                    margin: 0 5px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)
            button.clicked.connect(callback)
            footer_layout.addWidget(button)

        footer_status = QLabel("Status: Connected")
        footer_status.setStyleSheet("""
            margin-left: auto;
            margin-right: 10px;
            font-size: 14px;
        """)
        self.footer_status = footer_status

        footer_layout.addWidget(footer_status)
        footer.setLayout(footer_layout)

        # Main Layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
 
        content_layout = QHBoxLayout()
        content_layout.addWidget(left_panel, 1)
        content_layout.addWidget(input_area, 4)
        content_layout.addWidget(right_panel, 2)

        main_layout.addWidget(header)
        main_layout.addLayout(content_layout)
        main_layout.addWidget(footer)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def handleTextInput(self):
        user_input = self.input_box.text()
        if user_input:
            self.displayResponse(f"User: {user_input}")
            try:
                if self.current_mode == "Basic":
                    self.process_basic_command(user_input)
                else:
                    self.advanced_assistant.process_command(user_input)
            except Exception as e:
                self.displayResponse(f"Error: {str(e)}")
            self.input_box.clear()

    def handleVoiceInput(self):
        try:
            self.displayResponse("Listening for voice input...")
            user_input = take_voice_input()
            if user_input:
                self.displayResponse(f"User: {user_input}")
                if self.current_mode == "Basic":
                    self.process_basic_command(user_input)
                else:
                    self.advanced_assistant.process_command(user_input)
        except Exception as e:
            self.displayResponse(f"Error: {str(e)}")

    def process_basic_command(self, command):
        if "time" in command or "date" in command:
            self.displayResponse(show_date_time())
        elif "weather" in command:
            self.displayResponse(get_weather())
        elif "system info" in command or "battery" in command:
            self.displayResponse(system_info())
        elif "open file" in command:
            self.displayResponse(open_file(command))
        elif "screenshot" in command:
            self.displayResponse(take_screenshot())
        elif "search" in command:
            self.displayRespons (web_search())
        elif "email" in command:
            self.displayResponse(send_email())
        elif "reminder" in command.lower():  # Case-insensitive matching
            command_lower = command.lower()  # Convert command to lowercase for easier processing
            
            if "add" in command_lower:
                # Extract the reminder text after "add reminder"
                reminder_text = command.split("add reminder", 1)[-1].strip()
                print(f"Debug: Extracted reminder text: {reminder_text}")  # Debug statement
                
                if reminder_text:
                    self.displayResponse(set_reminder(reminder_text))  # Pass the reminder text to set_reminder
                else:
                    self.displayResponse("No reminder provided. Please specify a reminder.")
            
            elif "check" in command_lower or "give" in command_lower:  # Dedicated check for "check" or "give"
                print("Debug: Checking reminders...")  # Debug statement
                self.displayResponse(check_reminders())
            
            else:
                # Provide more specific feedback for invalid commands
                self.displayResponse("Invalid command. Please say 'add reminder <your reminder>' or 'check reminders'.")
        elif "task" in command:
            if "add task" in command:
                self.displayResponse(add_task(command))
            elif "show" in command:
                self.displayResponse(show_tasks())
            elif "clear" in command:
                self.displayResponse(clear_tasks())
        elif "notepad" in command:
            self.displayResponse(open_notepad())
        elif "save note" in command:
            self.displayResponse(save_note(command))
        elif "play" in command or "pause" in command or "next" in command or "previous" in command or "volume" in command or "stop" in command:
            self.displayResponse(control_media(command))
        elif "shortcut" in command:
            if "add shortcut" in command:
                self.displayResponse(add_shortcut(command))
            elif "execute shortcut" in command:
                self.displayResponse(execute_shortcut(command))
            else:
                self.displayResponse("Invalid shortcut command. Please say 'add shortcut <name> path <path>' or 'execute shortcut <name>'.")
        elif "open" in command:
            self.displayResponse(open_quick_access(command))   
        elif "meaning" in command:
            self.displayResponse(get_meaning(command))
        elif "exit" in command or "quit" in command:
            self.close()
        else:
            self.displayResponse("Command not recognized.")

    def displayResponse(self, message):
        if message is None:
            message = "No response received."
        label = QLabel(message)
        label.setStyleSheet("""
            background-color: #e1f5fe;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 5px;
        """)
        self.history_layout.addWidget(label)
        self.history_widget.adjustSize()

        # Update Footer Status
        if "error" in message.lower() or "offline" in message.lower():
            self.footer_status.setText("Status: Offline")
        else:
            self.footer_status.setText("Status: Connected")

    def switchMode(self, mode):
        self.current_mode = "Basic" if mode == "Basic Mode" else "Advanced"
        self.displayResponse(f"Switched to {mode}")

    # Quick Access Functions
    def show_tasks(self):
        self.displayResponse(show_tasks())

    def check_reminders(self):
        self.displayResponse(check_reminders())

    def open_notepad(self):
        self.displayResponse(open_notepad())

    # Footer Functions
    def show_about(self):
        QMessageBox.about(
            self,
            "About Bruce",
            "Bruce - Your Virtual Assistant\n\n"
            "Version: 1.0\n"
            "Developed By: [BATCH 13 CSE]\n\n"
            "Bruce is designed to simplify your daily tasks with advanced speech recognition "
            "and natural language processing capabilities. Whether it's managing files, setting reminders, "
            "or answering complex queries, Bruce has you covered.\n\n"
            "For feedback or inquiries, contact: support@bruceassistant.com"
        )

    def open_settings(self):
        self.displayResponse("Opening settings...")

    def show_help(self):
        help_file_path = r"C:\Users\vutla\Downloads\Building Bruce\help.html"

        # Create a new window for the help content
        help_window = QMainWindow(self)
        help_window.setWindowTitle("Help - Bruce Assistant")
        help_window.setGeometry(150, 150, 800, 600)

        # Add QWebEngineView to display the HTML content
        web_view = QWebEngineView()
        web_view.load(QUrl.fromLocalFile(help_file_path))
        help_window.setCentralWidget(web_view)

        # Show the help window
        help_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BruceAssistantUI()
    window.show()
    sys.exit(app.exec_())