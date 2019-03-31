from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import time

TOKEN = 'token.json'
CLIENT = 'client_id.json'
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
API = 'gmail'
VERSION = 'v1'
MAX_RESULTS = 5
LABELS_IDS = ['UNREAD']
USER_ID = 'me'


def compare(last_mail, mail):
    count = 0
    set1 = set(last_mail.keys())
    set2 = set(mail.keys())

    if len(set1) == len(set2):
        for key in set1:
            if last_mail[key] == mail[key]:
                count = count + 1

        if count == len(set1):
            return True

    return False


def init():
    store = file.Storage(TOKEN)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CLIENT, SCOPES)
        creds = tools.run_flow(flow, store)

    service = build(API, VERSION, http=creds.authorize(Http()))
    return service


def get_emails(service, last_mail):
    mails = []

    results = service.users().messages().list(userId=USER_ID, labelIds=LABELS_IDS, maxResults=MAX_RESULTS).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
    else:
        for message in messages:
            mail = {'from': '', 'to': '', 'subject': '', 'snippet': '', 'date': ''}
            msg = service.users().messages().get(userId=USER_ID, id=message['id']).execute()

            for field in msg['payload']['headers']:
                if field['name'] == 'From':
                    from_email = field['value'].encode('utf-8')
                    if len(from_email.split('<')) > 1:
                        mail['from'] = from_email.split('<')[0]
                    else:
                        mail['from'] = from_email
                elif field['name'] == 'To':
                    mail['to'] = field['value'].encode('utf-8')
                elif field['name'] == 'Date':
                    mail['date'] = field['value'].encode('utf-8')
                elif field['name'] == 'Subject':
                    mail['subject'] = field['value'].encode('utf-8')

            if 'snippet' in msg:
                mail['snippet'] = msg['snippet'].encode('utf-8')

            if 'internalDate' in msg:
                mail['date'] = str(time.strftime('%d %b, %I:%M %p', time.localtime(int(msg['internalDate']) / 1000))).encode('utf-8')

            if compare(last_mail, mail):
                break

            mails.append(mail)

        if len(mails) > 0:
            last_mail = mails[0]

    return mails, last_mail
