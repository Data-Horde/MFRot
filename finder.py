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
import pandas as pd

broken_links = set()
checked_links = set()
blank_links = []

#checked_file = None
#broken_file = None
checkedURLs = None
brokenURLs = None

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

    global brokenURLs, checkedURLs, broken_links, checked_links

    #checked_links.append(url)
    checked_links.add(url)

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

            #broken_links.append(url)
            broken_links.add(url)
            is_ok = False

            #write_broken = url + "," + str(url_request.status_code) + "\n"
            #broken_file.write(write_broken)
            brokenURLs = brokenURLs.append({'url': url, 'status_code': url_request.status_code, 'last_seen': LASTSEEN},ignore_index=True)
            #print("* Broken url: ", url)
            #print("")
            return None

        #write_checked = url + "," \
        #    + str(url_request.status_code) + "," + str(is_ok) + "\n"

        #checked_file.write(write_checked)
        checkedURLs = checkedURLs.append({'url': url, 'status_code': url_request.status_code, 'last_seen': int(time.time()*1000)},ignore_index=True)

def initialize():
    global broken_links
    print("TODO: Read Working URLs from last run")
    print("TODO: Replace `is_ok` with `last_seen` UNIX timestamp")

    print("TODO (LATER): OUTPUT TO SQLite DB as well!")

    #global checked_file, broken_file, headers_checked_file, headers_broken_file

    #checked_file = open(CHURL_PATH, "w")
    #headers_checked_file = "url" + "," + "status_code" + "," \
    #    + "is_ok" + "\n"
    
    #checked_file.write(headers_checked_file)

    #try:
    #    broken_file = open(BURL_PATH, "a+")
    #except:
    #    #if broken_file does not exist
    #    broken_file = open(BURL_PATH, "w")
    #    #headers_broken_file = "url" + "," + "status_code" + "\n"
    #    headers_broken_file = "url" + "," + "status_code" + "," + "last_seen" + "\n"
    #    broken_file.write(headers_broken_file)

    global checkedURLs, brokenURLs

    try:
        checkedURLs = pd.read_csv(CHURL_PATH,index_col=0)
    except:
        checkedURLs = pd.DataFrame({'url': [], 'status_code': [], 'last_seen': []})

    try:
        brokenURLs = pd.read_csv(BURL_PATH,index_col=0)
        broken_links = set(brokenURLs['url'].to_list())
        print(broken_links)
    except:
        brokenURLs = pd.DataFrame({'url': [], 'status_code': [], 'last_seen': []})

if __name__ == '__main__':
    
    #Database File
    #DBFile = sys.argv[1]

    #LIMIT URLs to check, recommended for debugging
    #LIMIT = -1
    #if len(sys.argv) > 2:
    #    LIMIT = sys.argv[2]

    parser = argparse.ArgumentParser(description="Check for dead links on MediaFire.")
    parser.add_argument("dbfile",type=str,help="Path to database file downloaded from https://urls.ajay.app/.")
    parser.add_argument("-b","--brokenurls",type=str,help="Path to csv of broken urls.")
    parser.add_argument("-c","--checkedurls",type=str,help="Path to csv of checked urls.")
    parser.add_argument("-L","--limit",type=int,help="Limit of max links to check, meant for debugging.")
    #parser.add_argument("-br","--brokenURLs",type=int,help="TBA")
    parser.add_argument("-l","--lastexecution",type=float,help="UNIX Timestamp of Last Execution.\nThis is used for labeling when a broken link was last seen.")
    args = parser.parse_args()
    #print(args)

    #SET LIMIT, DBFILE and LAST SEEN

    DBFile, LIMIT, LASTSEEN = args.dbfile, (args.limit or -1), (str(args.lastexecution) or "n/a")

    BURL_PATH, CHURL_PATH = (args.brokenurls or "broken_urls.csv"), (args.checkedurls or "checked_urls.csv")
    #print(BURL_PATH, CHURL_PATH)

    initialize()

    #quit()

    print("Reading: ", DBFile)
    print("--------------------------------------------------")
    N = s.read_SQLite_DB(DBFile,"url","urls",LIMIT)

    print("Started at {}\n".format(int(time.time()*1000.0)))

    #LASTSEEN 1612126565 

    for i in tqdm (range (N), desc="Checking URLs in {}".format(DBFile)):
        targetURL = s.getList()[i]

        #print(targetURL,broken_links)
        if targetURL in broken_links:
            #print("Link is already broken skipping!")
            continue
            #print(targetURL)
        read_url(targetURL)

    summary()

    #checkedURLs.reset_index(drop=False)
    #brokenURLs.reset_index(drop=False)

    print(checkedURLs)

    checkedURLs.to_csv(CHURL_PATH)
    brokenURLs.to_csv(BURL_PATH)
    #checked_file.close()
    #broken_file.close()
