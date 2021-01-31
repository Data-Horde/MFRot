import requests
from bs4 import BeautifulSoup
import sldextract as s
import sys
import normalizer as n

import sqlite3 as sql

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
    print("Summary")
    print("--------------------------------------------------")
    print("URL: \t\t", main_url)
    print("URL Domain: \t", main_url_domain)
    print("URL Extension: \t", main_url_ext)
    print("Links Checked: \t", len(checked_links))
    print("Broken Links: \t", len(broken_links))
    print("Link Rot: \t{0:.2f}%".format(0 if not len(checked_links) else len(broken_links)
          / len(checked_links) * 100))
    print("--------------------------------------------------")


def read_url(url):

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

            write_broken = url + "," + str(url_request.status_code) + "\n"
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


def initialize():
    print("TODO: OUTPUT TO SQLite DB as well!")
    global checked_file, broken_file, headers_checked_file, headers_broken_file

    checked_file = open("checked_urls.csv", "w")
    broken_file = open("broken_urls.csv", "w")

    headers_checked_file = "url" + "," + "status_code" + "," \
        + "is_ok" + "\n"
    headers_broken_file = "url" + "," + "status_code" + "\n"

    checked_file.write(headers_checked_file)
    broken_file.write(headers_broken_file)


if __name__ == '__main__':
    
    initialize()
    
    DBFile = sys.argv[1]

    print("Reading: ", DBFile)
    print("--------------------------------------------------")
    s.read_SQLite_DB(DBFile,"url","urls")

    print("Starting...\n")
    print("Checking ", DBFile)

    """
    main_url_domain, main_url_ext = s.extract(main_url).values()
    read_url(main_url)

    summary()
    checked_file.close()
    broken_file.close()
    """
