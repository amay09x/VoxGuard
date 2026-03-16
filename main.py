import os
import azure.cognitiveservices.speech as speechsdk
from google import genai
from dotenv import load_dotenv

# 1. Load all hidden keys from .env
load_dotenv()
SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 2. Initialize the Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

def transcribe_audio(audio_file_path):
    print(f"\n[1/2] Azure is listening to '{audio_file_path}'...")
    
    # Configure Azure Speech
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_recognition_language = "en-US" 
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    # Run transcription
    result = speech_recognizer.recognize_once_async().get()
    
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"      Transcript: '{result.text}'")
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("      Error: No speech could be recognized.")
        return None
    elif result.reason == speechsdk.ResultReason.Canceled:
        print(f"      Error: {result.cancellation_details.reason}")
        return None

def analyze_intent(transcript):
    print("\n[2/2] Gemini is analyzing the transcript for threats...")
    
    prompt = f"""
    You are an expert cybersecurity analyst. Read the following audio transcript and look for signs of a social engineering scam.
    Provide a "Risk Score" from 0% to 100%, and list 2 short bullet points explaining the red flags.

    Transcript: "{transcript}"
    """
    
    # Send to Gemini 2.5 Flash
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    print("\n=== VOXGUARD SECURITY REPORT ===")
    print(response.text)
    print("================================\n")

# --- MAIN EXECUTION PIPELINE ---
if __name__ == "__main__":
    # The audio file you will record later
    target_audio = "test_audio.wav"
    
    # Safety check: Does the file exist?
    if os.path.exists(target_audio):
        # Step 1: Get the text from Azure
        transcript_result = transcribe_audio(target_audio)
        
        # Step 2: If Azure heard something, send it to Gemini
        if transcript_result:
            analyze_intent(transcript_result)
    else:
        print(f"\nSystem Standby: Could not find '{target_audio}'.")
        print("Please record a test voice note, save it in this folder as 'test_audio.wav', and run the script again.")