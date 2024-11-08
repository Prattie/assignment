from datetime import datetime, timedelta
import os.path
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class CalendarIntegration:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.creds = None
        self.service = None
        try:
            self.initialize_credentials()
        except Exception as e:
            print(f"Failed to initialize calendar integration: {e}")

    def initialize_credentials(self):
        """Initialize Google Calendar credentials"""
        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError(
                        "credentials.json not found. Please download it from Google Cloud Console"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('calendar', 'v3', credentials=self.creds)

    def schedule_meeting(self, email, meeting_time, duration_minutes=60):
        """Schedule a meeting and return the event details"""
        try:
            if not self.service:
                raise Exception("Calendar service not initialized")

            event = {
                'summary': 'Educational Consultation',
                'location': 'Online Meeting',
                'description': 'Educational consultation session to discuss program details and next steps.',
                'start': {
                    'dateTime': meeting_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': (meeting_time + timedelta(minutes=duration_minutes)).isoformat(),
                    'timeZone': 'UTC',
                },
                'attendees': [
                    {'email': email},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }
            }

            event = self.service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all'
            ).execute()

            return {
                'event_id': event['id'],
                'meeting_link': event.get('hangoutLink', ''),
                'start_time': event['start']['dateTime'],
                'end_time': event['end']['dateTime']
            }

        except HttpError as error:
            print(f'An error occurred while scheduling the meeting: {error}')
            return None
        except Exception as e:
            print(f'Unexpected error while scheduling meeting: {e}')
            return None

    def cancel_meeting(self, event_id):
        """Cancel a scheduled meeting"""
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            return True
        except Exception as e:
            print(f'Error cancelling meeting: {e}')
            return False

if __name__ == "__main__":
    # Test the calendar integration
    try:
        calendar = CalendarIntegration()
        test_time = datetime.now() + timedelta(days=1)
        result = calendar.schedule_meeting("test@example.com", test_time)
        if result:
            print("Test meeting scheduled successfully!")
            print(f"Meeting details: {result}")
    except Exception as e:
        print(f"Test failed: {e}")