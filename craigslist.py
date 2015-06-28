from bs4 import BeautifulSoup
from urllib2 import urlopen
from datetime import datetime
import csv
import sys
import os
import smtplib
import config

"""
EMAIL_ADDRESSES = [ "benjamin.hipple@gmail.com",
                    "inneekim@gmail.com",
                    "chris.hipple@gmail.com",
                    "alexanderthegracie@gmail.com"
                  ]
"""
EMAIL_ADDRESSES = [ "benjamin.hipple@gmail.com",
                    "inneekim@gmail.com",
                  ]

# Craigslist search URL
BASE_URL = ('http://newyork.craigslist.org/search/'
            '?sort=rel&areaID=11&subAreaID=&query={0}&catAbb=sss')

def parseResults(search_term):
    results = []
    search_term = search_term.strip().replace(' ', '+')
    search_url = BASE_URL.format(search_term)
    soup = BeautifulSoup(urlopen(search_url).read())
    rows = soup.find('div', 'content').find_all('p', 'row')
    for row in rows:
        url = 'http://newyork.craigslist.org' + row.a['href']

        price = row.find('span', class_='price') or ""
        if price != "": price = price.get_text()
        create_date = row.find('time').get('datetime')
        title = row.find_all('a')[1].get_text()
        results.append({'url': url, 'price': price, 'create_date': create_date, 'title': title})
    return results

def writeResults(results):
    """Writes list of dictionaries to file."""
    fields = results[0].keys()
    with open('results.csv', 'w') as f:
        dw = csv.DictWriter(f, fieldnames=fields, delimiter='|')
        dw.writer.writerow(dw.fieldnames)
        dw.writerows(results)

def hasNewRecords(results):
    current_posts = [x['url'] for x in results]
    fields = results[0].keys()
    if not os.path.exists('results.csv'):
        return True

    with open('results.csv', 'r') as f:
        reader = csv.DictReader(f, fieldnames=fields, delimiter='|')
        seen_posts = [row['url'] for row in reader]

    is_new = False
    for post in current_posts:
        if post in seen_posts:
            pass
        else:
            is_new = True
    return is_new

def sendEmail(addr, msg):
    fromaddr = "Craigslist Checker"
    toaddrs = addr
    msg = ("From: {0}\r\nTo: {1}\r\nSubject: {2}\r\n\r\n{3}").format(fromaddr, toaddrs, "New results hype!", msg)
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(config.email['username'], config.email['password'])
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()

def formatMsg(results, TERM):
    message = "Hey - there are new Craigslist posts for: {0}".format(TERM.strip())

    message = message + "\n\n" + "\n".join(map(lambda x: x['url'] + " : " +
        x['title'] + " " + x['price'] + "\n", results))
    return message

def getCurrentTime():
    return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    try:
        TERM = sys.argv[1]
    except:
        print "You need to include a search term\n"
        sys.exit(1)

    results = parseResults(TERM)
    results = filter(lambda res: res['price'] == "" or int(res['price'][1:]) < 500, results)

    # Send the SMS message if there are new results
    if hasNewRecords(results):
        message = formatMsg(results, TERM)

        print "[{0}] There are new results - sending email message at {0}".format(getCurrentTime())
        map(lambda addr: sendEmail(addr, message), EMAIL_ADDRESSES)
        writeResults(results)
    else:
        print "[{0}] No new results - will try again later".format(getCurrentTime())
