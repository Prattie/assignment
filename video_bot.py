import os
import requests
import json
import pyaudio
import webrtcvad
from dotenv import load_dotenv

class VideoBot:
    def __init__(self):
        load_dotenv()
        self.api_url = "https://api.tavus.io/v2/videos"
        self.api_key = os.getenv('TAVUS_API_KEY')
        self.replica_id = os.getenv('REPLICA_ID')
        
        if not self.api_key or not self.replica_id:
            raise ValueError("Missing TAVUS_API_KEY or REPLICA_ID in .env file")
            
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        self.conversation_history = []
        self.vad = webrtcvad.Vad(1)  # Set aggressiveness mode (0-3)

    def generate_video_response(self, script):
        try:
            payload = {
                "replica_id": self.replica_id,
                "script": script
            }
            
            print("Preparing to send request to Tavus API...")
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30  # Increase timeout to 30 seconds
            )
            
            if response.status_code == 200:
                print(f"Video generated successfully: {response.json()}")
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
            
        except requests.exceptions.Timeout:
            print("Request timed out. Please check your network connection.")
            return None
        except Exception as e:
            print(f"Error generating video: {e}")
            return None

    def start_conversation(self):
        """Start the initial conversation with the user."""
        print("Starting conversation...")
        welcome_script = "Hello! I'm your admission counselor. I'll help guide you through the admission process."
        response = self.generate_video_response(welcome_script)
        if response is None:
            print("Failed to start video conversation. Exiting.")
            return False  # Indicate failure
        return True  # Indicate success

    def listen_for_speech(self):
        """Listen for user speech using VAD."""
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
        
        print("Listening for speech...")
        while True:
            audio_data = stream.read(1024)
            if self.vad.is_speech(audio_data, 16000):
                print("User is speaking...")
                break
        
        stream.stop_stream()
        stream.close()
        audio.terminate()

    def collect_student_info(self):
        print("Collecting student information...")
        questions = [
            {
                "topic": "name",
                "script": "Could you please tell me your name?"
            },
            {
                "topic": "academic_percentage",
                "script": "What is your academic percentage in your last degree?"
            },
            {
                "topic": "backlogs",
                "script": "Do you have any academic backlogs?"
            },
            {
                "topic": "work_experience",
                "script": "How many years of work experience do you have?"
            }
        ]

        student_info = {}
        for question in questions:
            response = self.generate_video_response(question["script"])
            if response:
                # Listen for user response
                self.listen_for_speech()
                # Here you would normally process the student's response
                # For now, we'll wait for actual integration
                student_info[question["topic"]] = None

        return student_info

if __name__ == "__main__":
    try:
        bot = VideoBot()
        if bot.start_conversation():  # Check if the conversation started successfully
            student_info = bot.collect_student_info()
            print("Student info collected:", student_info)
        else:
            print("Conversation could not be started. Exiting.")
    except Exception as e:
        print(f"Error in main execution: {e}")
