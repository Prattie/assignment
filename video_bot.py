import os
import requests
from dotenv import load_dotenv
import time
from eligibility_check import check_eligibility, format_eligibility_response

class VideoBot:
    def __init__(self):
        load_dotenv()
        self.api_url = "https://tavusapi.com/v2/videos"
        self.api_key = os.getenv('Tavus_api_key')
        self.replica_id = os.getenv('replica_id')  # Replace with your Tavus replica ID
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        self.conversation_history = []

    def generate_video_response(self, script):
        """Generate a video response using Tavus API"""
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
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Error generating video: {e}")
            return None

    def start_conversation(self):
        """Start the initial conversation"""
        welcome_script = """
        Hello! I'm your AI educational consultant. I'll help you find the perfect 
        educational program for your goals. I'll need to ask you a few questions 
        to understand your background and preferences better. Are you ready to begin?
        """
        return self.generate_video_response(welcome_script)

    def collect_student_info(self):
        """Collect student information through video interaction"""
        questions = [
            {
                "topic": "name",
                "script": "What is your name?"
            },
            {
                "topic": "academic_percentage",
                "script": "What was your academic percentage in your previous degree?"
            },
            {
                "topic": "backlogs",
                "script": "How many backlogs do you have?"
            },
            {
                "topic": "work_experience",
                "script": "How many years of work experience do you have?"
            },
            {
                "topic": "three_year_degree",
                "script": "Do you have a three-year degree?"
            }
        ]

        student_info = {}
        for question in questions:
            response = self.generate_video_response(question["script"])
            if response:
                # Here you would normally wait for and process the student's response
                # For now, we'll simulate waiting for a response
                time.sleep(2)  # Simulate waiting for response
                
                # Store the response (in a real implementation, this would come from the student)
                student_info[question["topic"]] = "Sample response"

        return student_info

    def present_eligibility_results(self, eligible_programs):
        """Present eligibility results through video"""
        response_text = format_eligibility_response(eligible_programs)
        return self.generate_video_response(response_text)

    def schedule_consultation(self):
        """Handle consultation scheduling through video"""
        scheduling_script = """
        Would you like to schedule a consultation with one of our advisors to discuss 
        these programs in detail? If yes, I'll need your email and preferred time slot.
        """
        return self.generate_video_response(scheduling_script)

    def collect_contact_info(self):
        """Collect contact information through video"""
        contact_scripts = [
            {
                "topic": "email",
                "script": "Please provide your email address. You can spell it out for me."
            },
            {
                "topic": "phone",
                "script": "What's your phone number? I'll use this to send you meeting details."
            },
            {
                "topic": "preferred_time",
                "script": "What's your preferred time for the consultation? We can schedule it for tomorrow."
            }
        ]

        contact_info = {}
        for script in contact_scripts:
            response = self.generate_video_response(script["script"])
            if response:
                # Simulate waiting for response
                time.sleep(2)
                contact_info[script["topic"]] = "Sample response"

        return contact_info

    def end_conversation(self, has_scheduled=False):
        """End the conversation appropriately"""
        if has_scheduled:
            closing_script = """
            Thank you for your time! I've scheduled your consultation and you'll 
            receive an email with the meeting details shortly. Looking forward to 
            having our team help you further with your educational journey!
            """
        else:
            closing_script = """
            Thank you for your time! If you'd like to schedule a consultation later, 
            you can always reach out to our support team. Good luck with your 
            educational journey!
            """
        return self.generate_video_response(closing_script)

def main():
    try:
        # Initialize the video bot
        video_bot = VideoBot()

        # Start conversation
        print("Starting conversation...")
        video_bot.start_conversation()

        # Collect student information
        print("Collecting student information...")
        student_info = video_bot.collect_student_info()

        # Check eligibility
        print("Checking eligibility...")
        eligible_programs = check_eligibility(student_info)

        # Present results
        print("Presenting results...")
        video_bot.present_eligibility_results(eligible_programs)

        # Offer consultation
        print("Offering consultation...")
        video_bot.schedule_consultation()

        # Collect contact information if interested
        contact_info = video_bot.collect_contact_info()

        # End conversation
        print("Ending conversation...")
        video_bot.end_conversation(has_scheduled=bool(contact_info))

        print("Conversation completed successfully!")

    except Exception as e:
        print(f"Error in video bot conversation: {e}")

if __name__ == "__main__":
    main()
