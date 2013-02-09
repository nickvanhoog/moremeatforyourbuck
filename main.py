from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
import json
import os
import pprint
import random

class MainPage(webapp.RequestHandler):
    def get(self):
        images = {"steak":["http://0.static.wix.com/media/01c68a_730785e499ab4ce8c43e26ab335a876b.jpg_1024","http://www.freegreatpicture.com/files/104/30944-meat.jpg","http://prairiemeats.ca/wp-content/uploads/2011/11/F-sirloinSteak19666927.jpg"], 
        "beef":["http://www.freegreatpicture.com/files/104/30959-meat.jpg","http://postsfreshmeatsanddeli.com/ESW/Images/hb.jpg?9569","http://www.pitch.com/binary/0dc0/1360166959-ground_beef.jpg","http://1.bp.blogspot.com/-X6MPY0HXA0k/TpfKCyiwxwI/AAAAAAAAARA/5rnsEf4ByTA/s1600/11554minced_meat.jpg"], 
        "pork":["http://www.amigosfoods.biz/wp-content/uploads/2011/04/pork.jpg","https://www.johndavidsons.com/wp-content/uploads/2012/07/Scottish-Pork-Sirloin-Steaks-Raw1.jpg","http://www.goodhousekeeping.com/cm/goodhousekeeping/images/WZ/1011-pork-lgn.jpg"] }
        
        self.response.headers['Content-Type'] = 'text/html'

        url = "http://ws.geonames.org/findNearbyPostalCodesJSON?formatted=true&lat=36&lng=-79.08"
        result = urlfetch.fetch(url)
        if result.status_code == 200:
            data = json.loads(result.content)
            #self.response.out.write(data["postalCodes"][0]["postalCode"])
            #self.response.out.write("<img height=\"600\" width=\"900\" src=\""+images[random.choice(images.keys())][0]+"\"/>")


        template_values = {
            'item_name': "STEAK",
            'img_url': images[random.choice(images.keys())][0],
            'item_savings': "2.99",
        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)



def main():
    run_wsgi_app(application)



if __name__ == "__main__":
    main()