import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_all_ebooks_links() -> list[str]:
    ebooks_url = "https://www.marxists.org/ebooks/"
    res = requests.get(ebooks_url)

    soup = BeautifulSoup(res.content, 'html.parser')

    document_links = []
    special_links = []

    for link in soup.find_all('a'): # "mobi", "azw3", "prc", "azw"
        if (link.text in ["pdf", "epub", ]):
            if link['href'] not in document_links:
                document_links.append(
                        urljoin(ebooks_url, str(link['href']))
                        )

        elif (link.text.endswith("in all formats")):
            if link['href'] not in special_links:
                special_links.append(
                        urljoin(ebooks_url , str(link['href'])))

    for l in special_links:
        url = urljoin(ebooks_url, l)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')

        for link in soup.find_all('a'): # "mobi", "azw3", "prc", "azw"
            if (link.text in ["pdf", "epub", ]):
                if link not in document_links:
                    document_links.append(urljoin(url, str(link["href"])))

    return document_links

def get_processed_ebooks_links():
    links_dics = []

    # get_all_ebooks_links()
    for link in get_all_ebooks_links():
        dic = {}
        dic["link"] = link
        dic["format"] = link.rsplit('.',1)[-1]

        dic['title'] = link.rsplit('/',1)[-1]  \
                        .split(".epub")[0]     \
                        .split(".pdf")[0]      \
                        .replace("-"," ")      \
                        .replace("_"," ")      \
                        .replace("%20"," ")
        dic["author"] = link.rsplit('archive',1)[-1] \
                            .rsplit('ebooks',1)[-1]  \
                            .rsplit('/')[1]

        links_dics.append(dic)

    return links_dics
