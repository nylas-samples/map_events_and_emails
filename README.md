# map_events_and_emails

The sample shows how to check a user's calendar for upcoming meetings this week, pull contact and email data for the meeting participants, and make modifications to the meetings based on the context of recent email communications with participants.

For context, you can check the blog post ["Turn Your App Into a Scheduling Powerhouse With Nylas"](https://www.nylas.com/blog/turn-your-app-into-scheduling-powerhouse-with-nylas/).

## Setup

### System dependencies

- Python v3.x

### Gather environment variables

You'll need the following values:

```text
CLIENT_ID = ""
CLIENT_SECRET = ""
ACCESS_TOKEN = ""
```

Add the above values to a new `.env` file:

```bash
$ touch .env # Then add your env variables
```

Run the file **Relations_Events_Emails.py**:

```bash
$ python3 Relations_Events_Emails.py
```

## Learn more

Visit our [Nylas Python SDK documentation](https://developer.nylas.com/docs/developer-tools/sdk/python-sdk/) to learn more.
