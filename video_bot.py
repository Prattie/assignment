import os
from dotenv import load_dotenv
import requests
import json

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

    def generate_video_response(self, script):
        try:
            payload = {
                "replica_id": self.replica_id,
                "script": script
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                print(f"Video generated successfully: {response.json()}")
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error generating video: {e}")
            return None

    def start_conversation(self):
        print("Starting conversation...")
        welcome_script = "Hello! I'm your admission counselor. I'll help guide you through the admission process."
        return self.generate_video_response(welcome_script)

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
                # Here you would normally process the student's response
                # For now, we'll wait for actual integration
                student_info[question["topic"]] = None

        return student_info

if __name__ == "__main__":
    try:
        bot = VideoBot()
        bot.start_conversation()
        student_info = bot.collect_student_info()
        print("Student info collected:", student_info)
    except Exception as e:
        print(f"Error in main execution: {e}")
