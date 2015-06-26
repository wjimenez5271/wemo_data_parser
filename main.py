# some parts taken from: https://gist.github.com/baali/2633554

import email
import imaplib
import cStringIO
import csv
import pprint
import argparse

def parse_attachement(messageParts):
    message_body = messageParts[0][1]
    mail = email.message_from_string(message_body)
    for part in mail.walk():
        if part.get_content_maintype() == 'multipart':
            # print part.as_string()
            continue
        if part.get('Content-Disposition') is None:
            # print part.as_string()
            continue
        return part.get_payload(decode=True)

def connect_imap(imap_host, imap_user, imap_pass):
    s = imaplib.IMAP4_SSL(imap_host)
    s.login(imap_user, imap_pass)
    return s

def get_messages(imap_server, search_string):
    imap_server.select('Inbox')
    typ, data = imap_server.search(None, search_string)
    return typ, data


def parse_csv(csvbody):
    _l = []
    data = csv.DictReader(cStringIO.StringIO(csvbody))
    for row in data:
      _l.append(row)
    return _l


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Export Elasticsearch data using an HTTP/web based interface')
    parser.add_argument("--imap_host", help="IMAP host to connect to", required=True)
    parser.add_argument("--imap_user", help="IMAP username", required=True)
    parser.add_argument("--imap_password", help="IMAP password", required=True)
    parser.add_argument("--email_search", help="search string",
                        required=False, default='(From WeMoExport@Belkin.com)')

    args = parser.parse_args()

    imapSession = connect_imap(args.imap_host, args.imap_user, args.imap_password)

    typ, data = get_messages(imapSession, args.email_search)

    for msgId in data[0].split():
        typ, messageParts = imapSession.fetch(msgId, '(RFC822)')
        print parse_attachement(messageParts)