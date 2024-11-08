import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import pandas as pd
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import json
from time import sleep
import keyboard  # For detecting interruptions
from eligibility_check import check_eligibility, format_eligibility_response
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import calendar_integration  # Assuming you have the calendar integration from previous example
import sys

   # Load environment variables from .env file
load_dotenv()

class EducationCrew:
    def __init__(self):
        self.llm = ChatOpenAI(
        model="gpt-3.5-turbo",  # Correct model name format
        temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")  # Secure API key management
        )
        
        # Initialize agents
        self.intake_agent = Agent(
            role='Student Intake Specialist',
            goal='Gather comprehensive information about student background and aspirations',
            backstory="You are an experienced education consultant...",
            llm=self.llm,
            verbose=True
        )
        self.program_matcher = Agent(
            role='Program Matching Specialist',
            goal='Analyze student profiles and suggest optimal educational programs',
            backstory="You are an expert in global education programs...",
            llm=self.llm,
            verbose=True
        )
        self.scheduling_agent = Agent(
            role='Meeting Coordinator',
            goal='Schedule and coordinate follow-up consultations',
            backstory="You excel at managing schedules...",
            llm=self.llm,
            verbose=True
        )

    def create_tasks(self, student_info):
        """Define tasks and link them to specific agents."""
        intake_task = Task(
            description=f"""Interview the student and gather key information about their
            academic background, career goals, preferred locations, budget, and timeline.
            Current student info: {student_info}""",
            agent=self.intake_agent,
            expected_output=""
        )
        matching_task = Task(
            description="Analyze and recommend suitable programs based on student info...",
            agent=self.program_matcher,
            expected_output=""
        )
        scheduling_task = Task(
            description="Schedule a follow-up consultation with agenda and time slots.",
            agent=self.scheduling_agent,
            expected_output=""
        )
        return [intake_task, matching_task, scheduling_task]

    def run_crew(self, student_info):
        """Kick off crew execution with sequential processing."""
        crew = Crew(
            agents=[self.intake_agent, self.program_matcher, self.scheduling_agent],
            tasks=self.create_tasks(student_info),
            process=Process.sequential
        )
        try:
            result = crew.kickoff()
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

class InteractiveEducationAgent:
    def __init__(self):
        # Initialize speech recognition with longer timeout
        self.recognizer = sr.Recognizer()
        
        # Initialize text-to-speech engine
        try:
            self.speaker = pyttsx3.init()
            
            # Configure the speech engine
            voices = self.speaker.getProperty('voices')
            # Set voice to male voice
            self.speaker.setProperty('voice', voices[0].id)  # Usually male voice
            
            # Set properties for better clarity
            self.speaker.setProperty('rate', 150)    # Speaking rate
            self.speaker.setProperty('volume', 1.0)  # Volume
            
            # Initialize student_info dictionary
            self.student_info = {
                "name": "",
                "academic_percentage": 0,
                "backlogs": 0,
                "work_experience": 0,
                "is_three_year_degree": False,
                "preferred_locations": [],
                "budget": 0,
                "timeline": ""
            }
            
        except Exception as e:
            print(f"Error initializing speech engine: {e}")
            sys.exit(1)

    def speak(self, text):
        """Convert text to speech with error handling"""
        try:
            print(f"Agent Max: {text}")
            sentences = text.split('.')
            for sentence in sentences:
                if sentence.strip():
                    self.speaker.say(sentence.strip())
                    self.speaker.runAndWait()
                    sleep(0.5)
        except Exception as e:
            print(f"Speech Error: {e}")
            print(f"(Speech failed, text only) Agent Max: {text}")

    def listen(self):
        """Listen to user input with longer timeout"""
        with sr.Microphone() as source:
            print("\n🎤 Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            try:
                # Increased timeout and phrase_time_limit
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                print("Processing your response...")
                text = self.recognizer.recognize_google(audio)
                print(f"You: {text}")
                return text.lower()
                
            except sr.WaitTimeoutError:
                self.speak("I didn't hear anything. Could you please speak again?")
                return None
            except sr.UnknownValueError:
                self.speak("I couldn't understand that. Could you please repeat?")
                return None
            except sr.RequestError as e:
                self.speak("There was an error with the speech recognition service.")
                print(f"Error details: {e}")
                return None
            except Exception as e:
                print(f"Unexpected error in listen(): {e}")
                return None

    def convert_spoken_number(self, text):
        """Convert spoken numbers to numeric values"""
        number_mapping = {
            'zero': 0, 'no': 0, 'none': 0,
            'one': 1, 'a': 1, 'single': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine': 9,
            'ten': 10
        }
        
        # Convert text to lowercase and split into words
        words = text.lower().split()
        
        # First try to find spoken numbers
        for word in words:
            if word in number_mapping:
                return float(number_mapping[word])
        
        # Then try to find numeric digits
        numbers = ''.join(filter(str.isdigit, text))
        if numbers:
            return float(numbers)
            
        return None

    def get_student_info(self):
        """Gather student information through conversation"""
        # Introduction
        self.speak("Hi, Welcome to Glovera! I am Max, here to help you with your admission related queries.")
        sleep(1)

        # Get name
        self.speak("First, could you please tell me your name?")
        while not self.student_info["name"]:
            response = self.listen()
            if response:
                self.student_info["name"] = response
                self.speak(f"Nice to meet you, {response}! Let me help you find the perfect educational program.")

        # Get academic percentage
        self.speak("What was your academic percentage in your previous degree?")
        while self.student_info["academic_percentage"] == 0:
            response = self.listen()
            if response:
                try:
                    percentage = float(''.join(filter(str.isdigit, response)))
                    if 0 <= percentage <= 100:
                        self.student_info["academic_percentage"] = percentage
                        self.speak(f"Got it. Your percentage is {percentage}%")
                except ValueError:
                    self.speak("Please provide a valid percentage between 0 and 100")

        # Get backlogs
        self.speak("How many backlogs do you have, if any?")
        while self.student_info["backlogs"] == 0:
            response = self.listen()
            if response:
                try:
                    if 'no' in response.lower() or 'zero' in response.lower():
                        self.student_info["backlogs"] = 0
                        self.speak("Great! No backlogs noted.")
                        break
                    backlogs = int(''.join(filter(str.isdigit, response)))
                    self.student_info["backlogs"] = backlogs
                    self.speak(f"Noted. You have {backlogs} backlogs")
                except ValueError:
                    self.speak("Please provide a valid number")

        # Get work experience with improved number recognition
        self.speak("How many years of work experience do you have?")
        while self.student_info["work_experience"] == 0:
            response = self.listen()
            if response:
                # Try to convert the spoken response to a number
                experience = self.convert_spoken_number(response)
                
                if experience is not None:
                    self.student_info["work_experience"] = experience
                    if experience == 0:
                        self.speak("Noted, no work experience.")
                    else:
                        year_word = "year" if experience == 1 else "years"
                        self.speak(f"Understood. You have {experience} {year_word} of work experience")
                    break
                else:
                    self.speak("Could you please say that again? For example, 'two years' or 'no experience'")

        # Check three-year degree
        self.speak("Do you have a three-year degree?")
        while "is_three_year_degree" not in self.student_info:
            response = self.listen()
            if response:
                is_three_year = any(word in response.lower() for word in ['yes', 'yeah', 'true', 'correct'])
                self.student_info["is_three_year_degree"] = is_three_year
                self.speak("Thank you for that information")

        # Get preferred locations
        self.speak("Which countries are you interested in studying in? For example, USA, Canada, or UK?")
        while not self.student_info["preferred_locations"]:
            response = self.listen()
            if response:
                # Split response into individual countries
                locations = [loc.strip() for loc in response.replace('and', ',').split(',')]
                self.student_info["preferred_locations"] = locations
                self.speak(f"Great! You're interested in studying in {', '.join(locations)}")

        # Get budget
        self.speak("What is your budget range for the program in US dollars?")
        while self.student_info["budget"] == 0:
            response = self.listen()
            if response:
                try:
                    # Extract numbers from response
                    numbers = ''.join(filter(str.isdigit, response))
                    if numbers:
                        budget = int(numbers)
                        self.student_info["budget"] = budget
                        self.speak(f"I've noted your budget as {budget} dollars.")
                except ValueError:
                    self.speak("Could you please specify the amount in numbers?")

        # Confirm all information
        self.speak("Let me confirm your information:")
        self.speak(f"Your name is {self.student_info['name']}")
        self.speak(f"Your academic percentage is {self.student_info['academic_percentage']}%")
        self.speak(f"You have {self.student_info['backlogs']} backlogs")
        
        year_word = "year" if self.student_info['work_experience'] == 1 else "years"
        self.speak(f"You have {self.student_info['work_experience']} {year_word} of work experience")
        
        degree_type = "a three-year" if self.student_info['is_three_year_degree'] else "not a three-year"
        self.speak(f"You have {degree_type} degree")
        
        self.speak(f"You're interested in studying in {', '.join(self.student_info['preferred_locations'])}")
        self.speak(f"Your budget is {self.student_info['budget']} dollars")

        # Ask for confirmation
        self.speak("Is all this information correct? Please say yes or no.")
        while True:
            response = self.listen()
            if response:
                if any(word in response.lower() for word in ['yes', 'correct', 'right', 'yeah']):
                    self.speak("Perfect! Let me find the best programs for you based on this information.")
                    return self.student_info
                elif any(word in response.lower() for word in ['no', 'wrong', 'incorrect']):
                    self.speak("Let's start over to ensure we have your correct information.")
                    return self.get_student_info()  # Start over
                else:
                    self.speak("Please say yes if the information is correct, or no if you'd like to make changes.")

        return self.student_info

    def handle_interruption(self, e):
        """Handle user interruption"""
        self.speak("Yes? How can I help you?")
        response = self.listen()
        if response:
            self.speak(f"Thank you for your input: {response}")
            # Here you can add logic to handle different types of interruptions
            return response
        return None

    def process_eligibility_and_schedule(self, student_info):
        """Process eligibility and handle meeting scheduling"""
        try:
            # Import eligibility functions
            from eligibility_check import check_eligibility, format_eligibility_response
            
            # Check eligibility
            print("Checking eligibility...")
            eligible_programs = check_eligibility(student_info)
            
            # Format response
            response_text = format_eligibility_response(eligible_programs)
            
            # Speak the results
            self.speak(response_text)
            
            # Ask about scheduling
            self.speak("Would you like to schedule a consultation with one of our advisors to discuss these options?")
            schedule_response = self.listen()
            
            if schedule_response and any(word in schedule_response.lower() for word in ['yes', 'sure', 'okay', 'yeah']):
                return {
                    "eligible_programs": eligible_programs,
                    "meeting_scheduled": True
                }
            else:
                return {
                    "eligible_programs": eligible_programs,
                    "meeting_scheduled": False
                }

        except Exception as e:
            print(f"Error in processing eligibility and scheduling: {str(e)}")
            self.speak("I'm having trouble processing the eligibility check. Let me connect you with an advisor.")
            return None

    def collect_contact_info(self):
        """Collect contact information for meeting scheduling"""
        contact_info = {}
        
        # Get email
        self.speak("Please provide your email address. Spell it out for me.")
        while 'email' not in contact_info:
            response = self.listen()
            if response:
                # Remove spaces and convert "at" to @
                email = response.lower().replace(" at ", "@").replace(" dot ", ".").replace(" ", "")
                contact_info['email'] = email
                self.speak(f"I have recorded your email as {email}. Is this correct?")
                confirmation = self.listen()
                if not any(word in confirmation.lower() for word in ['yes', 'correct', 'right']):
                    del contact_info['email']
                    self.speak("Let's try again. Please spell out your email address.")

        # Get phone number
        self.speak("Please provide your phone number.")
        while 'phone' not in contact_info:
            response = self.listen()
            if response:
                # Extract numbers from response
                numbers = ''.join(filter(str.isdigit, response))
                if len(numbers) >= 10:
                    contact_info['phone'] = numbers
                    self.speak(f"I have recorded your phone number as {' '.join(numbers)}. Is this correct?")
                    confirmation = self.listen()
                    if not any(word in confirmation.lower() for word in ['yes', 'correct', 'right']):
                        del contact_info['phone']
                        self.speak("Let's try again. Please provide your phone number.")
                else:
                    self.speak("Please provide a valid phone number with at least 10 digits.")

        return contact_info

    def schedule_meeting(self, contact_info):
        """Schedule a meeting and return meeting details"""
        self.speak("Let's schedule a meeting. When would be a good time for you? Please specify a day and time.")
        
        meeting_time = None
        while not meeting_time:
            response = self.listen()
            if response:
                try:
                    # Here you would need to implement natural language processing for date/time
                    # For this example, we'll schedule it for tomorrow at 10 AM
                    meeting_time = datetime.now() + timedelta(days=1)
                    meeting_time = meeting_time.replace(hour=10, minute=0, second=0, microsecond=0)
                    
                    # Create calendar event
                    calendar = calendar_integration.CalendarIntegration()
                    event = calendar.schedule_meeting(
                        contact_info['email'],
                        meeting_time,
                        duration_minutes=60
                    )
                    
                    return {
                        "datetime": meeting_time,
                        "duration": 60,
                        "event_id": event['id']
                    }
                except Exception as e:
                    print(f"Error scheduling meeting: {str(e)}")
                    self.speak("I'm having trouble scheduling the meeting. Let's try again.")
                    meeting_time = None

    def send_confirmation(self, contact_info, meeting_details):
        """Send confirmation email and SMS"""
        # Email configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "your-email@gmail.com"  # Replace with your email
        sender_password = "your-app-password"   # Replace with your app password

        # Create email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = contact_info['email']
        msg['Subject'] = "Educational Consultation Meeting Confirmation"

        body = f"""
        Dear Student,

        Thank you for your interest in our educational programs. Your consultation meeting has been scheduled for:
        Date: {meeting_details['datetime'].strftime('%B %d, %Y')}
        Time: {meeting_details['datetime'].strftime('%I:%M %p')}
        Duration: {meeting_details['duration']} minutes

        The meeting link will be sent to you 15 minutes before the scheduled time.

        Best regards,
        Your Educational Consultant
        """

        msg.attach(MIMEText(body, 'plain'))

        # Send email
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            self.speak("I've sent you a confirmation email with the meeting details.")
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            self.speak("I wasn't able to send the confirmation email, but your meeting has been scheduled.")

if __name__ == "__main__":
    # Test the speech system first
    print("Testing speech system...")
    agent = InteractiveEducationAgent()
    agent.test_speech_system()
    
    # If you want to continue with the rest of your program:
    try:
        # Get student information through conversation
        student_info = agent.get_student_info()
        
        # Process eligibility and schedule meeting if requested
        result = agent.process_eligibility_and_schedule(student_info)
        
        if result:
            if result["meeting_scheduled"]:
                agent.speak("Great! I've scheduled your meeting and sent you the details.")
            else:
                agent.speak("Thank you for your time. Feel free to reach out if you need anything else.")
                
    except Exception as e:
        print(f"Error in main program: {e}")