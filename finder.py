import requests
from bs4 import BeautifulSoup
import sldextract as s
import sys
import normalizer as n


broken_links = []
checked_links = []
blank_links = []

checked_file = None
broken_file = None

headers_checked_file = ""
headers_broken_file = ""

main_url = ""


def read_url(url):

    checked_links.append(url)
    url = n.normalize(url, main_url_domain, main_url_ext)

    # check normalizer.py mailto: condition
    if url is not None:
        try:
            url_request = requests.get(url)
        except Exception:
            print("Could not read url")
            return None

        print("Extracting details from: ", url)
        url_domain = s.extract(url)["url_domain"]

        is_ok = True

        if url_request.status_code >= 400:

            broken_links.append(url)
            is_ok = False

            write_broken = url + "," + str(url_request.status_code) + "\n"
            broken_file.write(write_broken)

        soup = BeautifulSoup(url_request.content, "html.parser", from_encoding="iso-8859-1")

        url_list = soup.find_all('a', href=True)

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
    s.read_tld_list()
    main_url = sys.argv[1]
    print("Extracting details from ", main_url)
    main_url_domain, main_url_ext = s.extract(main_url)

    read_url(main_url)
    checked_file.close()
    broken_file.close()
