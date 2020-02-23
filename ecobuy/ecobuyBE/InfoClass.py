import urllib.request
from bs4 import BeautifulSoup
import string
import random
from selenium import webdriver
import time
import os
from ecobuyBE.ConstantsPy import Constants
import platform
from selenium.webdriver.common.keys import Keys
import time
import requests
import json
import types
from math import radians, cos, sin, asin, sqrt
from ecobuyBE.Utils import *
import geocoder
import numpy as np


class Scraper:
    def __init__(self):
        self.product_vector = []
        self.product_recommendations = []
        self.product = Info()

    def findIfIsAConcreteProduct(self, url):
        concrete_product = False
        if "/itm" in url:
            concrete_product = True
        return concrete_product

    def switchToFrame(self):
        try:
            self.browser.switch_to.frame(self.browser.find_element_by_tag_name("iframe"))
        except:
            pass

    def switchToGlobal(self):
        try:
            self.browser.switch_to.default_content()
        except:
            pass

    def findElement(self, place_to_search, label_list=[], containing=None, number=False, money=False):
        if containing and containing == " x ":
            number = False
        scraped_data = None
        if len(label_list) and not containing:
            scraped_data = place_to_search.findAll(label_list[0], {label_list[1]: label_list[2]})
            if scraped_data:
                scraped_data = scraped_data[0].get_text()
            if money and scraped_data:
                scraped_data = scraped_data.split("$")[1]
        elif containing:
            if label_list:
                places_to_search = place_to_search.findAll(label_list[0], {label_list[1]: label_list[2]})
            else:
                places_to_search = place_to_search

            for item in places_to_search:
                script = str(item)
                if containing in script:
                    if containing == ' x ':
                        scraped_data = item.get_text()
                    else:
                        scraped_data = item.get_text().split(containing)[0].strip()
                    break
        else:
            scraped_data = None
        if number and scraped_data:
            scraped_data = self.numberDetection(scraped_data)
        return scraped_data

    def cleanVolume(self, raw_volume):
        volume = None
        volume_numbers = []
        for number in raw_volume.split(" x "):
            if "\"" in number:
                if "\n" in number:
                    number = number.split("\n")[1]
                volume_numbers.append(convertionToIS(number.split("\"")[0], 'inches'))
        if len(volume_numbers) == 3:
            volume = round(volume_numbers[0] * volume_numbers[1] * volume_numbers[2], 6)
        return volume

    def numberDetection(self, raw_number, boolean=False):
        numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        index = 0
        if boolean:
            exist_number=False
        where_to_cut = False
        for character in str(raw_number):
            for number in numbers:
                if character == number:
                    if boolean:
                        exist_number=True
                        return exist_number
                    if index > 1:
                        where_to_cut = index
                    else:
                        where_to_cut = -1
                    break
            if where_to_cut:
                break
            index += 1
        if where_to_cut > 0:
            number_to_send = float(raw_number[where_to_cut:])
        else:
            number_to_send = raw_number
        return number_to_send

    def getContinent(self, country):
        country = country.split(",")[-1].strip()
        url_continent = 'https://www.google.com/search?q=' + str(country) + ' continent'
        self.browser.get(url_continent)
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        continent = self.findElement(soup, ['a', 'class', 'FLP8od'])
        return continent

    def calculateIndex(self):
        attributes = 0
        volume_index = 1
        weight_index = 1
        distance_index = 1
        intercontinental_index = 1
        contaminant_material_index=1
        contaminant_countries_index=1
        number_of_indexes = 6
        if self.product.distance > 0:
            distance_index = round(1 - (self.product.distance) / 20000, 2)
            attributes += 1
        if self.product.weight > 0:
            weight_index = round(1 - self.product.weight / 15, 2)
            attributes += 1
        if self.product.volume > 0:
            volume_index = round(1 - self.product.volume /5, 2)
            attributes += 1
        if self.product.origin_continent and self.product.destiny_continent:
            if self.product.origin_continent != self.product.destiny_continent:
                intercontinental_index = 0.6
            attributes += 1
        if self.product.materials:
            number_of_materials=len(self.product.materials)
            for index in range(number_of_materials):
                contaminant_material_index=contaminant_material_index*0.75
        if self.product.countries:
            number_of_countries = len(self.product.countries)
            for index in range(number_of_countries):
                contaminant_material_index = contaminant_countries_index * 0.75
        self.product.index_accuracy = round(attributes / number_of_indexes*100, 2)
        self.product.ecofriendly_index = round(distance_index * weight_index * volume_index * intercontinental_index *contaminant_material_index*contaminant_countries_index*100,0)


    def printResults(self):
        print("Name: ", self.product.name)
        print("Origin: ", self.product.origin)
        print("Destiny: ", self.product.destiny)
        print("Distance: ", self.product.distance, " km")
        print("Volume: ", self.product.volume, " m^3")
        print("Weight: ", self.product.weight, " kg")
        print("Price: ", self.product.price, " $")
        print("Contaminant materials: ", self.product.materials)
        print("Contaminant countries: ", self.product.countries)
        print("Ecofriendly Index: ", self.product.ecofriendly_index)
        print("Index accuracy: ", self.product.index_accuracy, "%")

    def selectOneUrl(self, number):
        url = None
        if number == 1:
            url = "https://www.ebay.com/itm/500-Chips-Poker-Chip-Set-11-5-Gram-Holdem-Cards-Game-W-Aluminum-Case-Dices/133050663345?_trkparms=ispr%3D1&hash=item1efa7001b1:g:1Q0AAOSw4YZc2UMZ&enc=AQAEAAACQBPxNw%2BVj6nta7CKEs3N0qVUAThiB0WpsCRR7s4hf5KS2jqgt6%2B8togN79WpFaVmYT61DKtLlSfaV0wyN4GsY15nerJpcCUwwGijLIuElM%2B%2B9nj9fMaSWA%2BkqGXReKZ9bMu0LHjHd3DjT71sq7pbqi2it0XzXzhpEJOxTQbxIz9YOlAFIWVPPvAvXv8aAZN4qFI5o%2FLVJEOD302sP%2BKpUaPy%2FDQmqCZQJaLmHblVZ60fd22WSKa5U5BRUDRmF498660Yr%2BAPeuq7450mf8rMNVaDhL7QoRsN7AeWstjs1fchklkM3vJCmEd2V953CfRF3oFeCW3bFqdhq2LSdA0YG4k8b4qEl1GQk73djYz6wgXDISst5gpBAqz2l5ndzjKdvtFcKFV%2FpXTS4Wn7Oxotx1KrL2Y9W3%2BPRygh%2F%2FNS3eCKWfU7ddq4wmfQeqn8uClbxhaKMQRztQ5%2BvxT6SYMUoIHd13zXzavNoVch%2FYfMA6FRoqakRbzHaMG3WMz%2F74%2B8V5xOEjzbQnRaXHKddYfXiHutamvZ8NEmrx5tpczgXZdyOEQbQ%2FKxsoCmMj%2Fhor55i9ExLEua0Rj0VAeoyiNfIAHd15vUCj51FqW%2FY3V2eMEToJSNgWNyvPPT1ft20PBc4xxqjt0YbP6iH80T8VJbJp5FbbQ2V8ugoc4kICJP0VgZRW%2BTulNi6Wjq2CcezM1e6SQs1l5aDS5qofxl9C3SwH4Y37195OqkTVC9dgG6S2iXr7v2xsd%2FlpJY3I3dsRtFlA%3D%3D&checksum=133050663345ed15b97c5c9349de8a3f0a70ae4a88ef"
        if number == 3:
            url = 'https://www.ebay.com/itm/Joyfay-47-120-cm-Brown-Giant-Teddy-Bear-Big-Huge-Stuffed-Toy-Valentine-Gift/111607223485?epid=1743995278&_trkparms=ispr%3D1&hash=item19fc4f14bd:g:-NAAAOSwSlRa4Yva&enc=AQAEAAACQBPxNw%2BVj6nta7CKEs3N0qUzmMriB5bMwFkQPZFkCRXNIMvW66Z7fA%2Fok7uc4C340M9AmBDC%2BTs%2BMlETVZz1UqCrWEXTlcrQn0EmaB7Fb2H1hrvccSOF9ZySYH5ok5fkNqn1adNJoqUTio0YOHW7U9VkuFh7npRWzGuikfnKJnzD%2FGFCJ1Gje%2F8iokjvO%2Fw5xXZ3KN5KepqbZhe02Rcq9YilTxt2v1UxCtHDCgI2zn8oxLEQgUtSAbz7TSTJiJvUWMi%2Bjim8AZuxaeuwRSR3%2B8m1kMhF%2F2BKjkKa%2Bqkp1%2F5DnlxxiAjGU6T8NATpnGvwYms15aMGzeMfe1EHmet8pQesdezGFEpLKzag0rZoo%2BKE%2FTOs5sybEG3uu15bFpMK4DiGOFVkk0OWyMIsxGKtbu9DG5cfgxTu%2Bjxw1jSmobrvCSEzqX1Ozh%2FjXM2dNW5dVoQmi42HV%2B%2BDYWbobIlag0wKTFVK6oeRqbMEfkEOKm98B%2BVVsonHf97FDmRst4xBRMS9lEBRnbh%2BJNGGDq3VnPDSfxgllFHo08QI3ncs7DsEP%2BQYXQ%2F%2BU0vIafEXlI%2FaIM5l414scf5I0abt6snc2aFlujXPJ1W9X%2BuCPPal2FCjjb3unhSU7W9jA9oZPfge32F5OORD7sKUwk03xBWMieYIvWEAaCrs2u2%2FjY3koduO8vzcIOCYKFSyUlxp7HBlyaD5L5nW0QWgw40Dp5R4aCYJ2P7RWii6%2FJ6%2FSlhHjdWIWVLNSFMpSPsvt41OIkM9BQ%3D%3D&checksum=111607223485ac7c068e6c69444b82f5e1ee0054e3f5'
        if number == 2:
            url = "https://www.ebay.com/itm/Disco-Party-Lights-Strobe-Led-Dj-Ball-Sound-Activated-Bulb-Dance-Lamp-Decoration/362665204949?epid=20031753259&_trkparms=ispr%3D1&hash=item547087dcd5:g:IboAAOSwstNc7~hL&enc=AQAEAAACQBPxNw%2BVj6nta7CKEs3N0qXHsdjmBPUu4yuPwRwsg76EVbv%2F1FmwyFM49zlEs66WSt8jj%2BoBKZKn6eB7pG0rNYntkuAey5fsGtQ1oJjqXJ01a%2Fik3XZJiHIqvohgBCzOPJ5lllbUr5%2BnZkWDmE0nGLopmVOWfcHY05qYHzMis5hiltpzI78GUJlq3id6nNchRiDBwAHTLyWYOJr%2B7of7rKi9xconzAhzMaPf3F3kvXrFkxhTRILjPBHkZ6lbR5vWcy9HEFTPonZV1gJerhgsaBQz2%2BwAWrbtZUKgAoEwkQxWfx%2FgE9N3UD%2BOy9i93SCHPao4Ndj4wXuMIDbxJ3mrYmHUe2XyvwhyQzKkDvfQ%2FgB2dvqnJQqO3OnlyByU%2FRZ%2FFXoK2PeKpnRPC%2FeTyaVFFhLf43iclVnhhWJNH%2FaueujMUMeyEJoR4y3eJ7wWpZsg4KTi31%2BHr5vduQayZZ3Sr2aRm9F%2F4dBEVS6sRB3X7eyxC0vkXtr7Gn5r4lh8E3Kluf4MRjuwBs7lTuo%2BIfSNWnND57Ztwg4BtHmNozLBqs712kEm1lBGQN7bah56zgpqZj9J%2F4V%2FaTkTlmnGqy4NSkv1ZRFWuvjPECuXTVPqgmyi%2B05hTQngsAEQAL%2BfsbMACskKIgWQmfaPMdXH9c3BczNUWdc5KcPWitKihhf9wYrNey4cIo56cJOM%2F9KLghjkg%2F2H3PrQAH1kTF872wKaFJSloM95Mt1wLruAbS2gNUxYAnL7GS%2F5tElDrSCqhGSRlQ%3D%3D&checksum=36266520494980791141606f4713bffe366e09d307f4"
        if number == 4:
            url = "https://www.ebay.com/itm/Marmite-Yeast-Extract-125g-x-1-delivery-in-3-4-days-expJan-2021/254193486546?hash=item3b2f1ccad2:g:g64AAOSwdxZbDdo9"
        if number == 5:
            url = "https://www.ebay.com/itm/Sony-PlayStation-4-PS4-Slim-1tb-Jet-Black-Console-w-accessories-SHIPS-FAST/323649342133?epid=236958512&_trkparms=ispr%3D1&hash=item4b5b010ab5:g:z1EAAOSwV21azqBD&enc=AQAEAAACQBPxNw%2BVj6nta7CKEs3N0qXYEgolfhLL0rYU5DOrS9AmZutHeCd0ha2aWUqJ9R521ruK7T5nL4ykZDd8WZbBCtc8PHrmUv8RFFT92QBCa2sDCl5BwVrp%2BllQw7xsmgtgMHz1OQ3z8PuLG9hhU%2F924iMiFjHVfhazOKB2n9qYZi%2Be0XrndMDkYsP9Xeyo5pgFvFmiBAUs72SguCQQqOmmCZrA5EKl0Jj2Q2GlwPSXLvBTjXm54FJtak8N4LtzrjQ5fW%2BBgMPEdBY8PgRe1sBd6zEkfGsZS7hhBpWm25DGGoLPNO%2BYBfxxjtj8ub7d9cP%2Bz30FtQXDK9%2FlQj%2BwcANjycQTz91bqhlWkDtytiuWpkRFH1ia9iuixRTWFt%2F5bci9LStnN7vtKVvnDd761Fs605a4QrPyjfhMuq8ADd8qB%2BHZ9xzKkJNNKa1Ne3lybaeVGUqVeWNHYLAXZDCUEalDXEeK0zI3ZRjLmnIeNULHXNcHaEz6iDqTyg8%2FMlxCq1%2BXKIG%2BnYUHcy7nDt88kRGTBC4c6P0cw5kQsERWdpSA%2Bd9cAEtlxvW09WI%2B26HorPOJamuxkGh6EgizrA7w0INtfsrJF5W%2FzFqoWicLUDuR6bAdugc%2BawGoQjyHVwlpzWGveO32%2FB0UkROnXUefIkpuVuAOsBriiTZnICQn7pwzyoudOi0A7W8wtF4PZGHXo4KAMU9P%2F2lvRBiZsN096Yr9gdFvD4EddWq8DmfdieKX2vnFxE3xvGhPPl7nSMKHaQ42Bg%3D%3D&checksum=3236493421334d4454ec565a4eaca3bb47586aa3f7a1"
        if number == 6:
            url = 'https://www.ebay.com/itm/Aguacatina-Aceite-de-Aguacate-100-Guatemalteco/223448318091?hash=item34068ec08b:g:Z3YAAOSwTmxciuef'
        if number==7:
            url='https://www.ebay.com/itm/Modern-Glass-Coffee-Table-Shelf-w-Walnut-Leg-Living-Room-Furniture-Rectangular/152592995526?_trkparms=ispr%3D1&hash=item23874054c6:g:tOoAAOSwIMlc3SVP&enc=AQAEAAACQBPxNw%2BVj6nta7CKEs3N0qUm4bby0Rrhe6cpI1seFbpzw1H9DwmEyz%2FFwEbtpgpbVUBBt8L5wSGaXQ6RDnVNdXc78IQSjjbtS6f1%2B2Jm3VJIIAbQbk%2BJ5z3mWgRig0jVno2VjioQVUBF4WEglkZcXue44HNcq1VldE9NjXg24VkGC0urXx5%2B9sNDk8lfPfhIeJN%2BBuqxfTuFryJfkDSuMunvQ36bS4DBmfGfEovQLfQZE61Txm22CDxi3vOwMgupI2A06zgaG0qOMbe2LH8fVG3I0DAHcQo8D85KWSDsu6Fx8kmlVbx7U2PBBBIcDJ0JOHAxA3fobxWfPUtq2bfb9Tqw5BsxrURXMcH0oEC9FIFq%2FkKu4yICfTzRpgq0gHSXdjB3DRm8eLrzUD79UQCnKC%2FKAZpv0ehRe7T1Eh4ElEP7x73b2gp8T7zuQdMlzgUkt6z%2FnXUu1X4hQcVMHStMIUgJek6Ad4dmCAGWBPI3se3fBc6ihHVyekNdqlszg8HMw5Y0vfjwBgvnJhsyLJAhunQ%2Ffz%2BNPFoJYxXv5ib1ZvGfqmfRn%2BHXBlw3MsB4fAbv7Z3B7e4OwN4VrBdNQpZRLHiraLfn3yRYR3X4GZEdW91WB%2Ftfss13TBmEnSHF4w0YI94tzUWH1IlEkKB02deFNYibCEC%2BZ1Wohf8BsjBpikveVmrzZg%2FUoqXMk9GRQOik4%2FjcT%2Fb8NPAmkUldS3DZ%2FZAIXHpbZ4mZMpOMv7MD4%2FzmMnp9HwEDmVyrsPyo%2BxCLYw%3D%3D&checksum=1525929955260f19c17fcc944094a8c1b4bae49d54ad'
        if number==8:
            url="https://www.ebay.com/itm/DELL-LAPTOP-LATiTUDE-WINDOWS-10-CORE-2-DUO-4GB-RAM-WIN-DVD-WIFI-PC-HD-COMPUTER/151744607899?_trkparms=ispr%3D1&hash=item2354aef69b:g:iU8AAOSwBdhbT3lt&enc=AQAEAAACQBPxNw%2BVj6nta7CKEs3N0qUljzPz6Lx8XOXtShhOmXqx%2FU34kb4KnwMEY0bwEf4JQX5bYAK1mtT%2FMKIunsuy42UXTE0FgOqZk7KCNcu9oU99ChefasfsRiI3gmbrSC5xUYGgWlycdxbBIlDOf9j72XA3W%2B5rsjd6u7FjYzPFfKcrr%2Ba1clq1nngZKgloK86f5s%2FDgReFAAgKTVCmjS6DXS4mz3BaHYd2pFdkTh0C55HFLMwzqn51wOoNo8Sft%2FNu8EY9RorDEEUUjGulfk01nZGnZ64UVFhGFtH7da3SM0UnZudb4FCe1Q7sPL8zu04LdNPSLLcAmigIV8iKvPXYnHS%2BtNyTOST62DzneK%2B0GfvdMpCQ8Vy73Gp6ExLPzbQP1ugitB6riR4k8tSH6c7P0%2BAS87VHHdDOEnxG0LMAyi0o5rJOxyXCBasDFl%2BxtX6Emcc5w3vGBayPDsQXn%2BU%2F3kQKI1UNOdeWVGqPjRfUQ%2FSOfyfF4bZKGANrIZdy4N5%2F%2Bu5ALocPrQYWJGG5ACxVBtyje9Cr4Rh4pFBYHDRZihe%2FC6suRLeYnHgotzoHhnb5kx0BHop6ekFwuTkq45URWIrlotM65t1cf6KJP8TP1dra6fkj1s5tQTPZXUllblNKob1k9uwMqFIfJN%2BxntNgFsKxLLOTuo%2BAoxZI56VJCvPdEM8KbJBhITFEJ6RYprLJKp2HVyRw%2FV%2B6cBusNqTEXcolmjw%2BGEmr95J2WIWYzg5bKdgsHHcL%2BU7jGJrsFJ4XSw%3D%3D&checksum=1517446078998331e6276f6540568559d650d87557d2"
        if number==9:
            url="https://www.ebay.com/itm/Beethoven-Bust-greek-statue-NEW-Free-Shipping-Tracking/324033228062?hash=item4b71e2ad1e:g:h9wAAOSwcqZbXXy9"
        if number==10:
            url='https://www.ebay.com/itm/WONDERFUL-ARIA-A100F-HAND-MADE-POWERFUL-VERY-SPANISH-FLAMENCO-CONCERT-GUITAR/192886430464?_trkparms=ispr%3D1&hash=item2ce8ed5b00:g:XeEAAOSwxH1UDIFA&enc=AQAEAAACQBPxNw%2BVj6nta7CKEs3N0qUu4hJMFjE2QsujxliNJ9QRvLlu5wMAoISDDe0JIgYW9Rb%2BldgWw%2B2zyjR%2BsrfCusWB50dAxYiuM2L0quJjB2nRMb5ydEfPXLGIr3wom1hUpxHbE5F%2FJbHOU1PQkbAAG1%2F82SMLZ8oHjrDDOq3ksJxYUgX%2F2XxE883AMly1rJOX90y0voEhoErzfiS8F6wzgCSKmD76tpBGfCn7%2Fpuz2F%2B4JSKspwsWSAPpWqL6pkroWQnYKDe7fYVCpVRw5oxj3OrpNp9siW54wmVYyPYvMpQAV673wNMlfIDnqMJtthCeFLEYVIPZ4866Ha7WtOEs3gXrkMkMRZUffmmpOvmWGC%2FmmX%2BhcC7POd6SWhfKOQYFlyGVe8TgFBTXq0SXsfrQSZPAL%2FigoF7CSHcBIapMqSQe0r5YTQnAMOg8i%2Ba5vRM8Ccm83PaCGyKMcYWSCV3KftCCrz05NOI4JrdYuyiCdarTCrMu%2B11Xg6Yq1HQHegMvJGCQyznBX%2FvTnsIh8PSz%2BkwTA2VDzLw2KxA66fofjCv5YAfwLEeKaJ%2FENkQ39RNlIb%2BQCr9HUlvyUULx8Xh0tbq8Wi9KHzjgg0iCjezbhfdSKROblPZIN0LtNyDLfVRYs%2FrcMgmP1SSiN%2FP4cVcS7c3osrZjzdU42%2BWm8EOFDy18Zzd%2FTpRxQ3cYuF1qsY%2FTQAHV981LBgTXGkPUrHCMf0ZngKLY0TBFL9Co4IL5WXeAf%2BpT7XsGuKHAlkmWPM6paQ%3D%3D&checksum=19288643046445a81391c57d492e9ad6126d5f1ce45b'
        if number==11:
            url='https://www.ebay.com/itm/Samsung-43-Class-4K-2160P-Smart-LED-TV-UN43NU6900B/123989349376?epid=22034424683&_trkparms=ispr%3D1&hash=item1cde575400:g:ksIAAOSwxw5eUEBE&enc=AQAEAAACMBPxNw%2BVj6nta7CKEs3N0qUWtl6q3PsfafmwE1pJbSj8rliTBktRvJWcBL9372%2F2JY9mpXcrFREn803%2FoVRuPBJvntV6MLJ3VZWZX8MBBCOc%2FwtGltqJ%2B5bm8HhqhntmtiImrtQGE1k%2Fyoiwe1DoJLqA61NEdrJj9wJ3YkSaA%2BRoV75nhqhuYWwpCbiP5iuWzoQTwNHkKe5Fk8GZd5jvZBZUF1xAkSYj4Rtj6HHG%2FXp3tyGrV4V8cgvG7ducqelzMQwXSHwdu4jdHPnEa1u4yivJbDKZCWuIYgZZIEnXLMAnc9FHtgkHwKazO4WmBVcKMYuS8sHF4eOTWzwJoOrRiX%2FZX4JLtXNGXXnxaw4lpfBbcnUAeSPnVgp4jKqy3fIp1eM%2Bqc8bFgbDlV%2Bn3mZWrnFg2skfyRFtud8e0x79wJ8CWBqIFwFgsUSxk%2BNOhE38OyNMO7hkVLe74p3EUjLfvv092Unr0kbkEro4%2F2YAlWHdiOu9gyk%2BFN%2BFdPGCKA6DxbJIv6y5XGf%2BFKjC4tks4WhSkMRtkHnlY1Uo1Fj0Kl2BdkidskWRyvx2jNVCCt9YlT2c3TjxlDkDaWOaS4UL1z%2FXt7Ol%2B01K2Bem%2BCQc1pUgCP8BB8TT70asf9fXsHQyswPvL%2Bk9XORGVUb4LBQ94k2XNRv1YatYBTp0XoLR7f4CGtiqHC7JJNZncYsoD2qS%2BzWobfMPAmTHea28RHXqJclvJJwgoVrsS6CuP0ynfqo3&checksum=1239893493761287a77904df4d8db304a2ed7de3b931'
        if number==12:
            url='https://www.ebay.com/itm/5FT-Green-Pines-Artificial-Christmas-Tree-Hinged-With-30M-300-LED-String-Lights/254336362395?_trkparms=ispr%3D1&hash=item3b37a0e79b:g:2hcAAOSwUPVb~hPw&enc=AQAEAAACQBPxNw%2BVj6nta7CKEs3N0qVU04nrsEXDJR6VSaxpN7p7begvnXE%2FCT3MiniCOHm6ZqfFLZjPCLwwsYJy8sddBn10uXM5ZyPfE37JK9QIYWTl36lRYrqHPonN%2BGmjQvqCf%2F6gSOFR%2Fo2IhKbcbQXqzERF50%2FxN3bAUtgeQQzIKDGsEeupZ%2FvLSaKvDsV2XS3tpv0wbETwi1%2BtrsrGE3I4bV5gP%2FBvC5G9D9ko03oKH323MMe2RuMszejyT0dpfyJ9Il0vP1pmuJvcEC6mfE4kdoZ1CXQgVjXNCzRD5Ps6fGEPpHxaO6ZmIIW%2F78%2BurW9RB1XUPKh%2BENP%2BkXPURTWcG45vb92oVGpMyKYdTPlaiS1WHUtg4CnAMPeWk1XgU7XEI2fFQduJfpkajEiQ2JB83PNyNz4fjoe5%2FLupnwDBMm2tYK6daXEoplfZ2yFMX673JZ8tksillDfPHct57UdSq%2FXnYPFmo0ggJ2aifh6EpdA%2FOc4%2FHd59S9p%2B%2BoxGqzhh6lNb6kvXHR8QxUfvF2V9vDBt3SeEtlNyOPxAFGN2mWjUF0tIM2id3EBYBzn6r3xuN162ApgZVrQli33Aw09KkFar%2FmyPCfnv5w%2BYUAjJ0jKbT3oQUB9yfyWfKGw0EzA2tJJK92I0Ap3sPfla1uQgnXuf2mNm00AcKsMmiYMa4yQbh9n7D%2B9kmCnYshianaOdZTet1b%2B04LvCljtArUUSAXQDPgLq4kVpboHrZlj6i0E%2Fxn9Ri8JcTPsC3De3kIAcUQ%3D%3D&checksum=254336362395a269022c6c144636930a0e1b7e660740'
        return url

    def getOrigin(self, soup):
        self.product.origin = self.findElement(soup, ['span', 'itemprop', 'availableAtOrFrom'])

    def getPrice(self, soup):
        for label in Constants.MONEY_LABELS:
            self.product.price = self.findElement(soup, label, money=True)
            if self.product.price:
                break

    def getVolume(self, soup):
        volume_found = False
        for volume_word in Constants.VOLUME_WORDS:
            for volume_label in Constants.VOLUME_LABELS:
                raw_volume = self.findElement(soup, volume_label, containing=volume_word, number=True)
                if raw_volume and self.numberDetection(raw_volume, boolean=True):

                    volume_found = True
                    if volume_word == " x ":
                        self.product.volume = self.cleanVolume(str(raw_volume))
                    else:
                        self.product.volume = round(convertionToIS(raw_volume, volume_word)**3, 6)
                    break
            if volume_found:
                break

    def getWeight(self, soup):
        weight_found = False
        for weight_word in Constants.WEIGHT_WORDS:
            for weight_label in Constants.WEIGHT_LABELS:
                raw_weight = self.findElement(soup, weight_label, containing=weight_word, number=True)
                if raw_weight:
                    self.product.weight = convertionToIS(raw_weight, weight_word)
                    weight_found = True
                    break
            if weight_found:
                break

    def getDestiny(self):
        latlng = str(geocoder.ip('me'))
        self.product.destiny = latlng.split("[")[2].split("]")[0]

    def getDistance(self):
        url_distance = 'https://www.mapdevelopers.com/distance_from_to.php'
        self.browser.get(url_distance)
        self.writeInBox(self.product.origin, ['input', 'id', 'fromInput'])
        self.writeInBox(self.product.destiny, ['input', 'id', 'toInput'])
        self.clickOnButton(['a', 'class', 'link_button'])
        time.sleep(5)
        soup_distance = BeautifulSoup(self.browser.page_source, 'html.parser')
        distance = self.findElement(soup_distance, ['div', 'id', 'status']).split(",")[1].split("kilometers")[0]
        if distance:
            self.product.distance = float(distance)
        # url = 'https://www.google.com/search?q=distance ' + str(self.product.origin) + ' to '+ str(self.product.destiny)
        # self.browser.get(url)
        # soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        # raw_distance = self.findElement(soup, ['div', 'class', 'dDoNo vk_bk'])
        # self.product.distance=convertionToIS(raw_distance.split('mi')[0].strip(),'miles')

    def clickOnXPath(self, x_path):
        element = self.browser.find_element_by_xpath(x_path)
        # print (element.location_once_scrolled_into_view)
        self.browser.execute_script("arguments[0].scrollIntoView();", element)
        self.browser.execute_script("arguments[0].click();", element)

    def writeInBox(self, message, label_message):
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        box = self.getScrapData(soup, label_message)
        if box:
            x_path = self.getXPathFromBeautifulSoupComponent(box[0])
            element = self.browser.find_element_by_xpath(x_path)
            if element:
                self.browser.execute_script("arguments[0].value = '{}';".format(message), element)

    def getScrapData(self, place_to_search, label_list):
        if len(label_list) == 3:
            scraped_data = place_to_search.findAll(label_list[0], {label_list[1]: label_list[2]})
        elif len(label_list) == 2:
            first_value = place_to_search.findAll(label_list[0][0], {label_list[0][1]: label_list[0][2]})
            second_value = place_to_search.findAll(label_list[1][0], {label_list[1][1]: label_list[1][2]})
            scraped_data = []
            if first_value:
                scraped_data.append(first_value[0])
            if second_value:
                scraped_data.append(second_value[0])
        elif len(label_list) == 1:
            scraped_data = place_to_search.select(label_list[0])
        else:
            scraped_data = None
        return scraped_data

    def getXPathFromBeautifulSoupComponent(self, element):
        components = []
        child = element if element.name else element.parent
        for parent in child.parents:
            """
            @type parent: bs4.element.Tag
            """
            siblings = parent.find_all(child.name, recursive=False)
            components.append(
                child.name
                if siblings == [child] else
                '%s[%d]' % (child.name, 1 + siblings.index(child))
            )
            child = parent
        components.reverse()
        return '/%s' % '/'.join(components)

    def clickOnButton(self, label_to_click, browser=False):
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        if len(label_to_click) > 1:
            button = soup.findAll(label_to_click[0], {label_to_click[1]: label_to_click[2]})
            if len(button) > 0:
                x_path = self.getXPathFromBeautifulSoupComponent(button[0])
                if browser:
                    element = self.browser.find_element_by_xpath(x_path)
                    element.click()
                else:
                    self.clickOnXPath(x_path)
            # else:
            #     print("Error de scrapeo al clicar en ", self.self.bookmaker.name)
        elif browser:
            self.browser.find_element_by_xpath(label_to_click[0]).click()

    def scrollDown(self):
        for num_press in range(60):
            self.browser.find_element_by_css_selector('body').send_keys(Keys.DOWN)

    def connectionChrome(self, chrome_options=webdriver.ChromeOptions()):
        browser = webdriver.Chrome(
            executable_path=r'/Users/evelazquez/Desktop/ecobuy/ecobuy/ecobuyBE/chromedriver')
        return browser

    def getMaterials(self,soup):
        script=str(soup)
        for material in Constants.CONTAMINANT_MATERIALS:
            if material in script:
                self.product.materials.append(material)

    def getName(self,soup):
        self.product.name = self.findElement(soup, ['h1', 'id', 'itemTitle']).split("Details about")[1].strip()

    def getCountries(self, soup):
        script = str(soup)
        for country in Constants.CONTAMINANT_COUNTRIES:
            if country in script:
                self.product.countries.append(country)

    def scrap(self, url):
        self.browser = self.connectionChrome()
        # url = self.selectOneUrl(random.randint(1,12))
        # url = self.selectOneUrl(12)
        self.browser.get(url)
        is_a_concrete_product = self.findIfIsAConcreteProduct(url)
        if is_a_concrete_product:
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            self.getPrice(soup)
            self.getName(soup)
            self.getVolume(soup)
            self.getWeight(soup)
            self.getOrigin(soup)
            self.getMaterials(soup)
            self.getCountries(soup)
            self.getDestiny()
            self.getDistance()
            self.product.origin_continent = self.getContinent(self.product.origin)
            self.product.destiny_continent = self.getContinent(self.product.destiny)
            self.calculateIndex()
            self.browser.close()
            # self.printResults()
            return self.product
            

class Info:
    def __init__(self):
        self.destiny = None
        self.destiny_continent = None
        self.origin_continent = None
        self.origin = None
        self.distance = 0
        self.weight = 0
        self.volume = 0
        self.materials = []
        self.price = 0
        self.username = None
        self.name=None
        self.ecofriendly_index = 0
        self.index_accuracy = 0
        self.countries=[]

