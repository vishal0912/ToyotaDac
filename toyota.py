import xml.etree.ElementTree as ET
import scrapy
import uuid
from locations.items import GeojsonPointItem

class Toyotadealer(scrapy.Spider):
    name = 'toyota_dac'
    brand_name = "Toyota"
    spider_type = "chain"
    spider_chain_id = "251"
    spider_categories = ['AUTOMOBILE_DEALERSHIP_NEW_CARS']
    spider_countries = ['IND']
    allowed_domains = ["toyotabharat.com"]
    

    def start_requests(self):
        

        for state_id in range(1, 30):
            base_url = 'https://webapi.toyotabharat.com/1.0/api/businessstates/{}/businesscities'
            
            state_url = base_url.format(state_id)

            # Construct the XML payload
            data = ET.Element('data')
            state_element = ET.SubElement(data, 'state')
            state_element.text = str(state_id)

            # Convert the XML payload to a string
            request_body = ET.tostring(data, encoding='utf-8')

            yield scrapy.Request(
                state_url,
                method='POST',
                #body=request_body,
                headers={'Content-Type': 'application/xml; charset=utf-8'},
                callback=self.parse_state,
                meta={'state_id': state_id},
            )

    def parse_state(self, response):
        state_id = response.meta['state_id']
        #print(response.text)
        root = ET.fromstring(response.text)
        for city in root.findall('.//City'):
            city_id = city.find('Id').text
            city_name = city.find('Name').text
            #print(f"State: {state_id}, City ID: {city_id}, City Name: {city_name}")


        

        # Parse the XML response
        
        for city in root.findall('.//City'):

            city_id = city.find('Id').text
            city_name = city.find('Name').text
            url = f'https://webapi.toyotabharat.com/1.0/api/dealers/{state_id}/{city_id}/1'
            
            # Construct the XML payload for city request
            data = ET.Element('data')
            state_element = ET.SubElement(data, 'state')
            state_element.text = str(state_id)
            city_element = ET.SubElement(data, 'city')
            city_element.text = str(city_id)

            # Convert the XML payload to a string
            request_body = ET.tostring(data, encoding='utf-8')

            yield scrapy.Request(
                url,
                method='POST',
                #body=request_body,
                headers={'Content-Type': 'application/xml; charset=utf-8'},
                callback=self.parse_city,
                meta={'state_id': state_id, 'city_id': city_id, 'city_name': city_name},
            )

    def parse_city(self, response):
        state_id = response.meta['state_id']
        city_id = response.meta['city_id']

        # Parse the XML response
        root = ET.fromstring(response.text)

        for dealer in root.findall('.//Dealer'):
            dealer_info = {
                'chain_id': '251',
                'chain_name': 'TOYOTA',
                'brand' : 'TOYOTA',
                'ref': uuid.uuid4().hex,
                'name': dealer.find('Name').text,
                'addr_full': dealer.find('Address1').text + " " + dealer.find('Address2').text,
                'city': dealer.find('.//City/Name').text,
                'postcode': dealer.find('Pincode').text,
                'store_url': dealer.find('URL').text,
                'phone' : dealer.find('Phone').text,
                'lat': dealer.find('Latitude').text if dealer.find('Latitude') is not None else None,
                'lon': dealer.find('Longitude').text if dealer.find('Longitude') is not None else None,
                'country': "India",
                'website': "https://www.toyotabharat.com/find-a-dealer/"
                # Add more fields as needed based on the XML structure
            }
            yield GeojsonPointItem(**dealer_info)