# some parts taken from: https://gist.github.com/baali/2633554

import email
import imaplib
import cStringIO
import csv
import pprint
import argparse
import json
import os

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

def seperate_datatypes(csvdata):
    def reconstruct_string(l):
        _l = ''
        for line in l:
            _l = _l + line
        return _l

    header = []
    daily_summary = []
    detailed_usage = []
    a = header
    for line in cStringIO.StringIO(csvdata):
        if "Exported Data for WeMo Insight" in line:
            a = header
        elif "Daily Usage Summary" in line:
            a = daily_summary
        elif "Energy Data" in line:
            a = detailed_usage
        else:
            a.append(line)
    header = reconstruct_string(header)
    daily_summary = reconstruct_string(daily_summary)
    detailed_usage = reconstruct_string(detailed_usage)
    return header, daily_summary, detailed_usage


def parse_csv(csvbody):
    _l = []
    data = csv.DictReader(cStringIO.StringIO(csvbody))
    for row in data:
      _l.append(row)
    return _l

def update_db(dbname, data, dirpath):
    filename = os.path.join(dirpath,'db_{}.json'.format(dbname))
    if not os.path.isfile(filename):
        with open (filename, 'w') as f:
            f.write('[]')
    with open(filename, 'r') as f:
        _data = json.load(f)
    _data.append(data)
    with open(filename, 'w') as f:
        json.dump(_data, f)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Export Elasticsearch data using an HTTP/web based interface')
    parser.add_argument("--imap_host", help="IMAP host to connect to", required=True)
    parser.add_argument("--imap_user", help="IMAP username", required=True)
    parser.add_argument("--imap_password", help="IMAP password", required=True)
    parser.add_argument("--db_dir", help="Directory to write database files to", required=False,
                        default=os.path.expanduser("~"))
    parser.add_argument("--email_search", help="search string",
                        required=False, default='(From WeMoExport@Belkin.com)')

    args = parser.parse_args()

    imapSession = connect_imap(args.imap_host, args.imap_user, args.imap_password)

    typ, data = get_messages(imapSession, args.email_search)

    for msgId in data[0].split():
        typ, messageParts = imapSession.fetch(msgId, '(RFC822)')
        data = parse_attachement(messageParts)

    header, daily_summary, detailed_usage = seperate_datatypes(data)

    update_db("daily_summary", parse_csv(daily_summary), args.db_dir)
    update_db("detailed_usage", parse_csv(detailed_usage), args.db_dir)
