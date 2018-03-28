import scrapy, json
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import TextResponse

class JoomSpider(scrapy.Spider):
    name = "joom"
    rules = (
        Rule(LinkExtractor(deny='$/robots.txt'),
             follow=False)
    )

    def initAccessToken (self,value):
        global AccessToken
        AccessToken = value
        return AccessToken

    def getAccessToken(self):
        return AccessToken

    def setAccessToken(self):
        return

    def start_requests(self):

        urls = [
            'https://www.joom.com/ru/search/c.1473502937203552604-139-2-118-470466103'
        ]

        for url in urls:
            rqst = scrapy.Request(url=url,
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
            yield rqst

    def parse_tokens(self, response):

        yield scrapy.Request(url="https://www.joom.com/tokens/init?",
                             method='POST',
                             callback=self.parse_api
                             )

    def parse_api(self, response):
        jsonresponse = json.loads(response.body_as_unicode())


        # accessToken = ''
        # isAuthorized = ''
        # isEphemeral = ''
        #
        # if "accessToken" in jsonresponse:
        #     accessToken = jsonresponse["accessToken"]
        # if "isAuthorized" in jsonresponse:
        #     isAuthorized = jsonresponse["isAuthorized"]
        # if "isEphemeral" in jsonresponse:
        #     isEphemeral = jsonresponse["isEphemeral"]

        token = self.initAccessToken(jsonresponse["accessToken"])

        # print ('**** --- accessToken=', accessToken)
        # print ('**** --- isAuthorized=', isAuthorized)
        # print ('**** --- isEphemeral=', isEphemeral)

        category_id = '1473502937203552604-139-2-118-470466103'

        yield scrapy.Request(url="https://api.joom.com/1.1/search/products",
                             method='POST',
                             body='{"count":10,"filters":[{"id":"categoryId","value":{"type":"categories","items":[{"id":"1473502937203552604-139-2-118-470466103"}]}}]}',
                             headers={'Accept': '*/*',
                                      'Authorization': 'Bearer ' + token,
                                      'Content-Encoding': 'gzip'
                                      },
                             callback=self.parse_next
                             )

    def parse_next(self, response):

        jsonresponse = json.loads(response.body_as_unicode())
        items = jsonresponse["contexts"][0]["value"]
        nextPageToken = jsonresponse["payload"]["nextPageToken"]

        for item in items:

            yield {
                'item_id': item["id"]
            }

        print ("nextPageToken=", nextPageToken)
        print("len =", len(items))
        body = '{"count":10,"pageToken":"%s","filters":[{"id":"categoryId","value":{"type":"categories","items":[{"id":"1473502937203552604-139-2-118-470466103"}]}}]}' % (nextPageToken)
        
        # next page
        token = self.getAccessToken()
        if len(items) > 0:
            yield scrapy.Request(url="https://api.joom.com/1.1/search/products",
                           method='POST',
                           body=body,
                           headers={'Accept': '*/*',
                                    'Authorization': 'Bearer ' + token,
                                    'Content-Encoding': 'gzip'
                                          }
                           )
