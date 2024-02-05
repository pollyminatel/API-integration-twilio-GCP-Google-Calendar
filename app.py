import re
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from calendar_utility import CalendarUtility
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
calendar_utility = CalendarUtility()

global adding_event
adding_event = False

global conversation_state
conversation_state = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    global adding_event
    global conversation_state

    body = request.form['Body'].lower().strip()
    response = MessagingResponse()  # Initialize response here

    if adding_event == False:
        if 'next' in body:
            matches = re.findall(r'\d+', body)

            if matches:
                num_events = int(matches[0])
            else:
                num_events = 3

            calendar_service = calendar_utility.get_calendar_service()
            CALENDAR_ID = 'primary'
            next_events = calendar_utility.get_next_events(calendar_service, CALENDAR_ID, num_events)

            if next_events:
                for event in next_events:
                    summary = event['summary']
                    start_time = event['start'].get('dateTime', event['start'].get('date'))
                    response.message(f'Event: {summary}\nStart Time: {start_time}')
            else:
                response.message('No upcoming events.')

            return str(response)

        elif 'add' in body or 'create' in body:
            response.message("Please, provide a name for the event")
            adding_event = True
            return str(response)

        else:
            response.message('Invalid command. Please use "Next Events" or "Add Event".')
            return str(response)
    else:
        if conversation_state == {}:
            #logging.debug('CALLED COLLECT EVENT NAME')
            return calendar_utility.collect_event_name(response, conversation_state)

        elif conversation_state['event_date'] == 'awaiting_date' and conversation_state['event_name'] != 'awaiting_name':
            #logging.debug('CALLED COLLECT EVENT DATE')
            return calendar_utility.collect_event_date(response, conversation_state)

        elif conversation_state['event_time'] == 'awaiting_time' and conversation_state['event_date'] != 'awaiting_date':
            #logging.debug('CALLED COLLECT EVENT TIME')
            return calendar_utility.collect_event_time(response, conversation_state)

        elif conversation_state['event_duration'] == 'awaiting_duration' and conversation_state['event_time'] != 'awaiting_time':
            #logging.debug('CALLED COLLECT EVENT DURATION')
            return calendar_utility.collect_event_duration(response, conversation_state)

if __name__ == '__main__':
    app.run(debug=True)
