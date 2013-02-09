from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
import json
import random

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        #self.response.out.write('Hello, webapp World!')

        zipCode = '92677'
        queryStrings = ['beef', 'pork', 'steak']
        TITLE_KEY = 'Title'
        REGULAR_PRICE_KEY = 'RegularPrice'
        SAVINGS_KEY = 'Savings'

        itemDicts = []

        # Compile items
        for q in queryStrings:
            requestURL = 'http://api.smartpea.com/api/deal/?title=' + q +  '&zip=' + zipCode

            result = urlfetch.fetch(requestURL)

            if result.status_code == 200:
                requestContents = result.content
                itemDicts.extend(json.loads(result.content))

        itemDicts = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in itemDicts)]
        currentItem = random.choice(itemDicts)

        while not self.itemHasData(currentItem, [TITLE_KEY, REGULAR_PRICE_KEY, SAVINGS_KEY]):
            currentItem = random.choice(itemDicts)

        currentTitle = str(currentItem[TITLE_KEY])
        currentRegPrice = self.makePrice(str(currentItem[REGULAR_PRICE_KEY]))
        currentSavings = self.makePrice(str(currentItem[SAVINGS_KEY]))
        currentPrice = currentRegPrice - currentSavings


    def makePrice(self, price):
        if price[0] == '$':
            return float(price[1:])
        else:
            return float(price)

    def itemHasData(self, item, keysToCheck):
        for key in keysToCheck:
            if not key in item:
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