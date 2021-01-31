import sqlite3 as sql

tld_list = []
tld_cache_list = []


"""
def read_tld_list():
    global tld_list

    with open("tld.txt", 'r') as f:
        tld_list = [line.rstrip(',\n') for line in f]
"""

def read_SQLite_DB(filename, index, table, LIMIT=-1):
    global tld_list

    print("TODO: REMOVE DUPLICATE URLs")

    conn = sql.connect(filename)
    if LIMIT == -1:
        cursor = conn.execute("SELECT {} from {}".format(index,table))
    else:
        cursor = conn.execute("SELECT {} from {} LIMIT {}".format(index,table,LIMIT))
    tld_list = [x[0] for x in cursor]
    #print(tld_list[1156:1160])
    conn.close()

    return len(tld_list)

def getList():
    return tld_list

def extract(url):

    url = url.replace("https://", "")
    if '/' in url:
        url = url[:url.index('/')]

    for i in tld_cache_list:
        if url.endswith(i):
            url_tld = i
            url = url.replace(url_tld, "")
            break

    else:
        for i in tld_list:
            if url.endswith(i):

                url_tld = i
                tld_cache_list.append(i)
                url = url.replace(url_tld, "")
                break

        else:
            url_tld = ""

    url_domain = url.strip('.')

    url_contents = {
        "url_domain": url_domain,
        "url_tld": url_tld
        }

    return url_contents
