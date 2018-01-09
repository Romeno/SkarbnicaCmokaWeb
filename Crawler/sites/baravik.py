import requests
import bs4 as bs
import re
from time import time, sleep
from random import random
from Crawler.models import Crawled_Film
from .baravik_patterns import *
from Crawler.tools.html import Soup_opener

class Library():
    def __init__(self, *args):

        # I SHOULD REWRITE film_lists with lib.__init__ method

        # These two links are enter-gates for crawler
        self.film_lists = [
        r'https://baravik.org/forum/31/',
        r'https://baravik.org/forum/8/'
        ]
        self.film_urls = []

    def get_film_lists(self):
        # All links can be iterated via url "next-page"
        # So this function finds Block with Navigation
        # and look for the Link with text "Наступная"
        for page_url in self.film_lists:
            with Soup_opener(page_url) as soup:
                navigation_block = soup.find('p', {'class':'paging'})
                navigation_links = navigation_block.find_all('a')

                for link in navigation_links:
                    if link.text == 'Наступная':
                        self.film_lists.append(link.attrs['href'])
                        break
                sleep(random()*10)


    def get_film_urls(self):
        # This function finds every film URL located on film-lists pages
        for page_url in self.film_lists:
            with Soup_opener(page_url) as soup:
                films_block = (
                    soup.find('div', {'id': 'forum31'}) or
                    soup.find('div', {'id': 'forum8'})
                    )
                urls = [
                    link.attrs['href'] for link in films_block.find_all('a') if 
                    link.attrs['href'].startswith(r'https://baravik.org/topic/')
                    ]
                # save film links
                for url in urls:
                    if url not in self.film_urls:
                        self.film_urls.append(url)
    
    def get_film_data(self):
        # This function finds Film information from Crawled_Film.film_urls
        # Uses patterns from baravik_patterns.py file
        for film_url in self.film_urls:
            with Soup_opener(film_url) as soup:
                # store all crawled info into crawled_items dict:
                crawled_items = {}
                # 1) Somehow @Length isn't always could be founded
                #    with methods below. So we'll catch it in global-html
                _length = re.findall(meta_patterns['length'], str(soup))
                crawled_items['length'] = _length[0] if _length else ''

                # 2) Extract name, name_origin and year from title
                for item, patterns in patterns_header.items():
                    for pattern in patterns:
                        found = re.findall(pattern, soup.title.text)
                        crawled_items[item] = found[0].strip() if found else ''
                        if found:
                            break

                # 3) crawl body elements
                #   - remove buggy div elements
                for div in soup.findAll('div', {'style':'border: 1px dotted gray; padding: 4px; color: #4a566e;'}):
                    div.replaceWith('')
                #   - get only needed block of content
                good_html = soup.find('div', {'class', 'entry-content'})
                #   - get image_url
                crawled_items['image_url'] = good_html.find('img').attrs['src']

                #  - remove useless underline span-blocks
                for span in good_html.find_all('span', {'class': 'bbu'}):
                    new_span = span.text
                    span.replaceWith(new_span)

                #  - unpack needed html contents to bs.elements
                nested_blocks = good_html.contents
                nested_blocks = [block for block in nested_blocks if type(block) != type(str)]
                extended_blocks = []
                for block in nested_blocks:
                    extended_blocks.extend(block)

                #   - подготовить текст для последующего использования в регулярных выражениях
                stable_text = ''
                for i, block in enumerate(extended_blocks):
                    if type(block) != bs.element.Tag:
                        continue
                    if i == len(extended_blocks):
                        break
                    # искомые strong элементы иемют класс bs4.element.Tag, а последующие, содержащие
                    # необходимую информацию, являются классами bs4.element.NavigableString
                    #   - извлечь текст из цепочки следующих bs.element.NavigableString и передать в stable-text
                    if type(block) == bs.element.Tag and block.name == 'strong':
                        # записать текст из STRONG тэга
                        stable_text += block.text
                        # пройтись по цепочке NavigableStrings и записать текст
                        next_index = 0
                        next_block = extended_blocks[i + next_index + 1]
                        while type(next_block) == bs.element.NavigableString:
                            stable_text += str(next_block)
                            next_index += 1
                            next_block = extended_blocks[i + next_index + 1]
                        # добавить разделитель в stable_text
                        stable_text += '\n'

                #  - use regexp to finally catch elements and store it in crawled_items dict
                for item, patterns in patterns_body.items():
                    for pattern in patterns:
                        found = re.findall(pattern, stable_text)
                        crawled_items[item] = found[0].strip() if found else ''
                        if found:
                            break

                current_film = Crawled_Film.objects.create()
                # crawled_items['year'] = int(crawled_items['year'])
                for item, value in crawled_items.items():
                    for attr in current_film.__dict__:
                        if item == attr:
                            current_film.__dict__[item] = value

                if current_film not in Crawled_Film.objects.all():
                    current_film.save()
                else:
                    current_film.delete()

                print('Crawled items:')
                for i in crawled_items:
                    print(i, crawled_items[i])
                sleep(random()*10)



lib = Library()
# # lib.get_film_lists()
lib.film_urls = [r'https://baravik.org/topic/1771/']
# lib.get_films()
lib.get_film_data()