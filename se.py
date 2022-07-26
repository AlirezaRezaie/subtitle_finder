from PyQt5 import QtWidgets, uic
import sys
import threading
import json
import requests
from bs4 import BeautifulSoup
import threading
import asyncio
import aiohttp
import re
import json
import time

def attribute_selector(children,class_):
    holder = class_
    for child in children:
        holder = getattr(class_,child)
    return holder

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

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        self.setFixedSize(640, 480)
        uic.loadUi('subtitle Project.ui', self)
        self.THREADS = []
        self.SUBTITLE_LINKS = []
        self.website_name = "subtitlestar"
        f = open('supportedwebsites.json')
        self.website_info = json.load(f)
        f.close()
        self.menu = self.findChild(QtWidgets.QMenuBar,'menu')
        self.button = self.findChild(QtWidgets.QPushButton, 'pushButton') # Find the button
        self.button.clicked.connect(self.start)
        self.input = self.findChild(QtWidgets.QLineEdit, 'Input')
         # Remember to pass the definition/method, not the return value!

        self.show()
    
    async def get_subtitle_link(self, page_links,subtitle_name):
        async with aiohttp.ClientSession() as session:
            for link in page_links:
                try:
                    async with session.get(link) as response:
                        resp =  await response.read()
                        link_wrapper = BeautifulSoup(
                                resp.decode('utf-8'), 'html5lib'
                        )
                        
                        for pattern in self.website_info[self.website_name]['download_link_element']:
                            download_btn = link_wrapper.find(*pattern)
                            try:
                                url = re.search(r'href=["\']?([^"\'>]+)["\']?',download_btn.decode()).groups()
                                self.SUBTITLE_LINKS.append(url[0]+f" (subtitle for {subtitle_name})")
                                break
                            except:
                                pass
                except aiohttp.ClientConnectionError as e:
                    print("connection error")

    def search_subtitle(self,name):
        soup = get_content(self.website_info[self.website_name]['link'].format(q = name))
        elems = soup.find_all(*self.website_info[self.website_name]['search_scraper'])
        links = [attribute_selector(self.website_info[self.website_name]['children'],elem)['href'] for elem in elems]
        asyncio.run(self.get_subtitle_link(links,name))

    def start(self):
        # This is executed when the button is pressed
        names_list = self.input.text()
        for name in names_list.split():
            t = threading.Thread(target=self.search_subtitle,args=(name,))
            self.THREADS.append(t)
        # starting threads
        for t in self.THREADS:
            t.start()
        print("retrieving urls...")
        self.show()
        # waiting all threads to complete
        for t in self.THREADS:
            t.join()
        self.THREADS.clear()
        self.input.setText("")
        print(self.SUBTITLE_LINKS)
        self.SUBTITLE_LINKS = []


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
