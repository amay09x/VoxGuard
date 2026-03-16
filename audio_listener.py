import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

# 1. Load the secret variables
load_dotenv()
SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

def transcribe_audio(audio_file_path):
    print(f"Sending '{audio_file_path}' to Azure for transcription...")
    
    # 2. Configure Azure with your secret keys
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_recognition_language = "en-US" # You can change this later!
    
    # 3. Tell Azure to listen to a specific file, not the microphone
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    # 4. Do the transcription
    result = speech_recognizer.recognize_once_async().get()
    
    # 5. Check if it worked
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("\n--- TRANSCRIPT SUCCESS ---")
        print(result.text)
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("\nNo speech could be recognized.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        print(f"\nError: {result.cancellation_details.reason}")

# Let's test it! 
# We will call the function with a dummy file name for now.
transcribe_audio("test_audio.wav")