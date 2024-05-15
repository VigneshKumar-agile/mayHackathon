from http.client import HTTPException
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import speech_recognition as sr
import keyboard
from googletrans import Translator  
from gtts import gTTS  
import os

import uvicorn

app = FastAPI()

# Initialize the recognizer
recognizer = sr.Recognizer()

# Enable CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def save_text_to_file(text, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text)

def audio_to_text(audio_file):
    translator = Translator()
    with sr.AudioFile(audio_file.file) as source:
        print("Transcribing audio...")
        audio_data = recognizer.record(source)
        
        try:
            # Use Google Speech Recognition to convert audio to text
            text = recognizer.recognize_google(audio_data)
            print("You said:", text)
            
            # Translate the text to Tamil
            translated_text = translator.translate(text, dest='ta').text
            print("Translated to Tamil:", translated_text)
            
            # Text to Speech (Tamil)
            tts = gTTS(text=translated_text, lang='ta')
            output_file_path = "output.mp3"
            # tts.save(output_file_path)  # Save as MP3 file
            # print("Tamil audio generated! Saved as output.mp3")
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file_path = temp_file.name
                tts.save(temp_file_path)
                print("Tamil audio generated! Saved as", temp_file_path)
            
            return output_file_path
        except sr.UnknownValueError:
            raise HTTPException(status_code=400, detail="Sorry, I could not understand the audio.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

@app.post("/convert-audio")
async def convert_audio(upload_file: UploadFile = File(...)):
    if upload_file.content_type.startswith('audio/'):
        file_path =  audio_to_text(upload_file)
        print(file_path)
        return FileResponse(file_path, media_type="audio/mpeg",filename="output.mp3")
    else:
        raise HTTPException(status_code=415, detail="Unsupported Media Type (only audio files supported)")
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)