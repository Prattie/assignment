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
        self.student_info = {}
        self.engine = pyttsx3.init()  # Initialize the TTS engine

    def speak(self, text):
        """Use TTS to speak the provided text."""
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Capture audio input from the user and convert it to text."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
            try:
                response = recognizer.recognize_google(audio)
                print(f"User said: {response}")
                return response
            except sr.UnknownValueError:
                print("Sorry, I did not understand that.")
                return ""
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return ""

    def get_student_info(self):
        """Collect student information through TTS."""
        self.speak("What is your name?")
        name = self.listen()  # Listen for the user's response
        self.student_info["name"] = name
        
        self.speak("What is your academic percentage?")
        academic_percentage = self.listen()
        self.student_info["academic_percentage"] = academic_percentage
        
        self.speak("Do you have any academic backlogs? (yes/no)")
        backlogs = self.listen()
        self.student_info["backlogs"] = backlogs
        
        self.speak("How many years of work experience do you have?")
        work_experience = self.listen()
        self.student_info["work_experience"] = work_experience
        
        return self.student_info

    def create_script(self):
        """Create a script based on the collected student information."""
        return (
            f"Hello {self.student_info['name']}, "
            f"your academic percentage is {self.student_info['academic_percentage']}, "
            f"you have {self.student_info['backlogs']} backlogs, "
            f"and you have {self.student_info['work_experience']} years of work experience."
        )

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
