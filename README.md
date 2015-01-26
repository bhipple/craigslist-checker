Craiglist Checker
=================
Send a text when there's a new post for a given keyword or phrase.

The script sends a message to a given address using GMail's SMTP protocol

Be sure to edit the config.py file for sending credentials and target address, target CraigsList site and target category

Send SMS by specifying a target address of the form 

An SMS message will only be sent if a new post appears (based on the full URL).

Setup
-----
Install the required libraries via pip:

    pip install -r requirements.txt

Usage
-----
    python craigslist-checker.py <search-term> [<phone-number>]

It's useful to setup a cronjob that will run the script every N minutes.

Notes
-----
GMail is getting picky about access, per http://joequery.me/guides/python-smtp-authenticationerror/.  You may need to disable CAPTCHA on your account at https://accounts.google.com/DisplayUnlockCaptcha

Phone number is now optional.  When present code will mail SMS to phone number; when absent code will access email target in config.py file

Code now sends MIME, html and text.