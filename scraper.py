from craigslist import CraigslistHousing
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import sessionmaker
from dateutil.parser import parse
from util import find_points_of_interest
from slackutils import post_listing_to_slack
import time
import settings
import json

engine = create_engine('sqlite:///listings.db', echo=False)

Base = declarative_base()


class Listing(Base):
    """
    A table to store data on craigslist listings.
    """

    __tablename__ = 'listings'

    id = Column(Integer, primary_key=True)
    link = Column(String, unique=True)
    created = Column(DateTime)
    geotag = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    name = Column(String)
    price = Column(Float)
    location = Column(String)
    cl_id = Column(Integer, unique=True)
    area = Column(String)
    pois = Column(String)
    has_all_pois = Column(Boolean)
    keywords = Column(String)
    has_required_keywords = Column(Boolean)
    image = Column(String)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def scrape_area(area):
    """
    Scrapes craigslist for a certain geographic area,
    and finds the latest listings.
    :param area:
    :return: A list of results.
    """
    cl_h = CraigslistHousing(
        site=settings.CRAIGSLIST_SITE, area=area,
        category=settings.CRAIGSLIST_HOUSING_SECTION,
        filters={
            'max_price': settings.MAX_PRICE,
            'min_price': settings.MIN_PRICE,
            'cats_ok': settings.CATS_OKAY,
        })

    results = []
    gen = cl_h.get_results(sort_by='newest', geotagged=True, limit=20, include_details=True)
    while True:
        try:
            result = next(gen)
        except StopIteration:
            break
        except Exception as e:
            print('exception while iterating: {}'.format(e))
            continue
        listing = session.query(Listing).filter_by(cl_id=result["id"]).first()

        # Don't store the listing if it already exists.
        if listing or result["where"] is None:
            # If there is no string identifying which neighborhood
            # the result is from, skip it.
            continue

        lat = 0
        lon = 0
        if result["geotag"] is not None:
            # Assign the coordinates.
            lat, lon = result["geotag"]

            # Annotate the result with information about the area it's
            # in and points of interest near it.
            geo_data = find_points_of_interest(
                result["geotag"], result["where"])
            result.update(geo_data)
        else:
            result["area"] = ""

        # Check for existing keywords if the result has a body
        has_required_keywords = True
        matching_keywords = []
        if 'body' in result:
            body = result['body'].lower()
            for name, keyword_config in settings.KEYWORDS.items():
                keywords = keyword_config['keywords']
                required = keyword_config.get('required', False)

                if any(map(lambda x: x.lower() in body, keywords)):
                    matching_keywords.append(name)
                elif required:
                    has_required_keywords = False

        result['keywords'] = matching_keywords

        # Try parsing the price.
        price = 0
        try:
            price = float(result["price"].replace("$", ""))
        except Exception:
            pass

        # Set the first image for convenience
        images = result.get('images', None)
        result['image'] = images[0] if images else ''

        # Create the listing object.
        listing = Listing(
            link=result["url"],
            created=parse(result["datetime"]),
            lat=lat,
            lon=lon,
            name=result["name"],
            price=price,
            location=result["where"],
            cl_id=result["id"],
            area=result["area"],
            pois=json.dumps(result.get("pois", [])),
            has_all_pois=result.get("has_all_pois", False),
            keywords=','.join(matching_keywords),
            has_required_keywords=has_required_keywords,
            image=result['image']
        )

        # Save the listing so we don't grab it again.
        session.add(listing)
        session.commit()

        # Check that the apartment is available before the configured date.
        # If the listing doesn't mention availability, include it anyway.
        if settings.LATEST_AVAILABILITY is not None:
            available_on = result.get('available_on', None)
            if available_on is not None:
                if available_on.date() > settings.LATEST_AVAILABILITY:
                    continue

        # Return the result if it is in a defined area
        # and it meets the criteria of all configured pois.
        if result["area"] and result["has_all_pois"] and has_required_keywords:
            results.append(result)

    return results


def do_scrape():
    """
    Runs the craigslist scraper, and posts data to slack.
    """
    # Get all the results from craigslist.
    all_results = []
    for area in settings.AREAS:
        all_results += scrape_area(area)

    print("{}: Got {} results".format(time.ctime(), len(all_results)))

    # Post each result to slack.
    for result in all_results:
        post_listing_to_slack(result)

