from parsers.recommendation_criteria import parse_criteria
from recommend.maps import CouldNotFindMapException
from recommend.recommendation import Recommendation
from recommend.target import NoPlaysException


async def handler(user, message):
    criteria = parse_criteria(user, message)
    try:
        recommendation = await Recommendation.get(criteria)
    except CouldNotFindMapException:
        return 'Could not find a map fitting that criteria :(. Feel free to try !reset'
    except NoPlaysException:
        return 'Please play a few maps and try again!'
    return str(recommendation)
