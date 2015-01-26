from bs4 import BeautifulSoup
from urllib2 import urlopen
from datetime import datetime
import csv
import sys
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import config

# Craigslist search URL
#BASE_URL = ('http://chicago.craigslist.org/search/'
#            '?sort=rel&areaID=11&subAreaID=&query={0}&catAbb=sss')
BASE_URL = ('http://{0}/search/{2}'
            '?sort=rel=&query={1}')


def parse_results(search_term):
    results = []
    location_domain = config.terms['location_domain']
    cat_abb = config.terms['category_abb']
    search_term = search_term.strip().replace(' ', '+')
    search_url = BASE_URL.format(location_domain,search_term,cat_abb)
    # Because home url's are relative but out of area fully qualified
    home_location_url='http://' + location_domain

    soup = BeautifulSoup(urlopen(search_url).read())
    rows = soup.find('div', 'content').find_all('p', 'row')
    for row in rows:
        if row.a['href'].startswith('http'):
                url = row.a['href']
        else:
                url= home_location_url + row.a['href']
        # price = row.find('span', class_='price').get_text()
        # print url
        create_date = row.find('time').get('datetime')
        title = row.find_all('a')[1].get_text()
        results.append({'url': url, 'create_date': create_date, 'title': title})
    return results

def write_results(results):
    """Writes list of dictionaries to file."""
    fields = results[0].keys()
    with open('results.csv', 'w') as f:
        dw = csv.DictWriter(f, fieldnames=fields, delimiter='|')
        dw.writer.writerow(dw.fieldnames)
        dw.writerows(results)

def has_new_records(results):
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

def send_text(toaddrs, results):
        fromaddr = "Craigslist Checker"
        msg = MIMEMultipart('alternative')
        msg['Subject'] =  "Hey - there are new Craigslist posts for: {0}".format(TERM.strip())
        msg['From'] = "Automated Craigslist Monitor"
        msg['To'] = toaddrs

        # Create the body of the message (a plain-text and an HTML version).
        html =  """\
                <html>
                        <head></head>
                        <body>
                        <table>
        """
        text = '\n\n'
        for result in results:
                text = text +  '\n\n' + result['create_date'] + ' ' + result['title'] + ' ' + result['url']
                html = html + '<tr>' + '<td>' + result['create_date'] + '</td>' + '<td>' + result['title'] + '</td>' + '<td>' + result['url'] + '</td><tr>'
        html=html + """
                </table>
                </body>
                </html>
        """
        #print text
        #print html
        print "[{0}] There are new results - sending message to {0}".format(get_current_time(), toaddrs)

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        #msg = ("From: {0}\r\nTo: {1}\r\n\r\n{2}").format(fromaddr, toaddrs, msg)
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(config.email['username'], config.email['password'])
        server.sendmail(fromaddr, toaddrs, msg.as_string())
        server.quit()

def get_current_time():
    return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    TERM = sys.argv[1]
    print 'length is ' + str(len(sys.argv))
    if len(sys.argv) > 2:
        try:
                PHONE_NUMBER = sys.argv[2].strip().replace('-', '')
                toaddrs = PHONE_NUMBER + "@txt.att.net"
        except:
            print "You need to include a search term and a 10-digit phone number!\n"
            sys.exit(1)

        if len(PHONE_NUMBER) != 10:
            print "Phone numbers must be 10 digits!\n"
            sys.exit(1)
    else:
        toaddrs=(config.email['target_email'])

    results = parse_results(TERM)

    # Send the SMS message if there are new results
    if has_new_records(results):
        send_text(toaddrs, results)
        write_results(results)
    else:
        print "[{0}] No new results - will try again later".format(get_current_time())