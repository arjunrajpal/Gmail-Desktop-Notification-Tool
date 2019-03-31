import os, schedule, time
import gmail_mails

GMAIL_LINK = 'https://mail.google.com'
SOUND = 'default'

last_mail = {}


# The notifier function
def notify(title, subtitle, message, link=GMAIL_LINK, sound=SOUND):
    t = '-title {!r}'.format(title).encode('utf-8')
    s = '-subtitle {!r}'.format(subtitle).encode('utf-8')
    m = '-message {!r}'.format(message).encode('utf-8')
    l = '-open {!r}'.format(link)
    sound = '-sound {!r}'.format(sound)
    os.system('terminal-notifier.app/Contents/MacOS/terminal-notifier {}'.format(' '.join([m, t, s, l, sound])))


def send_notifications(service):
    global last_mail
    emails, last_mail = gmail_mails.get_emails(service, last_mail)

    for i in range(len(emails)):
        notify(title=emails[i]['subject'],
               subtitle=emails[i]['from'] + '|' + emails[i]['date'],
               message=emails[i]['snippet'])
        time.sleep(3)


if __name__ == '__main__':
    service = gmail_mails.init()

    schedule.every(60).minutes.do(send_notifications, service)

    while True:
        schedule.run_pending()
        time.sleep(1)
