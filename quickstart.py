from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import matplotlib.pyplot as plt
import sqlite3
conn = sqlite3.connect('texts.db')

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def getTimes(service, ids):
    days = []
    for i in ids:
        m = service.users().messages().get(userId='me', id=i).execute()
        print(m['snippet'])
        days.append(int(m['internalDate'])/(1000*3600*24)) #Convert from milliseconds to days
    return days


def createDatabase():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE texts
             (date real, data text)''')
    return conn


def addTheseToDatabase(service, ids, conn):
    c = conn.cursor()
    for i in ids:
        m = service.users().messages().get(userId='me', id=i).execute()
        time = int(m['internalDate'])/1000
        text = m['snippet']
        print("Inserting message from " + str(time) + ": " + text)
        c.execute("INSERT INTO texts VALUES (?,?)", (time,text))
    conn.commit()

def addAllToDatabase(service):
    results = service.users().labels().list(userId='me').execute()
    labels = results['labels']
    for label in labels:
        if label['name'] == u'SMS':
            textLabelId = label['id']

    conn = createDatabase()
    results = service.users().messages().list(userId='me', labelIds=textLabelId, q="to:Xiaoting").execute()
    while 'nextPageToken' in results:
        ids = [m['id'] for m in results['messages']]
        addTheseToDatabase(service, ids, conn)
        results = service.users().messages().list(userId='me', labelIds=textLabelId, q="to:Xiaoting",
                                                  pageToken = results['nextPageToken']).execute()
    ids = [m['id'] for m in results['messages']]
    addTheseToDatabase(service, ids, conn)
    conn.close()


def plotTimes(service):
    results = service.users().labels().list(userId='me').execute()
    labels = results['labels']
    for label in labels:
        if label['name'] == u'SMS':
            textLabelId = label['id']

    days = []
    results = service.users().messages().list(userId='me', labelIds=textLabelId, q="to:Xiaoting").execute()
    while 'nextPageToken' in results:
        ids = [m['id'] for m in results['messages']]
        days += getTimes(service, ids)
        results = service.users().messages().list(userId='me', labelIds=textLabelId, q="to:Xiaoting").execute()
    ids = [m['id'] for m in results['messages']]
    days += getTimes(service, ids)

    minDay = min(days)
    maxDay = max(days)
    counts = [0]*(maxDay - minDay + 1)
    x = range(maxDay - minDay + 1)
    for day in days:
        counts[day - minDay] += 1

    plt.bar(x, counts)
    plt.show()


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    #plotTimes(service)
    addAllToDatabase(service)


if __name__ == '__main__':
    main()
