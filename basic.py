import os
import time
import datetime
import pyttsx3
import speech_recognition as sr
import webbrowser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import psutil
from tkinter import Tk, simpledialog
import subprocess
from PIL import ImageGrab
import pyautogui
import json
import pygame
from PyDictionary import PyDictionary
import sqlite3
from PyQt5.QtWidgets import QApplication, QInputDialog, QFileDialog  # Add PyQt5 imports

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def take_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
            return None
        except sr.RequestError:
            speak("Error with the recognition service.")
            return None

def take_text_input():
    return input("Enter your command: ").strip().lower()

# Global variable to store input method
input_method = None

def take_command():
    """Get command based on selected input method."""
    if input_method == "voice":
        return take_voice_input()
    elif input_method == "text":
        return take_text_input()
    else:
        return None

def choose_input_method():
    global input_method
    speak("Would you like to use voice input or text input?")
    print("Choose your input method: (voice/text)")
    while True:
        method = input("Enter 'voice' or 'text': ").strip().lower()
        if method in ("voice", "text"):
            input_method = method
            speak(f"You have selected {input_method} input for this session.")
            break
        else:
            print("Invalid choice. Please type 'voice' or 'text'.")
            speak("Invalid choice. Please choose again.")

# Call this function at the beginning of the session


# Media Control

# Initialize Pygame mixer
pygame.mixer.init()

# Global variables for song list and current song index
songs_folder = r"C:\Users\vutla\Music\re"  # Replace with your songs folder path
song_list = [f for f in os.listdir(songs_folder) if f.endswith(('.mp3', '.wav'))]
current_song_index = 0

def play_song(index):
    """Play the song at the given index."""
    global current_song_index
    if 0 <= index < len(song_list):
        current_song_index = index
        song_path = os.path.join(songs_folder, song_list[current_song_index])
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        speak(f"Playing {song_list[current_song_index]}")
    else:
        speak("No songs available to play.")

def control_media(command):
    global current_song_index
    if "play song" in command:
        play_song(current_song_index)
        return f"Playing {song_list[current_song_index]}"
    elif "pause" in command:
        pygame.mixer.music.pause()
        return "Music paused."
    elif "resume" in command:
        pygame.mixer.music.unpause()
        return "Music resumed."
    elif "next" in command:
        current_song_index = (current_song_index + 1) % len(song_list)
        play_song(current_song_index)
        return f"Playing next song: {song_list[current_song_index]}"
    elif "previous" in command:
        current_song_index = (current_song_index - 1) % len(song_list)
        play_song(current_song_index)
        return f"Playing previous song: {song_list[current_song_index]}"
    elif "volume up" in command:
        volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(min(volume + 0.1, 1.0))
        return "Volume increased."
    elif "volume down" in command:
        volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(max(volume - 0.1, 0.0))
        return "Volume decreased."
    elif "stop" in command:
        pygame.mixer.music.stop()
        return "Music stopped."
    else:
        return "Media command not recognized."

# Reminders
def set_reminder(reminder_text):
    if reminder_text:
        conn = sqlite3.connect('bruce.db')
        cursor = conn.cursor()
        
        # Insert the reminder text and a dummy time value (e.g., 0)
        cursor.execute('INSERT INTO reminders (text, time) VALUES (?, ?)', (reminder_text, 0))
        conn.commit()
        conn.close()
        
        message = f"Reminder added: {reminder_text}"
        speak(message)
        return message
    return "No reminder provided."

def check_reminders():
    conn = sqlite3.connect('bruce.db')
    cursor = conn.cursor()
    
    # Fetch all reminders from the database
    cursor.execute('SELECT id, text FROM reminders')
    reminders = cursor.fetchall()
    
    if reminders:
        for reminder_id, reminder_text in reminders:
            message = f"Reminder: {reminder_text}"
            speak(message)
            cursor.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))  # Delete the reminder after notifying
        conn.commit()
        conn.close()
        return "Reminders checked and notified."
    else:
        conn.close()
        return "No reminders to notify."
    
    # Notepad Integration
def open_notepad():
    os.system("notepad")
    return "Notepad opened."

def save_note(command):
    if "save note" in command:
        content = command.split("save note", 1)[-1].strip()
        if content:
            with open("note.txt", "a") as file:
                file.write(f"{datetime.datetime.now()} - {content}\n")
            message = f"Note saved: {content}"
            speak(message)
            return message
    return "No content provided. Please say 'save note <your note>'."

# Task List Management

def add_task(command):
    if "add task" in command:
        task = command.split("add task", 1)[-1].strip()
        if task:
            conn = sqlite3.connect('bruce.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO tasks (description) VALUES (?)', (task,))
            conn.commit()
            conn.close()
            message = f"Task added: {task}"
            speak(message)
            return message
    return "No task provided. Please say 'add task <your task>'."

def show_tasks():
    conn = sqlite3.connect('bruce.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, description FROM tasks')
    tasks = cursor.fetchall()
    conn.close()
    if tasks:
        message = "Here are your tasks:\n"
        for task_id, task_desc in tasks:
            message += f"Task {task_id}: {task_desc}\n"
        speak(message)
        return message
    else:
        message = "No tasks found."
        speak(message)
        return message

def clear_tasks():
    conn = sqlite3.connect('bruce.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks')
    conn.commit()
    conn.close()
    message = "All tasks cleared."
    speak(message)
    return message

# Weather Updates
def get_weather():
    try:
        speak("Opening weather information for Hyderabad.")
        webbrowser.open("https://www.weather.com/weather/today/l/17.38,78.47")
        return "Weather information opened in the browser."
    except Exception as e:
        error_message = f"An error occurred while retrieving the weather. {str(e)}"
        speak(error_message)
        return error_message

# Quick Dictionary
def get_meaning(command):
    if "meaning" in command:
        word = command.split("meaning", 1)[-1].strip()
        if word:
            try:
                dictionary = PyDictionary()
                meaning = dictionary.meaning(word)
                if meaning:
                    message = ""
                    for key, value in meaning.items():
                        message += f"{key}: {', '.join(value)}\n"
                    speak(message)
                    return message
                else:
                    message = f"I couldn't find the meaning of {word}."
                    speak(message)
                    return message
            except ImportError:
                message = "Dictionary feature requires PyDictionary module. Please install it."
                speak(message)
                return message
    return "No word provided. Please say 'meaning <word>'."

# Quick Access Commands
quick_access = {
    "chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "notepad": "notepad",
    "paint": "paint",
}

def open_quick_access(command):
    if "open" in command:
        app = command.split("open", 1)[-1].strip()
        if app in quick_access:
            os.startfile(quick_access[app])
            message = f"Opening {app}."
            speak(message)
            return message
        else:
            message = f"Application '{app}' not found in quick access commands."
            speak(message)
            return message
    return "No application specified. Please say 'open <application>'."

# Customizable Shortcuts

def add_shortcut(command):
    if "add shortcut" in command:
        # Extract the shortcut name and path from the command
        parts = command.split("add shortcut", 1)[-1].strip().split("path", 1)
        if len(parts) == 2:
            name = parts[0].strip()
            path = parts[1].strip()
            if name and path:
                conn = sqlite3.connect('bruce.db')
                cursor = conn.cursor()
                cursor.execute('INSERT INTO shortcuts (name, path) VALUES (?, ?)', (name, path))
                conn.commit()
                conn.close()
                message = f"Shortcut added: {name}."
                speak(message)
                return message
    return "Invalid command. Please say 'add shortcut <name> path <path>'."

def execute_shortcut(command):
    if "execute shortcut" in command:
        # Extract the shortcut name from the command
        name = command.split("execute shortcut", 1)[-1].strip()
        if name:
            conn = sqlite3.connect('bruce.db')
            cursor = conn.cursor()
            cursor.execute('SELECT path FROM shortcuts WHERE name = ?', (name,))
            result = cursor.fetchone()
            conn.close()
            if result:
                os.startfile(result[0])
                message = f"Executing shortcut {name}."
                speak(message)
                return message
            else:
                message = f"Shortcut '{name}' not found."
                speak(message)
                return message
    return "No shortcut name provided. Please say 'execute shortcut <name>'."

# Initialize shortcuts from file
shortcuts = {}
if os.path.exists("shortcuts.json"):
    with open("shortcuts.json", "r") as file:
        shortcuts = json.load(file)


# Features implementation
def open_file(command):
    if "open file" in command:
        # Extract the file name from the command
        file_name = command.split("open file", 1)[-1].strip()
        if file_name:
            file_path = rf"C:\Users\vutla\OneDrive\Documents\{file_name}.txt"
            if os.path.exists(file_path):
                os.startfile(file_path)
                message = f"Opening {file_name}"
                speak(message)
                return message
            else:
                message = f"Sorry, I couldn't find the file '{file_name}'."
                speak(message)
                return message
    return "No file name provided. Please say 'open file <file name>'."

def take_screenshot():
    try:
        screenshot = ImageGrab.grab()
        save_path = r"C:\Users\vutla\OneDrive\Pictures\screenshot.png"
        screenshot.save(save_path)
        message = f"Screenshot taken and saved at {save_path}."
        speak(message)
        return message
    except Exception as e:
        error_message = f"Failed to take a screenshot. Error: {str(e)}"
        speak(error_message)
        return error_message
    
def show_date_time():
    now = datetime.datetime.now()
    message = f"The current date is {now.strftime('%Y-%m-%d')} and the time is {now.strftime('%H:%M:%S')}."
    speak(message)  # Speak the message
    return message  # Return the message for the GUI

def web_search():
    speak("What should I search for?")
    query = take_command()
    if query:
        webbrowser.open(f"https://www.google.com/search?q={query}")
        message = f"Searching for {query}"
        speak(message)
        return message
    return "No search query provided."

# Email Functionality with Attachments and PyQt Dialogs
def send_email():
    """
    Send an email with optional attachment using PyQt dialogs for input.
    Reuses the existing QApplication instance from the main GUI.
    """
    try:
        # Get the existing QApplication instance
        app = QApplication.instance()
        if app is None:
            app = QApplication([])  # Create a new instance only if one doesn't exist

        # Get recipient email
        recipient, ok = QInputDialog.getText(None, "Recipient", "Enter recipient email:")
        if not ok or not recipient:
            return "No recipient provided."

        # Get email subject
        subject, ok = QInputDialog.getText(None, "Subject", "Enter email subject:")
        if not ok or not subject:
            return "No subject provided."

        # Get email body
        body, ok = QInputDialog.getText(None, "Body", "Enter email body:")
        if not ok or not body:
            return "No body provided."

        # Get attachment file path (optional)
        attachment_path, _ = QFileDialog.getOpenFileName(None, "Select Attachment", "", "All Files (*)")
        if not attachment_path:
            attachment_path = None  # No attachment selected

        # Set up the email
        sender_email = "vaishnavtechnologiesassistance@gmail.com"
        sender_password = "mzzhrokesnjyzgvc"  # Replace with your app password or actual password

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject

        # Attach the body
        msg.attach(MIMEText(body, 'plain'))

        # Attach the file if provided
        if attachment_path:
            if os.path.exists(attachment_path):
                attachment = open(attachment_path, "rb")
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(attachment_path)}")
                msg.attach(part)
                attachment.close()
            else:
                return f"Attachment file not found: {attachment_path}"

        # Send the email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())
        server.quit()
        message = f"Email sent successfully."
        speak(message)
        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email. Error: {str(e)}"

def system_info():
    battery = psutil.sensors_battery()
    message = f"Your system has {battery.percent} percent battery remaining."
    speak(message)
    return message

def shut_down_pc():
    speak("Are you sure you want to shut down the PC?")
    confirmation = take_command()
    if "yes" in confirmation:
        os.system("shutdown /s /t 1")
        speak("Shutting down the PC.")

# Main Menu
def basic_mode():
    speak("Initializing Bruce. Please wait...")
    choose_input_method()
    while True:
        speak("How can I assist you?")
        command = take_command()
        if command:
            if "open file" in command:
                open_file()
            elif "screenshot" in command:
                take_screenshot()
            elif "time" in command or "date" in command:
                show_date_time()
            elif "search" in command:
                web_search()
            elif "email" in command:
                send_email()
            elif "battery" in command or "system info" in command:
                system_info()
            elif "shut down" in command:
                shut_down_pc()
                break
            elif "add reminder" in command:
                set_reminder()
            elif "check reminders" in command:
                check_reminders()
            elif "add task" in command:
                add_task()
            elif "show task" in command:
                show_tasks()
            elif "clear task" in command:
                clear_tasks()
            elif "notepad" in command:
                open_notepad()
            elif "save note" in command:
                save_note()
            elif "play" in command or "pause" in command or "next" in command or "previous" in command or "volume" in command or "stop" in command:
                control_media(command)
            elif "shortcut" in command:
                if "add" in command:
                    add_shortcut()
                else:
                    execute_shortcut()
            elif "quick access" in command:
                open_quick_access()
            elif "meaning" in command:
                get_meaning()
            elif "weather" in command:
                get_weather()
            elif "exit" in command or "quit" in command:
                speak("Exiting Basic Mode. Goodbye!")
                break
            else:
                speak("Command not recognized.")

if __name__ == "__main__":
    speak("Welcome to Bruce. You are in Basic Mode.")
    basic_mode()
