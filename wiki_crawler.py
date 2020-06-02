import time
import urllib

import bs4
import requests

import re
from queue import Queue

import pandas as pd

start_url = "https://en.wikipedia.org/wiki/Barack_Obama"
target_url = "https://en.wikipedia.org/wiki/Philosophy"

lists_politicants = 'wiki/Category:Lists_of_politicians'
lists_famous_people = 'wiki/Lists_of_celebrities'
cache_set = set()
link_que = Queue()
link_que.put(lists_famous_people)
cache_set.add(lists_politicants)

def extract_introduction(page):
    start_introduction = page.find("<p>")
    stop_introduction = page.find('<div id="toctitle">', start_introduction + 1)

    # If the page onl has introduction
    if '<div id="toctitle">' not in page:
        stop_introduction = page.find('</p>', start_introduction + 1)
        # while page.find('<p>', stop_introduction + 1) == stop_introduction + 4:
        #     stop_introduction = page.find('</p>', stop_introduction + 4)
    else:
        pass

    raw_introduction = page[start_introduction: stop_introduction]
    return raw_introduction

def extract_pure_introduction(page):
    pure_introduction = (re.sub(r'<.+?>', '', page))       #From '<' to the next '>'
    pure_introduction.replace('\n', '')
    return pure_introduction

def nomalize_st(st):
    if len(st) > 0:
        st = st.replace('\n', '')
        i = st.find('&#')
        while i >= 0:
            j = st.find(';', i + 1)
            while i > 0 and st[i - 1].isdigit():
                i -= 1
            st = st[0:i] + st[j + 1:]
            i = st.find('&#', i)

        while 1:
            i = st.find('http')
            if i >= 0:
                j = i + 1
                while j < len(st) and st[j] != ' ' and st[j] != ')':
                    j += 1
                st = st[:i] + st[j:]
            else:
                break
        st = re.sub(r'/.+?/', '', st)
        st = st.replace('[', '(')
        st = st.replace(']', ')')
        i = 0
        while 1:
            i = st.find('(', i)
            if i < 0:
                break
            j = st.find(')', i + 1)
            k = st.find('(', i + 1)
            if k > i and k < j:
                st = st[:k] + st[j + 1:]
            else:
                for k in range(j - 1, i, -1):
                    if st[k] != '–' and (ord(st[k]) > 255 or (
                            not st[k].isdigit() and not st[k].isalpha() and st[k] != ' ' and st[k] != ',')):
                        st = st[:k] + st[k + 1:]
                i += 1
        return st
    return ''

def get_introduction(name):
    try:
        name_link = name.replace(' ', '_')
        url = urllib.parse.urljoin(
            'https://en.wikipedia.org/wiki/', name_link)
        print(url)
        response = requests.get(url)
        html = response.text
        pure_introduction = extract_pure_introduction(extract_introduction(html))
        return nomalize_st(pure_introduction)
        # time.sleep(2)
    except:
        print(' error {}'.format(name))
        pass

def people_extract():
    people_df = pd.read_csv('people_wiki.csv', encoding='utf-8')
    for i in range(len(people_df)):
        try:
            link = people_df['URI'].iloc[i]
            name_link = link.split("/")[-1][:-1]
            url = urllib.parse.urljoin(
                'https://en.wikipedia.org/wiki/', name_link)
            print(url)
            response = requests.get(url)
            html = response.text
            pure_introduction = extract_pure_introduction(extract_introduction(html))
            print(pure_introduction)
            file = open('database.txt', 'a', encoding='utf-8')  # Open the text file called database.txt
            file.write(pure_introduction)  # write the introduction of that page
            file.write('\n')
            file.close()  # Close the file
            time.sleep(2)
        except:
            print(' error {}'.format(i))
            pass

def find_first_link(url):
    response = requests.get(url)
    html = response.text

    pure_introduction = extract_pure_introduction(extract_introduction(html))
    print(pure_introduction)
    file = open('database.txt', 'a', encoding='utf-8')  # Open the text file called database.txt
    file.write(pure_introduction)  # write the introduction of that page
    file.close()  # Close the file

    soup = bs4.BeautifulSoup(html, "html.parser")

    # This div contains the article's body
    # (June 2017 Note: Body nested in two div tags)
    content_div = soup.find(
        id="mw-content-text").find(class_="mw-parser-output")

    # stores the first link found in the article, if the article contains no
    # links this value will remain None
    article_link = None

    # Find all the direct children of content_div that are paragraphs
    for element in content_div.find_all("p", recursive=False):
        # Find the first anchor tag that's a direct child of a paragraph.
        # It's important to only look at direct children, because other types
        # of link, e.g. footnotes and pronunciation, could come before the
        # first link to an article. Those other link types aren't direct
        # children though, they're in divs of various classes.
        if element.find("a", recursive=False):
            article_link = element.find("a", recursive=False).get('href')
            if article_link not in cache_set:
                link_que.put(article_link)
                cache_set.add(article_link)
                if link_que.qsize() > 100000:
                    break

    # if not article_link:
    #     return

    # Build a full url from the relative article_link url
    first_link = urllib.parse.urljoin(
        'https://en.wikipedia.org/', article_link)
    #
    # return first_link


def continue_crawl(search_history, target_url, max_steps=25):
    if search_history[-1] == target_url:
        print("We've found the target article!")
        return False
    elif len(search_history) > max_steps:
        print("The search has gone on suspiciously long, aborting search!")
        return False
    elif search_history[-1] in search_history[:-1]:
        print("We've arrived at an article we've already seen, aborting search!")
        return False
    else:
        return True

def crawl():
    article_chain = [start_url]
    max_iter = 10000000
    step = 0
    while step < max_iter:
        step += 1
        article_link = link_que.get()
        first_link = urllib.parse.urljoin(
            'https://en.wikipedia.org/', article_link)
        print(step, first_link)
        find_first_link(first_link)
        # if not first_link:
        #     print("We've arrived at an article with no links, aborting search!")
        #     break
        #
        # article_chain.append(first_link)

        time.sleep(2)  # Slow things down so as to not hammer Wikipedia's servers

# people_extract()
# get_introduction('Barack Obama')