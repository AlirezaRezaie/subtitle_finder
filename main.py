# Author => minerva [1]
# [1]: https://github.com/alirezaRezaie/

import requests
from bs4 import BeautifulSoup
import threading
import argparse
from pick import pick
import asyncio
import aiohttp
import re

def attribute_selector(children,class_):
    holder = class_
    for child in children:
        holder = getattr(class_,child)
    return holder

# important variables
SUBTITLE_LINKS = []
THREADS = []

# subtitle websites support
website_info = {
        'worldsubtitle':{
            'link':"https://worldsubtitle.me/?s={q}",
            'search_scraper':["div", {"class": "cat-post-titel"}],
            'children':['h2','a'],
            'download_link_element':[["div", {"class": "new-link-3"},["ul",{"class","download1"}]]]
            
        },
        'subtitlestar':{
            'link':"http://subtitlestar.com/?s={q}&post_type=post",
            'search_scraper':["div", {"class": "wapper-posts"}],
            'children':['footer','div','a'],
            'download_link_element':[["a", {"id": "link-download"}]]
        }
    }

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
            async with session.get(link) as response:
                resp =  await response.read()
                link_wrapper = BeautifulSoup(
                        resp.decode('utf-8'), 'html5lib'
                )
                
                for pattern in website_info[website_name]['download_link_element']:
                    download_btn = link_wrapper.find(*pattern)
                    try:
                        url = re.search(r'href=["\']?([^"\'>]+)["\']?',download_btn.decode()).groups()
                        SUBTITLE_LINKS.append(url[0]+f" (subtitle for {subtitle_name})")
                    except:
                        pass

# searching the supported websites for the subtitle links
def search_subtitle(name):
    soup = get_content(website_info[website_name]['link'].format(q = name))
    elems = soup.find_all(*website_info[website_name]['search_scraper'])
    links = [attribute_selector(website_info[website_name]['children'],elem)['href'] for elem in elems]
    asyncio.run(get_subtitle_link(links,name))

if __name__ == "__main__":
    global website_name
    if args.site != None:
        website_name = args.site[0]
    else:
        website_name='worldsubtitle'

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