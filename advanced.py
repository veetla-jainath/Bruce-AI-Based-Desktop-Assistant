import sqlite3
import pyttsx3
import speech_recognition as sr
import requests
from datetime import datetime
import google.generativeai as genai
import os
import threading

class BruceAdvanced:
    def __init__(self, gui_callback=None):
        self.engine = pyttsx3.init()
        self.input_method = None
        self.conversation_history = []
        self.gui_callback = gui_callback
        self.speech_lock = threading.Lock()  # Lock for thread-safe speech

    def speak(self, text):
        def _speak():
            with self.speech_lock:
                self.engine.say(text)
                self.engine.runAndWait()

        # Run the speech in a separate thread
        threading.Thread(target=_speak, daemon=True).start()        

    def display_and_speak(self, text):
        if self.gui_callback:
            self.gui_callback(text)  # Send output to GUI
        print(text)
        self.speak(text)   # Speak the text in a thread-safe mannert

    def take_text_input(self):
        return input("Enter your command: ").strip().lower()

    def take_voice_input(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.display_and_speak("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=10)
                return recognizer.recognize_google(audio).lower()
            except sr.UnknownValueError:
                self.display_and_speak("Sorry, I didn't catch that.")
            except sr.RequestError:
                self.display_and_speak("There seems to be an issue with the recognition service.")
            return ""

    def take_command(self):
        if self.input_method == "voice":
            return self.take_voice_input()
        elif self.input_method == "text":
            return self.take_text_input()
        else:
            return None

    def choose_input_method(self):
        self.display_and_speak("Would you like to use voice input or text input?")
        print("Choose your input method: (voice/text)")
        while True:
            method = input("Enter 'voice' or 'text': ").strip().lower()
            if method in ("voice", "text"):
                self.input_method = method
                self.display_and_speak(f"You have selected {self.input_method} input for this session.")
                break
            else:
                print("Invalid choice. Please type 'voice' or 'text'.")
                self.display_and_speak("Invalid choice. Please choose again.")

    def get_database_connection(self):
        return sqlite3.connect('bruce.db')

    def sync_basic_advanced(self):
        conn = self.get_database_connection()
        cursor = conn.cursor()

        self.display_and_speak("Syncing tasks, reminders, and notes between modes.")
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        cursor.execute("SELECT * FROM reminders")
        reminders = cursor.fetchall()

        if tasks or reminders:
            self.display_and_speak("Here are the synced items:")
            for task in tasks:
                self.display_and_speak(f"Task: {task[1]}")
            for reminder in reminders:
                self.display_and_speak(f"Reminder: {reminder[1]} at {reminder[2]}")
        else:
            self.display_and_speak("No tasks or reminders to sync.")

        conn.close()

    def chat_with_gemini(self, prompt):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key is None:
            self.display_and_speak("API key not found. Please set the GEMINI_API_KEY environment variable.")
            return "API key error"

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')

        try:
            response = model.generate_content(prompt)
            reply = response.text.strip()
            self.display_and_speak(reply)
            return reply
        except Exception as e:
            self.display_and_speak(f"Error communicating with Gemini: {e}")
            return f"Error: {e}"

    def process_command(self, command):
        if "sync" in command:
            self.sync_basic_advanced()
        elif "ask" in command or "chat" in command or "gemini" in command:
            prompt = command.replace("ask", "").replace("chat", "").replace("gemini", "").strip()

            if not prompt and self.conversation_history:
                prompt = f"Follow-up on: {self.conversation_history[-1]['query']}"

            if prompt:
                response = self.chat_with_gemini("\n".join([f"User: {item['query']}\nGemini: {item['response']}" for item in self.conversation_history] + [f"User: {prompt}"]))
                self.conversation_history.append({"query": prompt, "response": response})
            else:
                self.display_and_speak("Please specify your question or topic to chat about.")
        elif "exit" in command or "quit" in command:
            self.display_and_speak("Exiting Advanced Mode.")
            return True
        else:
            self.display_and_speak("Sorry, I didn't understand that. Can you repeat?")
        return False

    def advanced_mode(self):
        self.display_and_speak("Welcome to Bruce Advanced Mode. How can I assist you?")
        while True:
            command = self.take_command()
            if command is None:
                continue
            if self.process_command(command):
                break

if __name__ == "__main__":
    bruce_advanced = BruceAdvanced()
    bruce_advanced.choose_input_method()
    bruce_advanced.advanced_mode()
