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
        try:
            print("Initializing Glovera System...")
            load_dotenv()
            
            # Initialize both video and voice agents
            self.video_bot = VideoBot()
            self.interactive_agent = InteractiveEducationAgent()
            self.calendar_integration = CalendarIntegration()
            
            # Set interaction mode (video or voice)
            self.interaction_mode = os.getenv('INTERACTION_MODE', 'voice')  # Default to voice if not specified
            
        except Exception as e:
            print(f"Error initializing Glovera System: {e}")
            sys.exit(1)

    def main(self):
        try:
            print(f"Starting Glovera System in {self.interaction_mode} mode...")
            
            if self.interaction_mode == 'video':
                self.run_video_interaction()
            else:
                self.run_voice_interaction()
                
        except Exception as e:
            print(f"Error in main execution: {e}")
            self.handle_error(e)

    def run_video_interaction(self):
        """Handle video-based interaction flow"""
        try:
            # Step 1: Start video conversation
            print("Starting video conversation...")
            self.video_bot.start_conversation()
            
            # Step 2: Collect student information
            student_data = self.video_bot.collect_student_info()
            if not student_data:
                raise Exception("Failed to collect student data")
            
            # Step 3: Check eligibility
            print("Checking program eligibility...")
            eligible_programs = check_eligibility(student_data)
            
            # Step 4: Present results via video
            self.video_bot.present_eligibility_results(eligible_programs)
            
            # Step 5: Handle consultation scheduling
            self.handle_scheduling_video()
            
        except Exception as e:
            print(f"Error in video interaction: {e}")
            self.video_bot.generate_video_response(
                "I apologize, but we've encountered an error. "
                "Our team will contact you shortly to assist you."
            )

    def run_voice_interaction(self):
        """Handle voice-based interaction flow"""
        try:
            # Step 1: Collect student information
            student_data = self.interactive_agent.get_student_info()
            if not student_data:
                raise Exception("Failed to collect student data")
            
            # Step 2: Check eligibility
            print("Checking program eligibility...")
            eligible_programs = check_eligibility(student_data)
            
            # Step 3: Present results via voice
            response = format_eligibility_response(eligible_programs)
            self.interactive_agent.speak(response)
            
            # Step 4: Handle consultation scheduling
            self.handle_scheduling_voice()
            
        except Exception as e:
            print(f"Error in voice interaction: {e}")
            self.interactive_agent.speak(
                "I apologize, but we've encountered an error. "
                "Please contact our support team for assistance."
            )

    def handle_scheduling_video(self):
        """Handle scheduling flow for video interaction"""
        try:
            # Offer consultation
            self.video_bot.schedule_consultation()
            
            # Collect contact information
            contact_info = self.video_bot.collect_contact_info()
            
            if contact_info:
                # Schedule the meeting
                meeting_time = datetime.now() + timedelta(days=1)
                meeting_time = meeting_time.replace(hour=10, minute=0, second=0, microsecond=0)
                
                meeting_details = self.calendar_integration.schedule_meeting(
                    contact_info['email'],
                    meeting_time
                )
                
                # End conversation with scheduling confirmation
                self.video_bot.end_conversation(has_scheduled=True)
            else:
                # End conversation without scheduling
                self.video_bot.end_conversation(has_scheduled=False)
                
        except Exception as e:
            print(f"Error in video scheduling: {e}")
            self.video_bot.generate_video_response(
                "I'm having trouble with the scheduling system. "
                "Our team will contact you to set up the consultation."
            )

    def handle_scheduling_voice(self):
        """Handle scheduling flow for voice interaction"""
        try:
            self.interactive_agent.speak("Would you like to schedule a consultation?")
            response = self.interactive_agent.listen()
            
            if response and any(word in response.lower() 
                              for word in ['yes', 'sure', 'okay', 'yeah']):
                
                # Collect email
                self.interactive_agent.speak("Please type your email address:")
                email = input("Your email: ")
                while not '@' in email or not '.' in email:
                    print("Invalid email format. Please try again.")
                    email = input("Your email: ")
                
                # Get preferred time slot
                self.interactive_agent.speak("Please select your preferred time slot for tomorrow:")
                self.interactive_agent.speak("1. Morning (10 AM)")
                self.interactive_agent.speak("2. Afternoon (2 PM)")
                self.interactive_agent.speak("3. Evening (5 PM)")
                
                time_slot = input("Enter slot number (1/2/3): ")
                while time_slot not in ['1', '2', '3']:
                    print("Invalid selection. Please enter 1, 2, or 3.")
                    time_slot = input("Enter slot number (1/2/3): ")
                
                # Convert slot to time
                slot_times = {
                    '1': 10,  # 10 AM
                    '2': 14,  # 2 PM
                    '3': 17   # 5 PM
                }
                
                # Schedule meeting
                meeting_time = datetime.now() + timedelta(days=1)
                meeting_time = meeting_time.replace(
                    hour=slot_times[time_slot], 
                    minute=0, 
                    second=0, 
                    microsecond=0
                )
                
                try:
                    # Try to schedule with calendar integration
                    meeting_details = self.calendar_integration.schedule_meeting(
                        email, 
                        meeting_time
                    )
                except Exception as e:
                    print(f"Calendar integration error: {e}")
                    meeting_details = None
                
                # Confirm scheduling
                time_str = meeting_time.strftime("%I:%M %p")
                self.interactive_agent.speak(
                    f"Perfect! I've scheduled your consultation for tomorrow at {time_str}. "
                    f"You will receive a confirmation email at {email} with the meeting details."
                )
                
                # Final thank you message
                self.interactive_agent.speak(
                    "Thank you for choosing Glovera! We look forward to helping you "
                    "with your educational journey. Have a great day!"
                )
            else:
                self.interactive_agent.speak(
                    "No problem! Feel free to reach out to us whenever you'd like "
                    "to schedule a consultation. Thank you for using Glovera!"
                )
            
        except Exception as e:
            print(f"Error in scheduling: {e}")
            self.interactive_agent.speak(
                "I apologize for the inconvenience. Please email us at support@glovera.com "
                "to schedule your consultation. Thank you for your understanding."
            )

    def handle_error(self, error):
        """Handle errors based on interaction mode"""
        if self.interaction_mode == 'video':
            self.video_bot.generate_video_response(
                "I apologize, but we've encountered an error. "
                "Our team will contact you shortly to assist you."
            )
        else:
            self.interactive_agent.speak(
                "I apologize, but we've encountered an error. "
                "Please contact our support team for assistance."
            )

if __name__ == "__main__":
    try:
        # Set up environment
        load_dotenv()
        
        # Create and run Glovera system
        glovera = GloveraSystem()
        glovera.main()
        
    except Exception as e:
        print(f"Critical error in Glovera System: {e}")
        sys.exit(1)