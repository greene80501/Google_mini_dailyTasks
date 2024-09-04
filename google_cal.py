import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dateutil import parser  # New import for flexible datetime parsing

# If modifying scopes, delete the file token.json
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate_google_calendar():
    """Authenticates with Google Calendar API and returns the service object."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret_365262864197-9e0bhtd6qsbvo4f6i4rdsec8oo75te13.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

def get_today_events(service):
    """Fetches all events from the user's Google Calendar for today."""
    # Use timezone-aware UTC datetime
    start_of_day = datetime.datetime.combine(
        datetime.date.today(), datetime.time.min, tzinfo=datetime.timezone.utc).isoformat()
    end_of_day = datetime.datetime.combine(
        datetime.date.today(), datetime.time.max, tzinfo=datetime.timezone.utc).isoformat()

    events_result = service.events().list(
        calendarId='primary', timeMin=start_of_day, timeMax=end_of_day,
        singleEvents=True, orderBy='startTime').execute()
    
    return events_result.get('items', [])

def format_event_time(event_time):
    """Formats the event time to a readable format using dateutil's parser."""
    dt = parser.isoparse(event_time)  # More flexible ISO parsing
    return dt.strftime('%I:%M %p')

def write_events_to_file(events, filename="today_events.txt"):
    """Writes the events to a text file with nicely formatted start and end times."""
    with open(filename, 'w') as file:
        if not events:
            file.write('No events found for today.\n')
        for event in events:
            summary = event.get('summary', 'No Title')
            start_time = event['start'].get('dateTime', event['start'].get('date'))
            end_time = event['end'].get('dateTime', event['end'].get('date'))
            
            # Format times nicely
            formatted_start = format_event_time(start_time)
            formatted_end = format_event_time(end_time)
            
            file.write(f'{summary} from {formatted_start} to {formatted_end}.\n')

def main():
    service = authenticate_google_calendar()
    events = get_today_events(service)
    write_events_to_file(events)

if __name__ == '__main__':
    main()
