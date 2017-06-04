import settings
from slackclient import SlackClient

CLIENT = SlackClient(settings.SLACK_TOKEN)

template = "{area} | {price} | <{url}|{name}>"
poi_template = "* {duration} walk to {name}"


def format_pois(pois):
    texts = []
    for poi in pois:
        name = poi['name']
        duration = poi['distance']['duration']['text']
        texts.append(poi_template.format(**locals()))
    return '\n'.join(texts)


def post_listing_to_slack(listing):
    """
    Posts the listing to slack.
    :param listing: A record of the listing.
    """
    desc = template.format_map(listing)
    pois = format_pois(listing['pois'])

    message = '\n'.join([desc, pois])

    CLIENT.api_call(
        "chat.postMessage", channel=settings.SLACK_CHANNEL, text=message,
        username='pybot', icon_emoji=':robot_face:'
    )
