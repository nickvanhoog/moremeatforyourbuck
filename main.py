from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
from django.utils import simplejson as json
import os
import random
import unicodedata

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        queryStrings = ['beef', 'pork', 'steak']
        TITLE_KEY = 'Title'
        REGULAR_PRICE_KEY = 'RegularPrice'
        SAVINGS_KEY = 'Savings'
        RETAILER_KEY = 'BrandName'

        images = {"steak":["http://0.static.wix.com/media/01c68a_730785e499ab4ce8c43e26ab335a876b.jpg_1024","http://www.freegreatpicture.com/files/104/30944-meat.jpg","http://prairiemeats.ca/wp-content/uploads/2011/11/F-sirloinSteak19666927.jpg"], 
        "beef":["http://www.freegreatpicture.com/files/104/30959-meat.jpg","http://postsfreshmeatsanddeli.com/ESW/Images/hb.jpg?9569","http://www.pitch.com/binary/0dc0/1360166959-ground_beef.jpg","http://1.bp.blogspot.com/-X6MPY0HXA0k/TpfKCyiwxwI/AAAAAAAAARA/5rnsEf4ByTA/s1600/11554minced_meat.jpg"], 
        "pork":["http://www.amigosfoods.biz/wp-content/uploads/2011/04/pork.jpg","https://www.johndavidsons.com/wp-content/uploads/2012/07/Scottish-Pork-Sirloin-Steaks-Raw1.jpg","http://www.goodhousekeeping.com/cm/goodhousekeeping/images/WZ/1011-pork-lgn.jpg"] }

        phrases = [ "Wow! That's some cheap meat!", "Holy cow!", "Now THAT'S more meat for your buck!", "Elect meat for president!", 
                    "Who needs fruits and veggies?", "Adopt a meat-only diet!", "Meaterrific!" ]

        latLongFetchURL = "http://api.hostip.info/get_json.php?ip="+self.request.remote_addr+"&position=true"
        result = urlfetch.fetch(latLongFetchURL)
        if result.status_code == 200:
            latLongdata = json.loads(result.content)
            latitude = latLongdata["lat"]
            longitude = latLongdata["lng"]


        if latitude is not None and longitude is not None:
            zipFetchURL = "http://ws.geonames.org/findNearbyPostalCodesJSON?formatted=true&lat="+latitude+"&lng="+longitude
            result = urlfetch.fetch(zipFetchURL)
            if result.status_code == 200:
                data = json.loads(result.content)
                zipCode = data["postalCodes"][0]["postalCode"]
        else:
            zipCode = "90024"

        itemDicts = []

        # Compile items
        for q in queryStrings:
            requestURL = 'http://api.smartpea.com/api/deal/?title=' + q +  '&zip=' + zipCode

            result = urlfetch.fetch(requestURL)

            if result.status_code == 200:
                requestContents = result.content
                itemDicts.extend(json.loads(result.content))

        # Removing duplicates and choosing a random item
        itemDicts = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in itemDicts)]
        currentItem = random.choice(itemDicts)

        while not self.itemHasData(currentItem, [TITLE_KEY, REGULAR_PRICE_KEY, SAVINGS_KEY]):
            currentItem = random.choice(itemDicts)

        itemTitle = self.unicodeToString(currentItem[TITLE_KEY])
        itemRegPrice = self.makePrice(self.unicodeToString(currentItem[REGULAR_PRICE_KEY]))
        itemSavings = self.makePrice(self.unicodeToString(currentItem[SAVINGS_KEY]))
        itemCurrentPrice = itemRegPrice - itemSavings
        itemImageURL = self.imageFromTitle(itemTitle, images)
        itemRetailer = self.unicodeToString(currentItem[RETAILER_KEY])

        template_values = {
            'item_name': itemTitle,
            'img_url': itemImageURL,
            'item_savings': itemSavings,
            'item_regPrice': itemRegPrice,
            'item_currentPrice': itemCurrentPrice,
            'item_retailer': itemRetailer, 
            'zip_code': zipCode,
            'silly_meat_phrase': random.choice(phrases)
        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

    def imageFromTitle(self, itemTitle, images):
        categories = ['beef', 'steak', 'pork']
        lowerTitle = itemTitle.lower()

        for c in categories:
            if c in lowerTitle:
                return random.choice(images[c])

        return random.choice(images[random.choice(categories)])

    def unicodeToString(self, uni):
        return uni.encode('ascii', 'ignore')

    def makePrice(self, price):
        if price[0] == '$':
            return float(price[1:])
        else:
            return float(price)

    def itemHasData(self, item, keysToCheck):
        for key in keysToCheck:
            if not key in item or item[key] is None:
                return False

        return True

    def output(self, x):
        self.response.out.write(x)

        


application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)



def main():
    run_wsgi_app(application)



if __name__ == "__main__":
    main()