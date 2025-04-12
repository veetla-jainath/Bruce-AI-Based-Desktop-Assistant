import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Test")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
    