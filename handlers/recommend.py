from parsers.recommendation_criteria import parse_criteria
from recommendation.recommendation import Recommendation
from recommendation.maps import CouldNotFindMapException


async def handler(user, message):
    criteria = parse_criteria(user, message)
    try:
        recommendation = await Recommendation.get(criteria)
    except CouldNotFindMapException:
        return "Could not find a map for you. Feel free to try !reset"
    return str(recommendation)
