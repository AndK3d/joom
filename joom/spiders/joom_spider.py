import scrapy, json
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from joom_spider.items import MyItem
from scrapy.http import TextResponse

class JoomSpider(scrapy.Spider):
    name = "joom"
    rules = (
        Rule(LinkExtractor(deny='$/robots.txt'),
             follow=False)
    )

    def start_requests(self):

        urls = [
            'https://www.joom.com/ru/search/c.1473502937203552604-139-2-118-470466103'
        ]

        for url in urls:
            yield scrapy.Request(url=url,
                                 headers={'Host': 'www.joom.com',
                                          'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
                                          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                          'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                                          'Accept-Encoding': 'gzip, deflate, br',
                                          'Connection': 'keep-alive',
                                          'Upgrade-Insecure-Requests': '1'
                                          },
                                 callback=self.parse_tokens
                                 )




    def parse_tokens(self, response):

        #for r in response.headers.getlist('Set-Cookie'): print('-*-', r)

        yield scrapy.Request(url="https://www.joom.com/tokens/init?",
                             method='POST',
                             callback=self.parse_api
                             )


    def parse_api(self, response):
        jsonresponse = json.loads(response.body_as_unicode())

        accessToken = ''
        isAuthorized = ''
        isEphemeral = ''

        if "accessToken" in jsonresponse:
            accessToken = jsonresponse["accessToken"]
        if "isAuthorized" in jsonresponse:
            isAuthorized = jsonresponse["isAuthorized"]
        if "isEphemeral" in jsonresponse:
            isEphemeral = jsonresponse["isEphemeral"]

        print ('**** --- accessToken=', accessToken)
        print ('**** --- isAuthorized=', isAuthorized)
        print ('**** --- isEphemeral=', isEphemeral)

        category_id = '1473502937203552604-139-2-118-470466103'

        scrapy.Request(url="https://api.joom.com/1.1/search/products",
                             method='POST',
                             body='{"count":10,"filters":[{"id":"categoryId","value":{"type":"categories","items":[{"id":"1473502937203552604-139-2-118-470466103"}]}}]}',
                             #meta={'cookiejar': response.meta['cookiejar']}
                             headers={'Accept': '*/*',
                                      'Authorization': 'Bearer ' + accessToken,
                                      'Content-Encoding': 'gzip'
                                      #'Referer': ''
                                      },
                             callback=self.parse_next
                       )
        yield

    def parse_next(self, response):
        jsonresponse = json.loads(response.body_as_unicode())

        items = jsonresponse["contexts"][0]["value"]
        nextPageToken = jsonresponse["payload"]["nextPageToken"]


        # for item in items:
        #     print item["id"]
        item = MyItem()
        item["item_id"] = jsonresponse["contexts"][0]["value"]


        print ("nextPageToken=", nextPageToken)
        print("lenght =", len(items))
        body = '{"count":10,"pageToken":"%s","filters":[{"id":"categoryId","value":{"type":"categories","items":[{"id":"1473502937203552604-139-2-118-470466103"}]}}]}' % (nextPageToken)
        print (body)
        # next page
        if len(items) > 0:
            scrapy.Request(url="https://api.joom.com/1.1/search/products",
                                 method='POST',
                                 body=body,
                                 headers={'Accept': '*/*',
                                          #'Authorization': 'Bearer ' + accessToken,
                                          'Content-Encoding': 'gzip',
                                          }
                                 )
