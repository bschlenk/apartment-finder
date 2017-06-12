import os
import datetime

# Price

# The minimum rent you want to pay per month.
MIN_PRICE = 0

# The maximum rent you want to pay per month.
MAX_PRICE = 2000

# Whether or not the apartment should allow cats.
CATS_OKAY = True

# Location preferences

# The Craigslist site you want to search on.
# For instance, https://sfbay.craigslist.org is SF and the Bay Area.
# You only need the beginning of the URL.
CRAIGSLIST_SITE = 'seattle'

# What Craigslist subdirectories to search on.
# For instance, https://sfbay.craigslist.org/eby/ is the East Bay,
# and https://sfbay.craigslist.org/sfc/ is San Francisco.
# You only need the last three letters of the URLs.
AREAS = ["see"]

# A list of neighborhoods and coordinates that you want to look for
# apartments in. Any listing that has coordinates attached will be checked
# to see which area it is in.  If there's a match, it will be annotated with
# the area name. If no match, the neighborhood field, which is a string,
# will be checked to see if it matches anything in NEIGHBORHOODS.
BOXES = {
    "Capitol Hill": [
        [47.609019, -122.337135],
        [47.631966, -122.300583],
    ],
    "Leschi": [
        [47.594222, -122.303364],
        [47.607687, -122.28114],
    ],
    "Madrona": [
        [47.605913, -122.307077],
        [47.619374, -122.279829],
    ],
    "Eastlake": [
        [47.62651, -122.331797],
        [47.653478, -122.301865],
    ],
    "South Lake Union": [
        [47.615942, -122.347527],
        [47.642839, -122.328129],
    ],
    "Belltown": [
        [47.600607, -122.36392],
        [47.620657, -122.327271],
    ],
    "First Hill": [
        [47.601266, -122.335145],
        [47.614995, -122.308409],
    ],
    "Queen Anne": [
        [47.616889, -122.378769],
        [47.647696, -122.345831],
    ],
    "Freemont": [
        [47.643996, -122.362547],
        [47.661861, -122.331133],
    ],
}

# A list of neighborhood names to look for in the Craigslist neighborhood name field. If a listing doesn't fall into
# one of the boxes you defined, it will be checked to see if the neighborhood name it was listed under matches one
# of these.  This is less accurate than the boxes, because it relies on the owner to set the right neighborhood,
# but it also catches listings that don't have coordinates (many listings are missing this info).
NEIGHBORHOODS = []

# Points of interest

# Distance is measured in feet
POINTS_OF_INTEREST = [
    {
        "type": "grocery_or_supermarket",
        "max_distance": 5280,
    },
    {
        "location": (47.624175, -122.338894),
        "name": "Brian's office",
        "max_duration": None,  # 2700,
    },
    {
        "location": (47.645383, -122.325724),
        "name": "Paige's office",
        "max_duration": None,  # 2700,
    },
    {
        "location": (47.619773, -122.353754),
        "name": "Dustliz",
        "max_duration": None,
    },
]


# Keywords

# Keywords to look for within the body of the listing.
# The key in the map is used in the slack message for any
# keyword found in the list. Required can be set to false
# to still show a listing that doesn't include the keyword,
# but include extra information.

KEYWORDS = {
    "gym": {
        "keywords": ["gym", "fitness", "fitnesscenter"],
        "required": False,
    },
    "pool": {
        "keywords": ["swimming", "pool", "swimmingpool"],
        "required": False,
    },
}

# Only show apartments who's availability is on or before this date.
# Set to None to show all apartments regardless of availability.
LATEST_AVAILABILITY = datetime.date(2017, 6, 25)


# Search type preferences

# The Craigslist section underneath housing that you want to search in.
# For instance, https://sfbay.craigslist.org/search/apa find apartments for rent.
# https://sfbay.craigslist.org/search/sub finds sublets.
# You only need the last 3 letters of the URLs.
CRAIGSLIST_HOUSING_SECTION = 'apa'

# System settings

# How long we should sleep between scrapes of Craigslist.
# Too fast may get rate limited.
# Too slow may miss listings.
SLEEP_INTERVAL = 20 * 60  # 20 minutes

# Which slack channel to post the listings into.
SLACK_CHANNEL = "#housing"

# The token that allows us to connect to slack.
# Should be put in private.py, or set as an environment variable.
SLACK_TOKEN = os.getenv('SLACK_TOKEN', "")

# The token thtat allows us to make requests to google maps.
GOOGLE_MAPS_TOKEN = os.getenv('GOOGLE_MAPS_TOKEN', '')

# Any private settings are imported here.
try:
    from private import *
except Exception:
    pass

# Any external private settings are imported from here.
try:
    from config.private import *
except Exception:
    pass
