from flask import request
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import datetime
from googleapiclient.discovery import build
from google.cloud import storage
import json
import logging

logging.basicConfig(level=logging.DEBUG)

class CalendarUtility:
    def __init__(self):
        self.adding_event = False
        self.conversation_state = {}

    def store_credentials_to_gcs(self, credentials):
        storage_client = storage.Client()
        bucket_name = "twilio-calendartoken"
        bucket = storage_client.bucket(bucket_name)
        if not bucket.exists():
            bucket.create()

        token_blob = bucket.blob("token.json")
        token_data = credentials.to_json()
        token_blob.upload_from_string(token_data)

    def get_calendar_service(self):
        credentials = None
        SCOPES = ["https://www.googleapis.com/auth/calendar"]
        bucket_name = "twilio-calendartoken"
        token_file_name = "token.json"

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        if not bucket.exists():
            bucket.create()

        blob = bucket.blob(token_file_name)
        if blob.exists():
            token_data_str = blob.download_as_text()

            try:
                token_data = json.loads(token_data_str)
                credentials = Credentials.from_authorized_user_info(token_data, SCOPES)
            except json.JSONDecodeError:
                print("Error decoding JSON from token file.")
                credentials = None

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                credentials = flow.run_local_server(port=0)

            self.store_credentials_to_gcs(credentials)

        return build('calendar', 'v3', credentials=credentials)

    def get_next_events(self, calendar_service, calendar_id, num_events=3):
        now = datetime.datetime.utcnow().isoformat() + '-03:00'
        events_result = calendar_service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=num_events,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        return events

    def add_event(self, calendar_service, calendar_id, event):
        created_event = calendar_service.events().insert(calendarId=calendar_id, body=event).execute()
        return created_event

    def collect_event_name(self, response, conversation_state):
        logging.debug('STARTED COLLECT EVENT NAME')
        conversation_state['event_name'] = 'awaiting_name'

        while conversation_state['event_name'] == 'awaiting_name':
            conversation_state['event_name'] = request.form['Body']
            event_name = conversation_state['event_name']
            pass

        response.message(f'Got it! The event name is "{event_name}". What date is the event? (Please provide dd/mm/year)')
        conversation_state['event_date'] = 'awaiting_date'

        logging.debug('ENDED COLLECT EVENT NAME')
        return str(response)

    def collect_event_date(self, response, conversation_state):
        global event_date

        logging.debug('STARTED COLLECT EVENT DATE')
        while conversation_state['event_date'] == 'awaiting_date':
            conversation_state['event_date'] = request.form['Body']
            event_date = conversation_state['event_date']

            try:
                formatted_date = datetime.datetime.strptime(event_date, '%d/%m/%Y').strftime('%d/%m/%Y')
                response.message(
                    f'Great! The event "{conversation_state["event_name"]}" is scheduled for {formatted_date}. What time will the event start? (Please provide in HH:MM format)')
                conversation_state['event_time'] = 'awaiting_time'
                logging.debug('ENDED COLLECT EVENT DATE')
                return str(response)

            except ValueError:
                conversation_state['event_date'] = 'awaiting_date'
                response.message('Sorry, the provided date is not in the correct format. Please try again.')
                logging.debug('ENDED COLLECT EVENT DATE WITH ERROR')
                return str(response)

    def collect_event_time(self, response, conversation_state):
        global start_time

        logging.debug('STARTED COLLECT EVENT TIME')
        while conversation_state['event_time'] == 'awaiting_time':
            conversation_state['event_time'] = request.form['Body']
            event_time = conversation_state['event_time']

            try:
                start_time = datetime.datetime.strptime(event_time, '%H:%M').time()
                response.message(
                    f'The event "{conversation_state["event_name"]}" will start at {event_time}. How long will the event last? (Please provide in hours)')
                conversation_state['event_duration'] = 'awaiting_duration'

                return str(response)

            except ValueError:
                conversation_state['event_time'] = 'awaiting_time'
                response.message('Sorry, the provided time is not in the correct format. Please try again.')
                logging.debug('ENDED COLLECT EVENT TIME WITH ERROR')
                return str(response)

    def collect_event_duration(self, response, conversation_state):
        global start_time, event_date

        while conversation_state['event_duration'] == 'awaiting_duration':
            conversation_state['event_duration'] = request.form['Body']
            event_duration = conversation_state['event_duration']

            try:
                duration_hours = int(event_duration)
                end_time = (datetime.datetime.combine(datetime.date.today(), start_time) +
                            datetime.timedelta(hours=duration_hours)).time()

                start_datetime = datetime.datetime.strptime(f'{event_date} {start_time}', '%d/%m/%Y %H:%M:%S')
                end_datetime = datetime.datetime.strptime(f'{event_date} {end_time}', '%d/%m/%Y %H:%M:%S')

                event = {
                    'summary': conversation_state['event_name'],
                    'start': {'dateTime': start_datetime.strftime('%Y-%m-%dT%H:%M:%S'), 'timeZone': 'UTC-3'},
                    'end': {'dateTime': end_datetime.strftime('%Y-%m-%dT%H:%M:%S'), 'timeZone': 'UTC-3'},
                }

                calendar_service = self.get_calendar_service()
                calendar_id = 'primary'
                created_event = self.add_event(calendar_service, calendar_id, event)

                response.message(
                    f'The event "{conversation_state["event_name"]}" has been successfully added to your calendar.')

                conversation_state.clear()
                global adding_event
                adding_event = False
                logging.debug('ENDED COLLECT EVENT DURATION')

                return str(response)

            except ValueError as e:
                conversation_state['event_duration'] = 'awaiting_duration'
                response.message(
                    f'Sorry, the provided duration is not in the correct format. {str(e)} Please try again.')
                logging.debug('ENDED COLLECT EVENT DURATION WITH ERROR')
                return str(response)
