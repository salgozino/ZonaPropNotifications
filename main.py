# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from hashlib import sha1
from urllib.parse import urlparse
from dataclasses import dataclass
import cloudscraper

scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance

# Cambiar URLs por las busquedas deseadas segun lo que se está buscando
urls = {
    "https://www.argenprop.com/departamento-y-ph-alquiler-barrio-palermo-barrio-br-norte-2-dormitorios-y-3-dormitorios-hasta-45000-pesos-desde-55-m2-cubiertos",
    "https://www.zonaprop.com.ar/departamentos-alquiler-recoleta-mas-de-3-ambientes-menos-40000-pesos.html"
}


@dataclass
class Parser:
    website: str
    link_regex: str

    def extract_links(self, contents: str):
        soup = BeautifulSoup(contents, "lxml")
        ads = soup.select(self.link_regex)
        for ad in ads:
            if 'data-to-posting' in self.link_regex:
                href = ad["data-to-posting"]
            else:
                href = ad["href"]
            _id = sha1(href.encode("utf-8")).hexdigest()
            yield {"id": _id, "url": "{}{}".format(self.website, href)}


parsers = [
    Parser(website="https://www.zonaprop.com.ar",
           link_regex="div[data-to-posting]"),
    Parser(website="https://www.argenprop.com",
           link_regex="div.listing__items div.listing__item a"),
    Parser(website="https://inmuebles.mercadolibre.com.ar",
           link_regex="li.results-item .rowItem.item a"),
]


def _main():
    for url in urls:
        res = scraper.get(url)
        # res = requests.get(url)
        ads = list(extract_ads(url, res.text))
        seen, unseen = split_seen_and_unseen(ads)

        print("{} seen, {} unseen".format(len(seen), len(unseen)))

        for u in unseen:
            notify(u)

        mark_as_seen(unseen)


def extract_ads(url, text):
    uri = urlparse(url)
    parser = next(p for p in parsers if uri.hostname in p.website)
    return parser.extract_links(text)


def split_seen_and_unseen(ads):
    history = get_history()
    seen = [a for a in ads if a["id"] in history]
    unseen = [a for a in ads if a["id"] not in history]
    return seen, unseen


def get_history():
    try:
        with open("seen.txt", "r") as f:
            return {line.rstrip() for line in f.readlines()}
    except Exception:
        return set()


def notify(ad):
    bot = None  # Completar con el token del bot
    room = None  # Completar con la sala donde enviar los mensajes
    url = f"https://api.telegram.org/bot{bot}/sendMessage?chat_id={room}"\
          f"&text={ad['url']}"
    if bot is not None and room is not None:
        requests.get(url)
    else:
        print(f"\n Nuevo resultado encontrado!: {ad['url']}")


def mark_as_seen(unseen):
    with open("seen.txt", "a+") as f:
        ids = ["{}\n".format(u["id"]) for u in unseen]
        f.writelines(ids)


if __name__ == "__main__":
    _main()