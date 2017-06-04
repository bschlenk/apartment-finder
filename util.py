import settings
import math
import locationutils


def coord_distance(lat1, lon1, lat2, lon2):
    """
    Finds the distance between two pairs of latitude and longitude.
    :param lat1: Point 1 latitude.
    :param lon1: Point 1 longitude.
    :param lat2: Point two latitude.
    :param lon2: Point two longitude.
    :return: Kilometer distance.
    """
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    km = 6367 * c
    return km


def in_box(coords, box):
    """
    Find if a coordinate tuple is inside a bounding box.
    :param coords: Tuple containing latitude and longitude.
    :param box: Two tuples, where first is the bottom left, and the second is the top right of the box.
    :return: Boolean indicating if the coordinates are in the box.
    """
    if box[0][0] < coords[0] < box[1][0] and box[1][1] < coords[1] < box[0][1]:
        return True
    return False


def find_points_of_interest(geotag, location):
    """
    Find points of interest, like transit, near a result.
    :param geotag: The geotag field of a Craigslist result.
    :param location: The where field of a Craigslist result.
        Is a string containing a description of where the listing was posted.
    :return: A dictionary containing annotations.
    """
    areas = []

    # Look to see if the listing is in any of the neighborhood boxes we defined.
    for a, coords in settings.BOXES.items():
        if in_box(geotag, coords):
            areas.append(a)

    # Check to see if the listing is near any configured points of interest
    points_of_interest = []
    pois_found = 0
    for poi in settings.POINTS_OF_INTEREST:
        max_distance = poi.get('max_distance', None)
        max_duration = poi.get('max_duration', None)
        if 'type' in poi:
            locations = locationutils.find_nearby_poi(
                geotag, poi['type'],
                max_distance=max_distance, max_duration=max_duration)
            points_of_interest += locations
            if locations:
                pois_found += 1
        elif 'location' in poi:
            distance = locationutils.calculate_distances(
                geotag, [poi['location']])[0]
            loc = {
                'name': poi['name'],
                'distance': distance,
                'location': poi['location'],
            }
            in_range = locationutils.distance_check(
                max_distance=max_distance, max_duration=max_duration)(loc)
            if in_range:
                points_of_interest.append(loc)
                pois_found += 1
        else:
            raise Exception('invalid poi {}'.format(poi))

    # If the listing isn't in any of the boxes we defined, check to see
    # if the string description of the neighborhood matches anything in
    # our list of neighborhoods.
    if not areas:
        for hood in settings.BOXES:
            if hood.lower() in location.lower():
                areas.append(hood)
                break

    return {
        "area": ', '.join(areas),
        "pois": points_of_interest,
        "has_all_pois": pois_found == len(settings.POINTS_OF_INTEREST),
    }
