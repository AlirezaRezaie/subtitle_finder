# Author => minerva [1]
# [1]: https://github.com/alirezaRezaie/

import requests
from bs4 import BeautifulSoup
import threading
import argparse
from pick import pick
import asyncio
import aiohttp
import json
import time
from shared_functions import *

# important variables
SUBTITLE_LINKS = []
THREADS = []

# subtitle websites support
f = open('supportedwebsites.json')
website_info = json.load(f)
f.close()

# a lambda function for bs4 abstraction (no use for now)
def get_content(link):
    error_count = 0
    for _ in range(0,100):
        time.sleep(1)
        try:
            return BeautifulSoup(requests.get(link).content, 'html.parser')
        except:
            error_count += 1
            print ("\rretrying " + str(error_count) , end='')
    exit()
            

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
      metavar="subtitles name",
      type=str
)
parser.add_argument(
      "-s","--site",
      nargs=1,
      metavar="website name",
      type=str,
      choices={*[name for name in website_info]},
)
args = parser.parse_args()


async def get_subtitle_link(page_links,subtitle_name):
    async with aiohttp.ClientSession() as session:
        for link in page_links:
            nested_links_holder = [link]
            for xpaths in website_object['download_link_xpaths']:
                try:                
                    for index,xpath in enumerate(xpaths):   
                        for link in nested_links_holder:
                            async with session.get(link) as response: 
                                resp =  await response.read()
                                link_wrapper = BeautifulSoup(
                                        resp.decode('utf-8'), 'html5lib'
                                )
                                download_btns = get_elem_by_xpath(xpath,link_wrapper)
                                nested_links_holder = map(lambda x:is_absolute(x,website_object['link']),download_btns)
                                nested_links_holder = list(nested_links_holder)

                                if index+1 == len(xpaths):
                                    for download_link in nested_links_holder:
                                        # live data
                                        print(download_link,link)
                                        SUBTITLE_LINKS.append(download_link+f" (subtitle for {link})")
                    break
                except Exception as e:
                    print(e)
# searching the supported websites for the subtitle links
def search_subtitle(name):
    soup = get_content(website_object['search_link'].format(q = name))
    links = get_elem_by_xpath(website_object['post_link_xpaths'],soup)
    if not links == []:
        links = map(lambda x:is_absolute(x,website_object['link']),links)
        asyncio.run(get_subtitle_link(list(links),name))
    else:
        pass


if __name__ == "__main__":
    global website_name
    global website_object
    
    if args.site != None:
        website_name = args.site[0]
    else:
        website_name='worldsubtitle'
    website_object = website_info[website_name]
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

    # removing duplicates in the list for some bugs may happened
    SUBTITLE_LINKS = list(set(SUBTITLE_LINKS))
    # cool cli picking menu
    title = 'Please choose your subtitle: '
    if SUBTITLE_LINKS == []:
        print("no subtitle found")
        exit()
    option= pick(SUBTITLE_LINKS + ['[quit]'], title, indicator='=>')
    if option == '[quit]':
        quit()
    print(option)