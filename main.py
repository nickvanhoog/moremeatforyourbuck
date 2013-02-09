from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

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

        images = {'beef': ["http://www.photographybysolaria.com/photoblog/wp-content/uploads/2012/04/prime_rib_roast_beef_food_photography-05.jpg", "http://sprinklejoy.files.wordpress.com/2011/11/img_5864.jpg", "http://images1.friendseat.com/2011/05/meat-raw-beef.jpg", "http://assets.nydailynews.com/polopoly_fs/1.1249821.1359411293!/img/httpImage/image.jpg_gen/derivatives/landscape_635/134129586.jpg" ], 
        'steak': ["http://www.huwareserve.com/sites/default/files/styles/term_background/public/quarter1_0.jpg", "http://nebraskastarbeef.com/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/n/a/natural-wagyu-12-oz-new-york-strip-raw.jpg", "http://nebraskastarbeef.com/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/n/a/natural-wagyu-8-oz-filet-raw.jpg"],
        'pork': ["http://www.itsfordinner.com/media/uploads/recipe/pulled-pork-oven-bbq/pulled-pork-1-raw.jpg", "http://notgoingoutlikethat.files.wordpress.com/2012/10/pork-tenderloin-raw.jpg?w=600", "http://nomnivores.files.wordpress.com/2011/09/jamestif8-3.jpg"]}

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


        itemDicts  = memcache.get(zipCode)

        if itemDicts is None:
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
            memcache.add(zipCode, itemDicts, 3600)

        currentItem = random.choice(itemDicts)

        while not self.itemHasData(currentItem, [TITLE_KEY, REGULAR_PRICE_KEY, SAVINGS_KEY]):
            currentItem = random.choice(itemDicts)


        itemTitle = self.unicodeToString(currentItem[TITLE_KEY])
        itemRegPrice = self.makePrice(self.unicodeToString(currentItem[REGULAR_PRICE_KEY]))
        itemSavings = self.makePrice(self.unicodeToString(currentItem[SAVINGS_KEY]))
        savingsFormatted = "%.2f" % float(itemSavings[1:])
        currentPriceFloat = float(itemRegPrice[1:]) - float(itemSavings[1:])
        itemCurrentPrice = "%.2f" % currentPriceFloat
        itemImageURL = self.imageFromTitle(itemTitle, images)
        itemRetailer = self.unicodeToString(currentItem[RETAILER_KEY])

        template_values = {
            'item_name': itemTitle,
            'img_url': itemImageURL,
            'item_savings': savingsFormatted,
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
        if price[0] != '$':
            return "$" + price
        else:
            return price

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