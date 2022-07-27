from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThread,pyqtSignal
import sys
import json
import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import re
import json
import time


# goes through nested elements as a list
# and returns the last one [child1, child2, child3]
#<child1>
#   <child2> 
#       </child3> <== selects this
#   </child2>
#</child1>
def attribute_selector(children,class_):
    holder = class_
    for child in children:
        holder = getattr(class_,child)
    return holder


# a wait thread for making sure 
# if all worker threads are done
class Waitor(QThread):
    def __init__(self, threads):
        super().__init__()
        self.threads = threads
     
    def run(self):
        while True:
            if not any(t.isRunning() for t in self.threads): 
                break


class Worker(QThread):
    # this signal return scraped subtitles as a list [self.SUBTITLE_LINKS]
    response = pyqtSignal(list)
    # this signal will be emmited whenever an error accoured
    error_msg = pyqtSignal(str)
    def __init__(self, sub_name):
        super().__init__()
        self.SUBTITLE_LINKS = []
        self.website_name = "subtitlestar"
        self.name = sub_name
        # reading and loading the supported websites
        f = open('supportedwebsites.json')
        self.website_info = json.load(f)
        f.close()

    async def get_subtitle_link(self, page_links,subtitle_name):
        async with aiohttp.ClientSession() as session:
            for link in page_links:
                try:
                    async with session.get(link) as response:
                        resp =  await response.read()
                        link_wrapper = BeautifulSoup(
                            resp.decode('utf-8'),
                            'html5lib'
                        )
                        for pattern in self.website_info[self.website_name]['download_link_element']:
                            download_btn = link_wrapper.find(*pattern)
                            try:
                                url = re.search(r'href=["\']?([^"\'>]+)["\']?',download_btn.decode()).groups()
                                self.SUBTITLE_LINKS.append(url[0]+f" (subtitle for {subtitle_name})")
                                # break if the pattern is true because no error
                                break
                            except:
                                pass

                except aiohttp.ClientConnectionError as e:
                    print(f"connection error {e}")

    def run(self):
        print("started")
        soup = None
        error_count = 0
        max_error_count = 10
        # running the request [max_error_count] times 
        # if there is a connection error
        for _ in range(0,max_error_count):
            time.sleep(1)
            try:
                   soup =  BeautifulSoup(
                    requests.get(
                        # reading the website's scraper string form database 
                        # and passing the query to it
                        self.website_info[self.website_name]['link'].format(q = self.name)
                   ).content, 'html.parser')
                   # break the retry loop if no error
                   break
            except:
                # increasing the error count and emmiting the error counter
                # to the UI for showing the error
                error_count += 1
                msg = "\rretrying " + str(error_count)
                self.error_msg.emit(msg)
        
        # check if limit has reached and end the search because there is no connection
        if not error_count == max_error_count:
            self.error_msg.emit("ok")
            elems = soup.find_all(*self.website_info[self.website_name]['search_scraper'])
            links = [attribute_selector(self.website_info[self.website_name]['children'],elem)['href'] for elem in elems]
            asyncio.run(self.get_subtitle_link(links,self.name))
            self.response.emit(self.SUBTITLE_LINKS)
            self.SUBTITLE_LINKS.clear()
        else:
            self.error_msg.emit("please retry")


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        self.setFixedSize(640, 640)
        uic.loadUi('subtitle Project.ui', self)
        self.THREADS = []
        self.SUBTITLE_LINKS_ALL = []
        self.menu = self.findChild(QtWidgets.QMenuBar,'menu')
        self.button = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.button.clicked.connect(self.start)
        self.input = self.findChild(QtWidgets.QLineEdit, 'Input')
        self.show()
    
    def handle_on_threads_end(self):
        self.input.setText('')
        self.button.setEnabled(True)
        print(self.SUBTITLE_LINKS_ALL)
        self.SUBTITLE_LINKS_ALL.clear()
        self.THREADS.clear()

    def error_handler(self,err_msg):
        print(err_msg,end='')        

    def start(self):
        names_list = self.input.text()
        # start a worker for each subtitle name
        for name in names_list.split():
            self.THREADS.append(Worker(name,))
        # start all threads
        for t in self.THREADS:
            t.start()
        # connect signals to their handler
        for t in self.THREADS:
            t.response.connect(lambda sub_links : self.SUBTITLE_LINKS_ALL.append(sub_links))
            t.error_msg.connect(self.error_handler)

        # defining waitor thread and starting it
        self.queue = Waitor(self.THREADS)
        self.queue.start()
        self.button.setEnabled(False)
        # if waitor ends it means all threads ended
        self.queue.finished.connect(self.handle_on_threads_end)
        

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()