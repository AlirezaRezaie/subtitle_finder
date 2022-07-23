# Author => minerva [1]
# [1]: https://github.com/alirezaRezaie/

import requests
from bs4 import BeautifulSoup
import threading
import argparse
from pick import pick
import asyncio
import aiohttp

# important variables
SUBTITLE_LINKS = []
THREADS = []

# a lambda function for bs4 abstraction (no use for now)
get_content = lambda link : BeautifulSoup(requests.get(link).content, 'html.parser')

"""  
this function reads the .zip file 
and extracts it's data (for later uses)
"""
#import zipfile
#from io import BytesIO
#from urllib.request import urlopen
#def get_files_of_zipfile(link):
#    resp = urlopen(link)
#    myzipfile = zipfile.ZipFile(BytesIO(resp.read()))
#    foofile = myzipfile.namelist()
#    return foofile

#initializing arg parser
parser = argparse.ArgumentParser(description='subtitle finder program!')
parser.add_argument(
      "-n","--name",
      nargs='*',
      metavar="subtitle's name",
      type=str
)
args = parser.parse_args()


async def get_subtitle_link(page_links,subtitle_name):
    async with aiohttp.ClientSession() as session:
        for link in page_links:
            async with session.get(link) as response:
                resp =  await response.read()
                SUBTITLE_LINKS.append(
                    BeautifulSoup(
                        resp.decode('utf-8'), 'html5lib'
                    ).find(
                        "a", {"id": "link-download"}
                    )['href'] + " " + f'(subtitle for {subtitle_name})'
                )

# searching the https://subtitlestar.com website for the subtitle links
def search_subtitle(name):
    soup = get_content("http://subtitlestar.com/?s={q}&post_type=post".format(q = name))
    mydivs = soup.find_all("div", {"class": "wapper-posts"})
    links = [elem.footer.div.a['href'] for elem in mydivs]
    asyncio.run(get_subtitle_link(links,name))

# if there is a name argument run the program
if args.name != None:
    search_query = args.name
    for name in search_query:
        t = threading.Thread(target=search_subtitle,args=(name,))
        THREADS.append(t)

# starting threads
for t in THREADS:
    t.start()
print("retrieving urls...")
# waiting all threads to complete
for t in THREADS:
    t.join()
print('done!!!')

# cool cli picking menu
title = 'Please choose your subtitle: '
option= pick(SUBTITLE_LINKS + ['[quit]'], title, indicator='=>')
if option == '[quit]':
    quit()
print(option)