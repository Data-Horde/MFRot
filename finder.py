import requests
from bs4 import BeautifulSoup
import sldextract as s
import sys
import normalizer as n

import sqlite3 as sql
from tqdm import tqdm
import time
import urllib.parse

import argparse

broken_links = []
checked_links = []
blank_links = []

checked_file = None
broken_file = None

headers_checked_file = ""
headers_broken_file = ""

main_url = ""


def summary():
    print()
    print("Ended at {}\n".format(int(time.time()*1000.0)))
    print("Summary")
    print("--------------------------------------------------")
    print("Links Checked: \t", len(checked_links))
    print("Broken Links: \t", len(broken_links))
    print("Link Rot: \t{0:.2f}%".format(0 if not len(checked_links) else len(broken_links)
          / len(checked_links) * 100))
    print("--------------------------------------------------")

def read_url(url):

    checked_links.append(url)

    # check normalizer.py mailto: condition
    if url is not None:
        try:
            #enc_url = urllib.parse.quote(url)
            #enc_url = url.replace(" ","%20")
            #print(enc_url)
            #url_request = requests.get(enc_url)
            url_request = requests.get(url,stream=True)
        except Exception:
            print("Could not read url...")
            return None
        #print("...done")

        #if url != main_url:
            #print("Checking: ", url)
        #    url_domain = s.extract(url)["url_domain"]
        #else:
        #    url_domain = main_url_domain

        is_ok = True

        if url_request.status_code >= 400:

            broken_links.append(url)
            is_ok = False

            write_broken = url + "," + str(url_request.status_code) + "\n"
            broken_file.write(write_broken)
            #print("* Broken url: ", url)
            #print("")
            return None

        write_checked = url + "," \
            + str(url_request.status_code) + "," + str(is_ok) + "\n"

        checked_file.write(write_checked)

def initialize():

    print("TODO: Read Broken URLs from last run")

    print("TODO (LATER): OUTPUT TO SQLite DB as well!")
    global checked_file, broken_file, headers_checked_file, headers_broken_file

    checked_file = open("checked_urls.csv", "w")
    headers_checked_file = "url" + "," + "status_code" + "," \
        + "is_ok" + "\n"
    
    checked_file.write(headers_checked_file)

    try:
        broken_file = open("broken_urls.csv", "rw")
    except:
        #if broken_file does not exist
        broken_file = open("broken_urls.csv", "w")
        #headers_broken_file = "url" + "," + "status_code" + "\n"
        headers_broken_file = "url" + "," + "status_code" + "," + "last_seen" + "\n"
        broken_file.write(headers_broken_file)

if __name__ == '__main__':
    
    initialize()
    
    #Database File
    #DBFile = sys.argv[1]

    #LIMIT URLs to check, recommended for debugging
    #LIMIT = -1
    #if len(sys.argv) > 2:
    #    LIMIT = sys.argv[2]

    parser = argparse.ArgumentParser(description="Check for dead links on MediaFire.")
    parser.add_argument("dbfile",type=str,help="Path to database file downloaded from https://urls.ajay.app/.")
    parser.add_argument("-l","--limit",type=int,help="Limit of max links to check, meant for debugging.")
    #parser.add_argument("-br","--brokenURLs",type=int,help="TBA")
    parser.add_argument("-le","--lastexecution",type=float,help="UNIX Timestamp of Last Execution.\nThis is used for labeling when a broken link was last seen.")
    args = parser.parse_args()
    print(args)

    #SET LIMIT, DBFILE and LAST SEEN
    print("TODO: SET LIMIT, DBFILE and LAST SEEN")
    quit()

    print("Reading: ", DBFile)
    print("--------------------------------------------------")
    N = s.read_SQLite_DB(DBFile,"url","urls",LIMIT)

    print("Started at {}\n".format(int(time.time()*1000.0)))

    print("TODO: CHECK IF targetURL was not broken before!") 

    for i in tqdm (range (N), desc="Checking URLs in {}".format(DBFile)):
        targetURL = s.getList()[i]
        #print(targetURL)

        read_url(targetURL)

    summary()

    checked_file.close()
    broken_file.close()


#### UNUSED BEGIN

def read_url_legacy(url):

    checked_links.append(url)

    url = n.normalize(url, main_url_domain, main_url_ext)

    # check normalizer.py mailto: condition
    print("Fetching page at {}...".format(url), end='')
    if url is not None:
        try:
            url_request = requests.get(url)
        except Exception:
            print("Could not read url...")
            return None
        print("...done")

        if url != main_url:
            print("Checking: ", url)
            url_domain = s.extract(url)["url_domain"]
        else:
            url_domain = main_url_domain

        is_ok = True

        if url_request.status_code >= 400:

            broken_links.append(url)
            is_ok = False

            #write_broken = url + "," + str(url_request.status_code) + "\n"

            #EDIT THIS TO LAST TIMESTAMP
            write_broken = url + "," + str(url_request.status_code) + "," + "WHEN LAST SEEN" + "\n"

            broken_file.write(write_broken)
            print("* Broken url: ", url)
            print("")
            return None

        soup = BeautifulSoup(url_request.content, "html.parser", from_encoding="iso-8859-1")

        print("Looking for links on the webpage...", end='')
        url_list = soup.find_all('a', href=True)
        print("...done")
        print("")

        write_checked = url + "," \
            + str(url_request.status_code) + "," + str(is_ok) + "\n"

        checked_file.write(write_checked)

        if url_domain == main_url_domain:
            for link in url_list:
                if not link['href']:
                    continue

                if link['href'] not in checked_links:
                    read_url(link['href'])

#### UNUSED END
