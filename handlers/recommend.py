from parsers.recommendation_criteria import parse_criteria
from recommend.maps import CouldNotFindMapException, InvalidDateException
from recommend.recommendation import Recommendation
from recommend.target import NoPlaysException


async def handler(user, message):
    try:
        criteria = parse_criteria(user, message)
        recommendation = await Recommendation.get(criteria)
    except CouldNotFindMapException:
        return 'Could not find a map fitting that criteria :(. Feel free to try !reset'
    except NoPlaysException:
        return 'Please play a few maps and try again!'
    except InvalidDateException:
        return 'Invalid date format! Try 2020-01-01, 2020-01 or 2020'
    return str(recommendation)
