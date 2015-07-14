## Wemo Data Parser

Parse CSV email attachments from [Wemo Insight](http://www.belkin.com/us/p/P-F7C029/) Smart Switch reports. 
Simple and somewhat hacky, hopefully it will get better in time (pull requests welcome!)

### Usage

Tested on python 2.7. Run `main.py` using the following options:

```
--imap_host IMAP_HOST
                        IMAP host to connect to
  --imap_user IMAP_USER
                        IMAP username
  --imap_password IMAP_PASSWORD
                        IMAP password
  --db_dir DB_DIR       Directory to write database files to
  --print_output        Print output to stdout?
  --email_search EMAIL_SEARCH
                        search string
```


