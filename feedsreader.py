"""Feedsreader.

Usage:
  feedsreader.py (-h | --help)
  feedsreader.py --version
  feedsreader.py <feedsfile> <output>

Options:
  -h --help     Show this screen.
  --version     Show vesion.


"""
from xml.etree.ElementTree import XML, ParseError
import string
import requests
from docopt import docopt
from dateutil.parser import parse
import datetime
import chardet
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DAYS_MAP = {
    "Lun," : "Mon,",
    "Mar," : "Tue,",
    "Mer," : "Wed,",
    "Gio," : "Thu,",
    "Ven," : "Fri,",
    "Sab," : "Sat,",
    "Dom," : "Sun,",
}

MONTHS_MAP = {
    "Nov" : "Nov",
    "Dic" : "Dec",
}



def readfeedurl(feedurl, date=None):
    """
    Read feed url and concat feed items titles
    """
    date = date or datetime.date.today()
    # Get raw feed string from feed url
    try:
        r = requests.get(feedurl)
    except Exception as e:
        logger.error('Error reading feed url: %s' % feedurl)
        return ''


    # TODO: Check encoding...
    encoding = chardet.detect(r.content)['encoding']

    #print(encoding)
    #return
    if encoding != 'utf-8':
        r.encoding = 'latin-1'
    else:
        r.encoding = 'utf-8'
    # Parse raw feed string to xml
    try:
        tree = XML(r.text.strip())
    except ParseError as e:
        logger.error('Error reading feed: %s' % feedurl)
        return ''

    

    index = 0
    feedtext = ''
    printable = set(string.printable)

    # Read rss items
    for node in tree.iter('item'):

        # Limit taken items
        node_date = node.find('pubDate').text
        node_date_pieces = node_date.split(" ")

        node_date_pieces = [ DAYS_MAP.get(piece, piece) for piece in node_date_pieces]
        node_date_pieces = [ MONTHS_MAP.get(piece, piece) for piece in node_date_pieces]
        node_date = " ".join(node_date_pieces)



        try:
            parsed_date = parse(node_date)

        except:
            print(node_date)
            continue

        if str(parsed_date.date()) != str(date):
            continue

        #if not index < take:
        #    break

        # Get title text from the item node
        titletext = node.find('title').text.strip()

        # Remove shitty characters from jsp fucking rss feeds...
        #titletext = ''.join(filter(lambda x: x in printable, titletext))

        feedtext += titletext + '\n'
        index += 1

    return feedtext

def readfeeds(feedsfile, date=None):
    with open(feedsfile, 'r') as infile:
        feedsurls = [line.strip() for line in infile.readlines()]
        feedstext = ''
        for feedurl in feedsurls:
            # try:
                feedstext += readfeedurl(feedurl, date)
                # print feedstext
                feedstext += '\n'
            # except:
                # TODO: Better error handling...
                # pass

        # print feedstext
        return feedstext


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Feedsreader 1.0')
    text = readfeeds(arguments['<feedsfile>'])
    with open(arguments['<output>'], "w") as outfile:
        outfile.write(text)
