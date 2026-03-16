import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

# Let's create a fake "suspicious audio transcript" to test
test_transcript = "Hey, it's me. I'm in a huge emergency and my phone broke. I'm borrowing a friend's phone. Please UPI me 5000 rupees immediately to this number. Don't call me back, just send it fast."

# The "System Prompt" - Telling Gemini how to act
prompt = f"""
You are an expert cybersecurity analyst. Read the following audio transcript and look for signs of a social engineering scam.
Provide a "Risk Score" from 0% to 100%, and list 2 short bullet points explaining the red flags.

Transcript: "{test_transcript}"
"""

# Send it to the AI and print the result
print("Analyzing transcript for scams...")
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt
)

print("\n--- SECURITY REPORT ---")
print(response.text)