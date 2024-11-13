import os
import requests
from dotenv import load_dotenv

class VideoBot:
    def __init__(self):
        load_dotenv()
        self.api_url = "https://api.tavus.io/v2/videos"  # Ensure this is the correct URL
        self.api_key = os.getenv('TAVUS_API_KEY')
        self.replica_id = "r79e1c033f"  # Use the provided REPLICA_ID
        
        if not self.api_key:
            raise ValueError("Missing TAVUS_API_KEY in .env file")
            
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }

    def display_avatar(self):
        """Display the avatar using the Tavus API."""
        print(f"Displaying avatar with Replica ID: {self.replica_id}")
        # Here you would implement the logic to start the video stream
        # For example, you might call an API to start the video or use a library to display the avatar
        # This is a placeholder for actual video display logic
        # You might need to integrate with a video library or API to show the avatar

    def generate_video_response(self, script):
        try:
            payload = {
                "replica_id": self.replica_id,
                "script": script,
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30  # Set timeout to 30 seconds
            )
            
            if response.status_code == 200:
                return response.json().get("hosted_url", "Video generated successfully, but no URL returned.")
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "Request timed out. Please check your network connection."
        except Exception as e:
            return f"Error generating video: {e}"

    def start_conversation(self):
        """Start the video conversation and display the avatar."""
        print("Starting video conversation...")
        self.display_avatar()  # Display the avatar
        # You can add additional logic here to handle the conversation flow

if __name__ == "__main__":
    bot = VideoBot()
    bot.start_conversation()
