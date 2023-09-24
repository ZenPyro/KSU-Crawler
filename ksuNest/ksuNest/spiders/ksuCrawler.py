import json
from pathlib import Path
from time import sleep
import scrapy
from scrapy.exceptions import CloseSpider
from bs4 import BeautifulSoup
import re

# Steps for creating a virtual environment in VSCode:
# 1.) Open the `Command Palette` (Ctrl+Shift+P)
# 2.) Search for the `Python: Create Environment` command
# 3.) Select `Venv` as your environment type and selct an interpreter

# `Spider`s are `Class`s that you define and that Scrapy uses to scrape information from a ->
#-> website (or a group of websites). They must subclass the `Spider` Class and define ->
#-> the initial requests to make, optionally how to follow links, and how to parse the ->
#-> downloaded page content to extract data.

# OVERHEAD OF WHAT ALL JUST HAPPENED BELOW:
# 1.) Scrapy schedules the `Request` instances (`scrapy.Request`) returned by the ->
# -> `start_requests` instance function of the `Spider` instance
# 2.) Upon receiving a response for each `Request` instance, a `Response` instance ->
#-> is instantiated and calls the callback function `parse(self, response)` located in ->
#-> the line `yield scrapy.Request(url = url, callback = self.parse)`, this is the ->
#-> callback function associated with the `Request` instance, the `Response` instance is ->
#-> passed as an argument
class ksuCrawler(scrapy.Spider):
    global CLOSESPIDER_PAGECOUNT # MAX CALLBACK COUNTER
    global i
    i = 0
    CLOSESPIDER_PAGECOUNT = 1000
    global visited_pages # `List` INSTANCE OF ALL PREVIOUSLY VISITED PAGES
    visited_pages = []
    global entries
    entries = dict()
    allowed_domains = [
            "kennesaw.edu"
            #"quotes.toscrape.com"
        ]
    name = "ksuSpider" # Instance variable that identifies the `Spider` instance with a name ->
    #-> It must be unique within a project, that is, we can't set the same name for ->
    #-> different `Spider` instances

    # The below instance function `start_requests(self)` returns an interable `list` instance ->
    #-> of `request`s which the `Spider` instance will begin to crawl from. Subsequent ->
    #-> requests will be generated successively from these initial requests
    def start_requests(self):
        urls = [ # SEED PAGES:
            "https://www.kennesaw.edu/"
            #"https://quotes.toscrape.com/page/1/"
        ]

        for url in urls:
            yield scrapy.Request(url = url, callback = self.parse)


    # The below instance function `parse(self, response)` is called to handle the `response` ->
    #-> downloaded for each of the requests made. The `response` parameter is an instance ->
    #-> of `TextResponse` that holds the page content and has further helpful functions ->
    #-> to handle it
    # NOTE: The `parse(self, response)` instance function usually parses the `response`, ->
    #-> extracting the scraped data as `dict`s and finding new URLs to follow and creating ->
    #-> new `Request` instances from them
    def parse(self, response):
        global CLOSESPIDER_PAGECOUNT # We need to declare the variable `i` as global in each scope where it is ->
        #-> being modified, this is because Python can use the same name for a `global` ->
        #-> and `local` variable in the same scope (learned this in class)
        global i
        global visited_pages
        global entries
        i = i + 1

        if i < CLOSESPIDER_PAGECOUNT:
            entry = dict.fromkeys(["pageid", "url", "title", "body", "emails"])
            entry["pageid"] = i
            page = response.url.split("/")[-2]
            entry["url"] = page
            entry["title"] = response.xpath("//title/text()").get()

            stripped_body_list = []
            rough_body_list = response.xpath("//body/descendant::text()").getall()
            for token in rough_body_list:
                #NOTE: Python `String`s are immutable, so you have to re-assign it below ->
                #-> (had me stuck for a second haha)
                token = token.strip() # Strip `\n` (newlines) from the text
                token = re.sub(r"[^\w\s]", "", token) # Regex to strip anything but ->
                #-> words or whitespace from the text (the apostrophes where getting in the ->
                #-> way)
                if(token != ""):
                    stripped_body_list.append(token)
            entry["body"] = stripped_body_list
            #entry["body"] = BeautifulSoup(response.text) # Using the `BeautifulSoup` `Class` ->
            # #-> here to "strip" the html  from the `text`

            # IMPORTANT NOTE: The instance variable `body` for a `Response` instance is ->
            #-> always in `bytes`, this means that if you want a `string` data type ->
            #-> instead of a `bytes` data type, you have to use the instance variable ->
            #-> `text` like we did in the line above with `response.text`, this will ->
            #-> return a `string` data type (must be from a an encoding-aware `Response` ->
            #-> subclass like a `TextResponse` instance)
            # entry["body"] = response.body
            entry["emails"] = response.xpath("""//a[starts-with(@href, "mailto")]/text()[contains(., "@")]""").getall()
            entries[i] = entry

            filename = f"""referredfrom_#{i}-{page}.html"""
            # Added `"scrapedData/"` to the below line of code so that the scraped data could ->
            #-> easily be removed after running tests because the scraped data is being sent ->
            #-> to its own seperate folder
            Path("scrapedData/" + filename).write_bytes(response.body)
            self.log(f"Saved file {filename}")

            json_text = json.dumps(entries, indent = 4)
            Path("textData/text_data.json").write_text(json_text)
        else:
            raise CloseSpider("[MAXIMUM CRAWL LIMIT REACHED]")

        # STORING THE SCRAPED DATA: (For now I do it through the Scrapy Shell)
        # The simplest way to store the scraped data is by using "feed exports", with the ->
        #-> following commands: `scrapy crawl quotes -O quotes.json` ->
        #-> That will generate a `quotes.json` file containing all scraped items, serialized ->
        #-> in `JSON` (which is really cool!)
        # NOTE: The `-O` command-line switch overwrites any existing file; use `-o` instead ->
        #-> to append new content to any existing file (however, appending to a `JSON` file ->
        #-> makes the file contents invalid `JSON` so when appending to a file, consider ->
        #-> using a different serialization format, such as `JSON Lines`)

        # Now lets modify our `Spider` instance to recursively follow a link to the next ->
        #-> page, extracting data from it
        
        # Now, after extracting the data, the `parse(self, response)` instance function looks ->
        #-> for the link to the next page, builds a full absolute URL using the `urljoin()` ->
        #-> instance function (since the links can be relative) and `yield`s a new `Request` ->
        #-> instance to the next page, registering itself as `callback` to handle the data ->
        #-> extraction for the next page and to keep the crawling going through all the pages
        # What you see here is Scrapy's mechanism of following links: when you yield a ->
        #-> `Request` instance in a `callback` function, Scrapy will schedule that request to ->
        #-> be sent and register a `callback` function to be executed when the ->
        #-> current (super) request finishes    
        #next_pages = response.xpath("//a/@href").getall()
        #for page in next_pages:
        #    if i >= 10:
        #        break
        #    else:
        #        i = i + 1
        #        expand_page = response.urljoin(page)
        #        yield scrapy.Request(expand_page, callback = self.parse)

        # IMPORTANT NOTE: The 'xpath` example expression //a[not(contains(@href, "#"))]` ->
        #-> would not work correctly because this is "saying", for every `element` `a`, find ->
        #-> the FIRST child `@href` element that does not contain `#`, instead of out of all ->
        #-> `element`s that are a child of `a` and are `@href`
        next_pages = response.xpath("""//a/@href[not(contains(., "#"))]""").getall()
        for next_page in next_pages:
            # BELOW WAS AN OLD WAY OF THINKING BUT KEPT TO SEE MY TRAIN OF THOUGHT:
            # # Line of code below basically says, as long as the `next_page` instance is ->
            # #-> not `None` and is not currently in the `visited_pages` `List` instance ->
            # #-> then you can explore the `next_page` instance, BUT each page can only ->
            # #-> expand a maximum of 3 additional pages before, and there can only be ->
            # #-> a total of 300 expanding "root-ish" page nodes that are parents of other ->
            # # #-> page nodes. This means the maximum pages explored can only be at most ->
            # # #-> `3*300` which is 900 pages 

            # NEW MUCH SIMPLIER METHOD BELOW:
            if next_page is not None and next_page not in visited_pages and i < CLOSESPIDER_PAGECOUNT:
                visited_pages.append(next_page)
                next_pageL = response.urljoin(next_page)
                print(f"NEXT PAGE: {next_pageL}")
                #sleep(0.09)
                #sleep(5)
                yield scrapy.Request(next_pageL, callback = self.parse)