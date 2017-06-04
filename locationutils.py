import googlemaps
import settings
from operator import itemgetter


CLIENT = googlemaps.Client(key=settings.GOOGLE_MAPS_TOKEN)


def find_nearby_poi(location, type, max_distance=None, max_duration=None, max_results=4):
    results = CLIENT.places_nearby(
        location=location, type=type, rank_by='distance')
    places = []
    for place in results['results'][:max_results]:
        name = place['name']
        rating = place.get('rating', None)
        location = place['geometry']['location']
        places.append({
            'name': name,
            'rating': rating,
            'location': location,
        })

    locations = list(map(itemgetter('location'), places))
    distances = calculate_distances(location, locations)

    for place, distance in zip(places, distances):
        place['distance'] = distance

    func = distance_check(max_distance=max_distance, max_duration=max_duration)
    return list(filter(func, places))


def distance_check(*, max_distance=None, max_duration=None):
    assert max_distance is None or max_duration is None
    if max_distance is not None:
        target = max_distance
        key = 'distance'
    elif max_duration is not None:
        target = max_duration
        key = 'duration'
    else:
        target = None
        # give a key just to test that it is not 0 below
        key = 'distance'

    def inner(place):
        value = place['distance'][key]['value']
        # heuristic, ignore results that are 0
        if not value:
            return False
        return not target or value <= target

    return inner


def calculate_distances(start, places, mode='walking'):
    """
    Calculate the distance between start and each place within the
    places array. Travel duration is calculated based on the travel mode.
    :param start: The starting location.
    :param places: An array of destincations.
    :param mode: The travel mode, either 'driving', 'walking',
        'transit', 'bicycling'.
    :return: A list looking like this:
        [
            {
                'duration': {'text': '4 min', 'value': 215},
                'distance': {'text': '0.6 mi', 'value': 1018}
            }
        ]
    """
    result = CLIENT.distance_matrix(start, places, mode=mode, units='imperial')
    return result['rows'][0]['elements']
