## proj_nps.py
## Skeleton for Project 2, Winter 2018
## ~~~ modify this file, but don't rename it ~~~
from requests_oauthlib import OAuth1
from requests_oauthlib import OAuth1Session
import json
import plotly.plotly as py
#import sys
import requests
from bs4 import BeautifulSoup
import secrets


## SI 507 - Project2
## Name: Zheyi Tian
## UMID: 36521510
## Your section day/time: 006

## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)

Google_API_Key = secrets.google_places_key

CACHE_FNAME = 'National_Site.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

CF2 = 'Nearby_Place.json'
try:
    cache_file = open(CF2, 'r')
    cache_contents2 = cache_file.read()
    CD2 = json.loads(cache_contents2)
    cache_file.close()
except:
    CD2 = {}

class NationalSite():


    def __init__(self, parktype, name, desc, parkurl=None, street="", city="", state="", zipcode=""):
        self.type = parktype
        self.name = name
        self.description = desc
        self.url = parkurl

        self.address_street = street
        self.address_city = city
        self.address_state = state
        self.address_zip = zipcode

    def __str__(self):
        printout_result = "{} ({}): {}, {}, {} {}".format(self.name, self.type, self.address_street, self.address_city, self.address_state, self.address_zip)
        return printout_result

## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)
class NearbyPlace():
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

## Must return the list of NationalSites for the specified state
## param: the 2-letter state abbreviation, lowercase
##        (OK to make it work for uppercase too)
## returns: all of the NationalSites
##        (e.g., National Parks, National Heritage Sites, etc.) that are listed
##        for the state at nps.gov
def get_sites_for_state(state_abbr):

    if state_abbr in CACHE_DICTION:
        #print("Getting cached data...")
        printout_list = []
        for i in CACHE_DICTION[state_abbr]:
            j = NationalSite(i["parktype"], i["name"], i["desc"], i["parkurl"], i["street"], i["city"], i["state"], i["zipcode"])
            printout_list.append(j)
        return(printout_list)
    else:
        pass 

    CACHE_DICTION[state_abbr] = []

    nps_url = "https://www.nps.gov/index.htm"
    basic_url = "https://www.nps.gov"
    state_url = "https://www.nps.gov/state/{}/index.htm".format(state_abbr)
    state_nps = requests.get(state_url).text
    soup = BeautifulSoup(state_nps, 'html.parser')

    allpark_chunk = soup.find('ul', attrs = {'id':'list_parks'})
    nps_chunk_list = allpark_chunk.find_all('li', attrs = {'class': 'clearfix'})
    #print(len(nps_chunk_list))

    for each_nps_chunk in nps_chunk_list:
        parktype = each_nps_chunk.find('h2').string
        name = each_nps_chunk.find('h3').string
        desc = each_nps_chunk.find('p').string
        parkurl = basic_url + each_nps_chunk.find('a')['href'] + 'index.htm'

        park_detail = requests.get(parkurl).text
        park_page = BeautifulSoup(park_detail, 'html.parser')
        address_chunk = park_page.find('div', attrs = {'class':'mailing-address'})
        street = address_chunk.find('span', attrs = {'itemprop':'streetAddress'}).text.strip()
        if street is not None:
            street = street.replace('\n', ', ') 
        city = address_chunk.find('span', attrs = {'itemprop':'addressLocality'}).text.strip()
        state = address_chunk.find('span', attrs = {'itemprop':'addressRegion'}).text.strip()
        zipcode = address_chunk.find('span', attrs = {'itemprop':'postalCode'}).text.strip()
        zipcode = zipcode[0:5]

        ii = {"parktype":parktype, "name":name, "desc":desc, "parkurl":parkurl, "street":street, "city":city, "state":state, "zipcode":zipcode}
        CACHE_DICTION[state_abbr].append(ii)

    dumped_json_cache = json.dumps(CACHE_DICTION)
    fw = open(CACHE_FNAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 
    
    for i in CACHE_DICTION[state_abbr]:
        printout_list = []
        for i in CACHE_DICTION[state_abbr]:
            j = NationalSite(i["parktype"], i["name"], i["desc"], i["parkurl"], i["street"], i["city"], i["state"], i["zipcode"])
            printout_list.append(j)
        return(printout_list)

#aa = get_sites_for_state("az")
#for i in aa:
#    print(i)


## Must return the list of NearbyPlaces for the specifite NationalSite
## param: a NationalSite object
## returns: a list of NearbyPlaces within 10km of the given site
##          if the site is not found by a Google Places search, this should
##          return an empty list
def get_nearby_places_for_site(national_site):
    uniquename = national_site.name.replace(" ", "+") + "+" + national_site.type.replace(" ", "+")
	
    if uniquename in CD2:
        #print("Getting cached data...")
        nearby_list = []
        for i in CD2[uniquename]["nearby_places"]:
            nearby_instance = NearbyPlace(i)
            nearby_list.append(nearby_instance)
        return(nearby_list)
    else:
        pass

    #Search for the lat and lng of the NPS site
    baseurl = "https://maps.googleapis.com/maps/api/place/textsearch/json?query={}&key={}".format(uniquename, Google_API_Key)

    resp = requests.get(baseurl)
    TEMP_DICT = json.loads(resp.text)

    if TEMP_DICT['results']==[]:
        nearby_list = []
        return(nearby_list)

    NPS_lat = TEMP_DICT['results'][0]["geometry"]['location']['lat']
    NPS_lng = TEMP_DICT['results'][0]["geometry"]['location']['lng']


    CD2[uniquename] = {}
    CD2[uniquename]['lat'] = NPS_lat
    CD2[uniquename]['lng'] = NPS_lng

    #Search for nearby places
    nearbyurl = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={},{}&radius=10000&key={}".format(NPS_lat, NPS_lng, Google_API_Key)
    resp2 = requests.get(nearbyurl)
    TEMP_DICT2 = json.loads(resp2.text)
    CD2[uniquename]["nearby_places"] = {}
    nearby_list = []
    for i in TEMP_DICT2["results"]:
        nearby_item_name = i["name"]
        nearby_instance = NearbyPlace(i["name"])
        nearby_list.append(nearby_instance)
        CD2[uniquename]["nearby_places"][nearby_item_name] = {}
        CD2[uniquename]["nearby_places"][nearby_item_name]["lat"] = i["geometry"]["location"]["lat"]
        CD2[uniquename]["nearby_places"][nearby_item_name]["lng"] = i["geometry"]["location"]["lng"]

    json_string = json.dumps(CD2) # Then, use json.dumps to get a str
    fw1 = open("Nearby_Place.json","w") 
    fw1.write(json_string)
    fw1.close()

    return(nearby_list) 



## Must plot all of the NationalSites listed for the state on nps.gov
## Note that some NationalSites might actually be located outside the state.
## If any NationalSites are not found by the Google Places API they should
##  be ignored.
## param: the 2-letter state abbreviation
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_sites_for_state(state_abbr):
    lat_vals = []
    lon_vals = []
    text_vals = []
    new_nearby_list = ["just a list"]

    if state_abbr in CACHE_DICTION:
        #print("Getting cached data...")
        #nps_printout_list = []
        #new_nearby_list = []
        for i in CACHE_DICTION[state_abbr]:
            j = NationalSite(i["parktype"], i["name"], i["desc"], i["parkurl"], i["street"], i["city"], i["state"], i["zipcode"])
            uniquename = j.name.replace(" ", "+") + "+" + j.type.replace(" ", "+")
            if uniquename not in CD2:
                new_nearby_list = get_nearby_places_for_site(j) #To get the lat and lon for NPS
            if new_nearby_list != []:
                lat_vals.append(CD2[uniquename]['lat'])
                lon_vals.append(CD2[uniquename]['lng'])
                text_vals.append(j.name)
                          
    else:
        new_state_list = get_sites_for_state(state_abbr)
        for j in new_state_list:
            uniquename = j.name.replace(" ", "+") + "+" + j.type.replace(" ", "+")
            new_nearby_list = get_nearby_places_for_site(i)
            if new_nearby_list != []:
                lat_vals.append(CD2[uniquename]['lat'])
                lon_vals.append(CD2[uniquename]['lng'])
                text_vals.append(j.name)

    trace1 = dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = lon_vals,
        lat = lat_vals,
        text = text_vals,
        mode = 'markers',
        marker = dict(
            size = 20,
            symbol = 'star',
            color = 'red'
        ))

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
    padding = max_range * .10
    lat_axis = [min_lat - padding, max_lat + padding]
    lon_axis = [min_lon - padding, max_lon + padding]

    layout = dict(
        title = 'National Parks In {}'.format(state_abbr),
        geo = dict(
            scope='usa',
            projection=dict( type='albers usa' ),
            showocean = True,
            showlakes = True,
            showland = True,
            landcolor = "rgb(250, 250, 250)",
            subunitcolor = "rgb(100, 217, 217)",
            countrycolor = "rgb(217, 100, 217)",
            lataxis = {'range': lat_axis},
            lonaxis = {'range': lon_axis},
            center = {'lat': center_lat, 'lon': center_lon },
            countrywidth = 3,
            subunitwidth = 3
        ),
    )

    fig = dict(data=[trace1], layout=layout )
    py.plot( fig, validate=False, filename='National Parks in {}'.format(state_abbr))


## Must plot up to 20 of the NearbyPlaces found using the Google Places API
## param: the NationalSite around which to search
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_nearby_for_site(site_object):
    nps_lat_vals = []
    nps_lon_vals = []
    nps_text_vals = []
    
    nearby_lat_vals = []
    nearby_lon_vals = []
    nearby_text_vals = []

    uniquename = site_object.name.replace(" ", "+") + "+" + site_object.type.replace(" ", "+")

    if uniquename not in CD2:
        new_nearby_list = get_nearby_places_for_site(site_object)
    
    for j in CD2[uniquename]["nearby_places"]:
        nearby_lat_vals.append(CD2[uniquename]["nearby_places"][j]["lat"])
        nearby_lon_vals.append(CD2[uniquename]["nearby_places"][j]["lng"])
        nearby_text_vals.append(j)

    nps_lat_vals.append(CD2[uniquename]["lat"])
    nps_lon_vals.append(CD2[uniquename]["lng"])
    nps_text_vals.append(uniquename)

    trace1 = dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = nps_lon_vals,
        lat = nps_lat_vals,
        text = nps_text_vals,
        mode = 'markers',
        marker = dict(
            size = 20,
            symbol = 'star',
            color = 'red'
        ))

    trace2 = dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = nearby_lon_vals,
        lat = nearby_lat_vals,
        text = nearby_text_vals,
        mode = 'markers',
        marker = dict(
            size = 8,
            symbol = 'square',
            color = 'red'
        ))

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    lat_vals = nps_lat_vals + nearby_lat_vals
    lon_vals = nps_lon_vals + nearby_lon_vals

    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
    padding = max_range * .10
    lat_axis = [min_lat - padding, max_lat + padding]
    lon_axis = [min_lon - padding, max_lon + padding]

    layout = dict(
        title = 'Places near {} {}'.format(site_object.name, site_object.type),
        geo = dict(
            scope='usa',
            projection=dict( type='albers usa' ),
            showocean = True,
            showlakes = True,
            showland = True,
            landcolor = "rgb(250, 250, 250)",
            subunitcolor = "rgb(100, 217, 217)",
            countrycolor = "rgb(217, 100, 217)",
            lataxis = {'range': lat_axis},
            lonaxis = {'range': lon_axis},
            center = {'lat': center_lat, 'lon': center_lon },
            countrywidth = 3,
            subunitwidth = 3
        ),
    )

    fig = dict(data=[trace1, trace2], layout=layout )
    py.plot( fig, validate=False, filename='Nearby Sites of {}'.format(site_object.name))
    




#######For My Own Test
#site1 = NationalSite('National Monument','Sunset Crater Volcano', 'A volcano in a crater.')
#nearby_places1 = get_nearby_places_for_site(site1)
#print(nearby_places1)


#plot_sites_for_state('mi')
#plot_nearby_for_site(NationalSite('National Park','Yellowstone', 'There is a big geyser there.'))


####Part 4

states_list = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

check_list_exist = None
check_nearby_exist = None
n = 0 #number of nps
nps_commandwindow_list = []
national_site_window = ""
stateabbr_input = ""


#site1 = NationalSite('National Monument','Sunset Crater Volcano', 'A volcano in a crater.')
#nearby_places1 = get_nearby_places_for_site(site1)
#print(nearby_places1)

#for i in nearby_places1:
#    print(i)
def main():

    while True:
        input_words = input("Please input your commands:")
        if input_words[:4] == "list":
            stateabbr_input = input_words[4:].strip()
            stateabbr_input = stateabbr_input.upper()
            if stateabbr_input not in states_list:
                print("Wrong State Abbrivation Input, Please Try Again")
            elif stateabbr_input in states_list:
                n = 0
                nps_commandwindow_list = get_sites_for_state(stateabbr_input)
                for i in nps_commandwindow_list:
                    n += 1 
                    output_str = str(n) + " " + str(i)
                    check_list_exist = 1
                    print(output_str)
            else:
                print("Invalid Input, if you need help, please input 'help'")

        elif input_words[:6] == "nearby":
            result_number_input = input_words[6:].strip()
            result_number_input = int(result_number_input)
            if check_list_exist != 1:
                print("Please run 'list <stateabbr>' command first")
            elif result_number_input not in range(n+1)[1:]:
                print("Please input an integer within the range of numbers of items in list")
            else:
                national_site_window = nps_commandwindow_list[result_number_input-1]
                nn = 0
                for i in get_nearby_places_for_site(national_site_window):
                    #print(i)
                    nn+=1
                    print("{} {}".format(nn, str(i)))
                    check_nearby_exist = 1

        elif input_words == "map":
            if check_nearby_exist == 1:
                plot_nearby_for_site(national_site_window)

            elif check_list_exist == 1:
                plot_sites_for_state(stateabbr_input)

            else:
                print("Please run 'list <stateabbr>' command or 'earby <result_number>' command first")

        elif input_words == "help":
            print("list <stateabbr>\n    available anytime\n    lists all National Sites in a state\n    valid inputs: a two-letter state abbreviation\nnearby <result_number>\n    available only if there is an active result set\n    lists all Places nearby a given result\n    valid inputs: an integer 1-len(result_set_size)\nmap\n    available only if there is an active result set\n    displays the current results on a map\nexit\n    exits the program\nhelp\n    lists available commands (these instructions)\n")


        elif input_words == "exit":
            print("Bye!")
            exit()

        else:
            print("Invalid Input, if you need help, please input 'help'")

if __name__ == '__main__':
    main()




       

