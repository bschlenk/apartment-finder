import settings
from slackclient import SlackClient

CLIENT = SlackClient(settings.SLACK_TOKEN)

template = "{area} | {price} | <{url}|{name}>"
poi_template = "* {duration} walk to {name}"
keyword_template = "* mentions {}"


def format_pois(pois):
    texts = []
    for poi in pois:
        name = poi['name']
        duration = poi['distance']['duration']['text']
        texts.append(poi_template.format(**locals()))
    return '\n'.join(texts)


def format_keywords(keywords):
    texts = [keyword_template.format(k) for k in keywords]
    return '\n'.join(texts)


def post_listing_to_slack(listing):
    """
    Posts the listing to slack.
    :param listing: A record of the listing.
    """
    desc = template.format_map(listing)
    keywords = format_keywords(listing['keywords'])
    pois = format_pois(listing['pois'])
    image = listing['image']

    parts = [desc]
    if image:
        parts.append(image)
    parts += [keywords, pois]
    message = '\n'.join(parts)

    CLIENT.api_call(
        "chat.postMessage", channel=settings.SLACK_CHANNEL, text=message,
        username='pybot', icon_emoji=':robot_face:'
    )
