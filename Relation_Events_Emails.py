# Import your dependencies
import os
import datetime
from nylas import APIClient
from dotenv import load_dotenv

# Load your env variables
load_dotenv()

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']

# Initialize your Nylas API client
nylas = APIClient(
    os.environ.get("CLIENT_ID"),
    os.environ.get("CLIENT_SECRET"),
    os.environ.get("ACCESS_TOKEN"),
)

calendars = nylas.calendars.all()
# Get the calendar_id of the "Client Meetings" calendar
calendar_id = [ calendar['id'] for calendar in calendars if 'alvaro.t@nylas.com' in calendar['name']][0]

today = datetime.date.today()

# Get Monday's datetime and convert it to a unix timestamp
monday = today + datetime.timedelta(days=-today.weekday())
monday_unix = monday.strftime("%s")

# Get Friday's datetime
friday = monday + datetime.timedelta(days=5)
friday_unix = friday.strftime("%s")

# Return all events between Monday and Friday of this week
events = nylas.events.where(calendar_id=calendar_id, starts_after=monday_unix, ends_before=friday_unix)

for event in events:
    match event.when['object']:
        case "timespan":
            print("Title: {} | Participants: {} | Description: {} | Start Time: {} | End Time: {}".format(
                event.title,
                ",".join([participant['email'] for participant in event.participants]),
                event.description,
                event.when['start_time'],
                event.when['end_time']
                ))
        case "datespan":
            print("Title: {} | Participants: {} | Description: {} | Start Time: {} | End Time: {}".format(
                event.title,
                ",".join([participant['email'] for participant in event.participants]),
                event.description,
                event.when['start_date'],
                event.when['end_date']
                ))
        case "date":
            print("Title: {} | Participants: {} | Description: {} | Start Time: {} | End Time: {}".format(
                event.title,
                ",".join([participant['email'] for participant in event.participants]),
                event.description,
                event.when['date']
                ))
    
# Select the first event and get the list of participants
first_event = events[0]
participants = first_event['participants']

# Use the Nylas Contacts API to return detailed information about each participant
for participant in participants:
    contacts = nylas.contacts.where(email=participant['email'])
    if contacts.all():
        contact = contacts[0]
        phone_number = next(iter(list(contact['phone_numbers'].values())), None)
        email = next(iter(list(contact['emails'].values())), None)
        print("Full Name: {} | Email: {} | Phone Number: {} | Location: {} | Profile Picture: {} | Company Name: {} | Job: {}".format(
            contact['given_name'] + " " + contact['surname'],
            email,
            phone_number,
            contact['office_location'],
            contact['picture_url'],
            contact['company_name'],
            contact['job_title'],
            ))
 
threads = []
for participant in participants:
    two_weeks_ago = datetime.date.today() - datetime.timedelta(14)
    unix_two_weeks_ago = two_weeks_ago.strftime("%s")
    # Search across the user's email inbox for threads in last 14 days that are from any of the event participants.
    threads = nylas.threads.where(from_=participant['email'], last_message_after=unix_two_weeks_ago)

# For all matching threads, return the subject line, snippet, and date for all messages from that thread
for thread in threads:
    for message_id in thread['message_ids']:
        message = nylas.messages.get(message_id)
        print("Subject Line:\n {} \n Snippet: \n {} \n Date: \n {}".format(
            message.subject,
            message.snippet,
            message.date
            ))
        
for thread in threads:
    for message_id in thread['message_ids']:
        message = nylas.messages.get(message_id)    
        if message.files:
            for file_ in message.files:
                file_object = nylas.files.get(file_['id'])
                print("File Object: " + file_object.content_type)
                if file_object.content_type != "message/delivery-status" and file_object.content_type != "message/rfc822":
                    print("File: {} | Content Type: {}".format(
                        file_object.filename,
                        file_object.content_type
                        ))
                    open(file_object.filename, 'wb').write(file_object.download())
                
current_participants = [ participant['email'] for participant in participants ]
new_participants = []

# For all matching threads, return the participants who aren't also a participant in the event
for thread in threads:
    for thread_participant in thread.participants:
        if thread_participant['email'] not in current_participants + new_participants :
            new_participants.append(thread_participant['email'])

print("Adding the following participants to the event:")
for participant in new_participants:
    print(participant)

# Modify the upcoming event to add the missing participants
for participant in new_participants:
    first_event.participants.append({'email' : participant})
    first_event.save(notify_participants='true')  
