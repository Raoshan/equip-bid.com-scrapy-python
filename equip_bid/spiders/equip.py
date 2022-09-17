import scrapy
import pandas as pd
df = pd.read_csv('F:\Web Scraping\Golabal\keywords.csv')
base_url = 'https://www.equip-bid.com/auction/search?search_phrase={}'

class EquipSpider(scrapy.Spider):
    name = 'equip'

    header= {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }

    
    def start_requests(self):
        for index in df:
            yield scrapy.Request(base_url.format(index), headers = self.header, cb_kwargs={'index':index})

    def parse(self, response, index):
        total_pages = response.xpath("//ul[@id='pagination']/li[last()-1]/a/text()").get()
        print(total_pages)
        current_page =response.css("li.active::text").get()
        print(current_page)
        url = response.url
        print("***********  "+url)
    
        if total_pages and current_page:
            if int(current_page) ==1:
                for i in range(2, int(total_pages)+1):                                      
                    yield response.follow(url=f'{url}&page={i}', headers = self.header, cb_kwargs={'index':index})

        images = response.xpath("//div[@class='col-xs-12 col-sm-4']//img/@src").getall()       
        links = response.xpath("//div[@class='col-xs-12 col-sm-4']/a/@href")  
        counter = 0
        for link in links:
            image = images[counter]
            yield response.follow("https://www.equip-bid.com"+link.get(), headers = self.header, callback=self.parse_item, cb_kwargs={'index':index,'image':image})  
            counter = counter+1
        
    def parse_item(self, response, index,image): 
        print(".................")      
        auction_date = response.xpath("//span[@id='lot_scheduled_close']/text()").get()
        print(auction_date)
        description = response.xpath('//*[@id="lot_description"]/div[3]/text()').extract()[2].strip()
        print(description)
        location = response.xpath("//span[@class='location']/p/text()").get().strip()
        print(location)
        product_name = response.css('span.lot-title::text').extract()[0]
        print(product_name)
        lot_number = response.css('span.lot-title::text').extract()[1][5:]
        print(lot_number)
        auctioner = response.css('h4 a::text').get()
        print(auctioner)

        yield{
            
            'product_url' : response.url,           
            'item_type' :index,            
            'image_link' : image,          
            'auction_date' : auction_date,            
            'location' : location,           
            'product_name' : product_name,            
            'lot_id' : lot_number,          
            'auctioner' : auctioner,
            'website' : "equip-bid",
            'description':description            
        }