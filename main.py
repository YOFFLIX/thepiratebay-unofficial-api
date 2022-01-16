from bs4 import BeautifulSoup
import concurrent.futures
import itertools
import requests
import json
import math
import re


class ThePirateBayApi:

    def __init__(self, base_url="https://thepiratebay.party/"):
        self.base_url = base_url

    # Scraping Methods

    def _get_soup(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        return soup

    def _get_div(self, soup):
        return soup.find("div", {"id": "main-content"})

    def _get_trs(self, soup):
        div = self._get_div(soup)
        trs = div.find_all("tr")
        return trs
    
    # Fetch Methods

    def _get_number_of_total_results(self, soup):
        h2 = soup.find("h2").text
        total_results_re = re.search(r"(?<=approx )(.*)(?= found)", h2)
        total_results = int(total_results_re.group(1)
                            ) if total_results_re else 0

        return int(total_results)

    def _find_number_of_pages(self, soup):
        total_results = self._get_number_of_total_results(soup)
        if total_results > 1050:
            return 35
        else:
            return int(math.ceil(total_results / 30))

    def _get_torrent_informations(self, tr):
        # Category, Name, Upload Date, Size, SE, LE, Author
        torrent_infos_list = list(filter(None, [x.text for x in tr.find_all("td")]))
        torrent_infos_dict = {
            "Category": torrent_infos_list[0],
            "Name": torrent_infos_list[1].replace("\n", ""),
            "Upload Date": torrent_infos_list[2].replace("\xa0", " "),
            "Size": torrent_infos_list[3].replace("\xa0", " "),
            "SE": torrent_infos_list[4],
            "LE": torrent_infos_list[5],
            "Author": torrent_infos_list[6],
            "Magnet Url": tr.find_all("a")[2]["href"]
        }

        return torrent_infos_dict

    def _get_torrents_from_url(self, url, one_page=False):
        soup = self._get_soup(url)

        trs = self._get_trs(soup)[1:] if one_page else self._get_trs(soup)[1:-1]
        torrents = [self._get_torrent_informations(x) for x in trs]

        return torrents

    def search(self, query, category=0):
        query = re.sub(" +", "%20", query.strip())
        url = f"{self.base_url}search/{query}/1/99/{category}"

        soup = self._get_soup(url)

        number_of_pages = self._find_number_of_pages(soup)

        print(number_of_pages)

        if number_of_pages == 0:
            print("0 results found...")
        elif number_of_pages == 1:
            results = self._get_torrents_from_url(url, one_page=True)

            results_json = json.dumps(results, indent=4)

            with open("test.json", "w") as file:
                file.write(results_json)
        else:
            urls = [
                f"{self.base_url}search/{query}/{x}/99/{category}" for x in range(
                    1, number_of_pages + 1)
            ]

            results = []

            with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_pages) as pool:
                for x in pool.map(self._get_torrents_from_url, urls):
                    results.append(x)

            results = list(itertools.chain.from_iterable(results))
            print(len(results))

            results_json = json.dumps(results, indent=4)

            with open("test.json", "w") as file:
                file.write(results_json)


api_instance = ThePirateBayApi()

while True:

    inp = input()
    cat_inp = int(input())
    api_instance.search(inp, cat_inp)