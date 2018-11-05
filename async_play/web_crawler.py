import asks
import asks.errors
import curio
import logging
import re
import sys

from datetime import datetime
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

asks.init('curio')
http_regex = re.compile("^http[s]?://")


class PrintingSet(set):
    def add(self, element):
        super(PrintingSet, self).add(element)
        log.info(f"New element: {element}")


all_urls = PrintingSet()
get_counter = 0
stop_after_finding = 100
start_url = 'http://www.monzo.com/blog'


def generate_links_from_page(page_content):
    soup = BeautifulSoup(page_content, features="html.parser")
    for link in soup.find_all('a', attrs={'href': http_regex}):
        yield link.get('href')


async def crawl(url):
    global all_urls, get_counter, stop_after_finding

    if len(all_urls) > stop_after_finding:
        log.info(f"Not getting {url} as reached limit")
        return

    log.debug(f"Crawling from: {url}")
    log.debug(f"Done {get_counter} GETs")
    log.debug(f"Num found: {len(all_urls)}")

    sub_tasks = []

    get_counter += 1
    try:
        res = await asks.get(url)
    except asks.errors.BadHttpResponse:
        log.error("Bad HTTP response.")
        return
    for link in generate_links_from_page(res.content):
        if link not in all_urls:
            all_urls.add(link)
            log.debug(f"Found: {link}")
            sub_crawler = await curio.spawn(crawl, link)
            sub_tasks.append(sub_crawler)
        else:
            log.debug(f"skipped {link}")
    for task in sub_tasks:
        await task.join()


if __name__ == "__main__":
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(logging.DEBUG)
    log.addHandler(handler)
    now = datetime.now()
    print(f"Starting at: {now}")
    curio.run(crawl(start_url))
    print(f"Done in {(datetime.now() - now).total_seconds()}!")
