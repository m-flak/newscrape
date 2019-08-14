from abc import abstractmethod, abstractproperty
from bs4 import BeautifulSoup, Tag
from io import BytesIO
import certifi
import pycurl
import re
import werkzeug.urls

# Callable that generates a search query from multiple terms OR a list of 'em
# Ex: SearchQuery('foo', 'bar') / SearchQuery(['foo','bar'])
class SearchQuery(object):
    def __init__(self, *args, **kwargs):
        self.separator = kwargs.get('separator', " OR ")
        if re.fullmatch(r"[\s]\w+[\s]", self.separator) is None:
            self.separator = " {} ".format(self.separator)
        self.search_terms = self.merge_args(args)

    # merge any arguments that are lists
    def merge_args(self, args):
        rv = []
        for a in args:
            if isinstance(a, list):
                rv = rv + a
            else:
                rv.append(a)
        return rv

    # Optional Arguments: Additional search terms
    def __call__(self, *args):
        allterms  = self.search_terms + self.merge_args(args)
        rv        = str()

        for i in range(0, len(allterms)):
            rv += allterms[i]
            if i+1 == len(allterms):
                continue
            rv += self.separator

        return rv

# Callable that generates the URL for a search query from a URL and/or terms
# Ex: WebSearchQuery("http://foobar.com/search?q=", 'foo', ['foo', 'bar'])
# NOTE: Any argument `q` will be overridden from the url with search terms
class WebSearchQuery(SearchQuery):
    def __init__(self, search_addr, *args, **kwargs):
        super(WebSearchQuery, self).__init__(*args, **kwargs)
        self.url = werkzeug.urls.url_parse(search_addr)
        self.query_param_name = kwargs.get('query_param_name', "q")

    # Refer to SearchQuery.__call__
    def __call__(self, *args):
        searchstr = super(WebSearchQuery, self).__call__(*args)
        query = werkzeug.urls.url_decode(self.url.query)
        query[self.query_param_name] = searchstr
        new_url = werkzeug.urls.URL(self.url.scheme, self.url.netloc,
                    self.url.path, werkzeug.urls.url_encode(query),
                    self.url.fragment)
        self.url = new_url
        return self.url.to_url()

class WebSearch(object):
    @abstractmethod
    def parse_search(self):
        pass

    @abstractproperty
    def buffer(self):
        pass

    @abstractproperty
    def curl(self):
        pass

class GoogleSearch(WebSearch):
    base_url = "https://www.google.com/search?q=&tbm=nws"

    def __init__(self, keywords):
        full_url = WebSearchQuery(self.base_url)
        self.full_url = full_url(keywords)
        self._curl = None
        self._buffer = None

    def parse_search(self):
        return Results(self.buffer.getvalue(), self)

    @property
    def buffer(self):
        if self._buffer is None:
            self._buffer = BytesIO()
        return self._buffer

    @property
    def curl(self):
        if self._curl is None:
            self._curl = pycurl.Curl()
            self._curl.setopt(pycurl.URL, self.full_url)
            # google is racially prejudiced against curl UA's
            self._curl.setopt(pycurl.HTTPHEADER, ("User-Agent:",("Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134)")))
            self._curl.setopt(pycurl.CAINFO, certifi.where())
            self._curl.setopt(pycurl.WRITEDATA, self.buffer)
        return self._curl

    @staticmethod
    def soup_callback(soup):
        stories = soup.find_all(class_='g')
        results = []
        for story in stories:
            story_a = story.find('a')
            try:
                story_a.b.unwrap()
            except:
                story_a = story_a
            headline = ''.join([lnk if not isinstance(lnk, Tag) else lnk.string for lnk in story_a])
            g_link = werkzeug.urls.url_decode(story_a.get('href'))
            link = g_link['/url?q']
            story_st = story.find(class_='st')
            summary = ''.join([sum if not isinstance(sum, Tag) else sum.string for sum in story_st])
            results.append({
                            'headline': headline,
                            'link': link,
                            'summary': summary,
                            })
        return results

class BingSearch(WebSearch):
    base_url = "https://www.bing.com/news/search?q="

    def __init__(self, keywords):
        full_url = WebSearchQuery(self.base_url)
        self.full_url = full_url(keywords)
        self._curl = None
        self._buffer = None

    def parse_search(self):
        return Results(self.buffer.getvalue(), self)

    @property
    def buffer(self):
        if self._buffer is None:
            self._buffer = BytesIO()
        return self._buffer
    @property
    def curl(self):
        if self._curl is None:
            self._curl = pycurl.Curl()
            self._curl.setopt(pycurl.URL, self.full_url)
            # now, bing doesn't have a problem with curl :)
            self._curl.setopt(pycurl.CAINFO, certifi.where())
            self._curl.setopt(pycurl.WRITEDATA, self.buffer)
        return self._curl

    @staticmethod
    def soup_callback(soup):
        stories = soup.find_all(class_='news-card')
        results = []
        for story in stories:
            link = story.get('url')
            headline = story.find('a', class_='title').string
            story_sum = story.find(class_='snippet')
            summary = ''.join([sum if not isinstance(sum, Tag) else sum.string for sum in story_sum])
            results.append({
                            'headline': headline,
                            'link': link,
                            'summary': summary,
                            })
        return results

class YahooSearch(WebSearch):
    base_url = "https://news.search.yahoo.com/search?p="

    def __init__(self, keywords):
        full_url = WebSearchQuery(self.base_url, query_param_name='p')
        self.full_url = full_url(keywords)
        self._curl = None
        self._buffer = None

    def parse_search(self):
        return Results(self.buffer.getvalue(), self)

    @property
    def buffer(self):
        if self._buffer is None:
            self._buffer = BytesIO()
        return self._buffer
    @property
    def curl(self):
        if self._curl is None:
            self._curl = pycurl.Curl()
            self._curl.setopt(pycurl.URL, self.full_url)
            self._curl.setopt(pycurl.CAINFO, certifi.where())
            self._curl.setopt(pycurl.WRITEDATA, self.buffer)
        return self._curl

    @staticmethod
    def soup_callback(soup):
        stories = soup.find_all(class_='dd NewsArticle')
        results = []
        for story in stories:
            a_hla = story.find('a')
            link = a_hla.get('href')
            if a_hla.get('title') is not None:
                headline = a_hla.get('title')
            else:
                headline = ''.join([hdl if not isinstance(hdl, Tag) else hdl.string for hdl in a_hla])
            p_sum = story.find('p')
            summary = ''.join([sum if not isinstance(sum, Tag) else sum.string for sum in p_sum])
            results.append({
                            'headline': headline,
                            'link': link,
                            'summary': summary,
                            })
        return results

class Results(object):
    def __init__(self, input_data, parent_search, **kwargs):
        encoding = kwargs.get('encoding', 'utf-8')
        alt_encoding = kwargs.get('alt_encoding', 'latin-1')
        try:
            self.html = input_data.decode(encoding)
        except UnicodeDecodeError:
            self.html = input_data.decode(alt_encoding)
        self.soup = BeautifulSoup(self.html, features="html.parser")
        self.results = None

        soup_cb = getattr(parent_search, 'soup_callback')
        self.eat_soup(soup_cb)

    def eat_soup(self, cb):
        self.results = cb(self.soup)

    def __add__(self, other):
        self.results = self.results + other.results
        return self

class Scraper(object):
    def __init__(self, *args, **kwargs):
        self.scrapees = []

    def add_scrapee(self, websearch):
        self.scrapees.append(websearch)

    def scrape(self):
        for i in range(0, len(self.scrapees)):
            self.scrapees[i].curl.perform()

    def fetch_results(self):
        search_results = [ws.parse_search() for ws in self.scrapees]

        # add the result objects together
        # we only want a -single set- of results
        first_result = search_results[0]
        for result in search_results:
            if result is first_result:
                continue
            first_result = first_result + result

        # multiple result objects are now a single
        return first_result.results
