from bs4 import BeautifulSoup
from urllib2 import urlopen
from datetime import datetime
import csv
import sys
import os
import smtplib
import config

## ============================================================================
##                          Configurable Variables
## ============================================================================
# Addresses to which results should be emailed
EMAIL_ADDRESSES = [ "benjamin.hipple@gmail.com",
                  ]

# Search queries to execute
QUERIES = ["bicycle 60cm"]

# Maximum price; items with no price will still be shown
MAX_PRICE = 1200

# Craigslist search URL
BASE_URL = ('http://newyork.craigslist.org/search/'
            '?sort=rel&areaID=11&subAreaID=&query={0}&catAbb=sss')

# Sender email and password are included from config.py
## ============================================================================

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

def filterToNewPosts(results):
    current_posts = [x['url'] for x in results]
    fields = results[0].keys()
    if not os.path.exists('results.csv'):
        return True

    with open('results.csv', 'r') as f:
        reader = csv.DictReader(f, fieldnames=fields, delimiter='|')
        seen_posts = [row['url'] for row in reader]

    newPosts = filter(lambda post: post['url'] not in seen_posts, results)
    return newPosts

def sendEmail(addr, msg):
    fromaddr = "Craigslist Checker"
    toaddrs = addr
    msg = ("From: {0}\r\nTo: {1}\r\n\r\n{2}").format(fromaddr, toaddrs, msg)
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(config.email['username'], config.email['password'])
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()

def formatMsg(results):
    message = "Hey - there are new Craigslist posts!"

    message = message + "\n\n" + "\n".join(map(lambda x: x['title'] + "\n" + x['url'] +
        "\n" + x['price'] + "\n", results))

    return message

def getCurrentTime():
    return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':

    results = []
    map(lambda term: results.extend(parseResults(term)), QUERIES)
    results = filter(lambda res: res['price'] == "" or int(res['price'][1:]) <= MAX_PRICE, results)
    # Send the SMS message if there are new results
    newPosts = filterToNewPosts(results)
    if len(newPosts):
        message = formatMsg(newPosts)

        print "[{0}] There are new results - sending email message".format(getCurrentTime())
        map(lambda addr: sendEmail(addr, message), EMAIL_ADDRESSES)
        writeResults(results)
    else:
        print "[{0}] No new results - will try again later".format(getCurrentTime())
