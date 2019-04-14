#!/usr/bin/env python3
# coding: utf-8

import os
from urllib.parse import urlparse as uparse

import requests
from bs4 import BeautifulSoup as bs

start_urls = [
    "https://www.franceinter.fr/emissions",
    "https://www.franceculture.fr/emissions"
]


def get_programs(start_page):
    '''from alphabetical list collect the available programs along with the podcast url page'''
    root_page = uparse(start_page).netloc
    print(root_page)
    r = requests.get(start_page)
    soup = bs(r.text, "lxml")
    for program in soup.find_all("li", {"class": "concept-item"}):
        link = program.a.get("href")
        title = program.find('span', {"class": "title"}).text
        short_description = program.p.text
        p = {
            "url": "https://" + root_page + link,
            "title": title,
            "short_description": short_description
        }
        print(p["url"])
        r2 = requests.get(p["url"])
        print(r2)
        if r2.status_code < 400:
            soup2 = bs(r2.text, "lxml")
            podcast_block_list = soup2.find(
                "ul", {"class": "podcast-links-group"}
                )
            if podcast_block_list is not None:
                try:
                    p["podcast_url"] = podcast_block_list.find_all(
                        "li")[1].a.get("href")
                except IndexError:
                    p["podcast_url"] = podcast_block_list.a.get("href")
        yield p

def get_podcasts(program):
    '''
    <item>
        <title>1606 : "Le Roi Lear", une pièce barbare ?</title>
        <link>https://www.franceculture.fr/</link>
        <description>durée : 00:08:16 - 1606 : "Le Roi Lear", une pièce barbare ? - En direct des grands chocs esthétiques de l'histoire des arts et de la culture, Mathilde Serrell est aujourd'hui en 1606, lorsque Shakespeare met en scène &quot;Le Roi Lear&quot; pour la première fois au Palais de Whitehall de Londres : une pièce hybride, jugée de mauvais goût.</description>
        <author>podcast@radiofrance.com</author>
        <category>Arts </category>
        <enclosure url="http://rf.proxycast.org/1557753733729755136/19724-12.04.2019-ITEMA_22034229-0.mp3" length="8013824" type="audio/mpeg"/>
        <guid>http://media.radiofrance-podcast.net/podcast09/19724-12.04.2019-ITEMA_22034229-0.mp3</guid>
        <pubDate>Fri, 12 Apr 2019 06:00:00 +0200</pubDate>
        ...
    </item>
    '''
    program["podcasts"] = []
    r = requests.get(program["podcast_url"])
    soup = bs(r.text, "lxml")
    for podcast in soup.find_all("item"):
        p = {}
        p["title"] = podcast.title.text.strip()
        p["description"] = podcast.description.text.strip()
        p["category"] = podcast.category.text.strip()
        p["media_url"] = podcast.enclosure.get("url")
        p["guid"] = podcast.guid
        yield p
    
if __name__ == "__main__":
    for u in start_urls:
        for prg in get_programs(u):
            for pod in get_podcasts(prg):
                print(pod)