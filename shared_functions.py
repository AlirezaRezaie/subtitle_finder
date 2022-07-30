from lxml import etree
from urllib.parse import urlparse

# check if url is absolute because some hrefs
# are not and supposed to be completed
def is_absolute(url,website):
    if not bool(urlparse(url).netloc):
        return website+url
    else:
        return url

def get_elem_by_xpath(xpath,wrapper):
        return etree.HTML(str(wrapper)).xpath(xpath)