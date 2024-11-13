from video_bot import VideoBot
from agent2 import InteractiveEducationAgent
from eligibility_check import check_eligibility, format_eligibility_response
from calendar_integration import CalendarIntegration
from datetime import datetime, timedelta
import sys
import os
from dotenv import load_dotenv

class GloveraSystem:
    def __init__(self):
        print("Initializing Glovera System...")
        load_dotenv()
        
        # Initialize the VideoBot
        self.video_bot = VideoBot()
        
        # Initialize the InteractiveEducationAgent
        self.agent = InteractiveEducationAgent()

    def main(self):
        try:
            print("Starting Glovera System...")
            
            # Start the video conversation
            self.video_bot.start_conversation()  # This should start the video chat
            
            # Collect student information using the agent
            student_info = self.agent.get_student_info()  # This should use TTS to ask questions
            
            # Create a script based on the collected information
            script = self.agent.create_script()  # Assuming this method exists in agent2.py
            
            # Generate the video response using the VideoBot
            video_response = self.video_bot.generate_video_response(script)
            print(video_response)  # Print the result of the video generation
            
        except Exception as e:
            print(f"Error in main execution: {e}")

if __name__ == "__main__":
    glovera = GloveraSystem()
    glovera.main()
