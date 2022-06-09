import re
import json

PARAMS = {
    'low_high': {
        'query': {
            'text': 'How many hotels do you  want to check?',
            'next_step': 'pageSize',
            'validation_mask': r'\b[a-zA-Z]+',
            'not_valid': 'City name must consist only from letters'
            },
        'pageSize': {
            'text': 'Enter start date in yyyy.mm.dd format',
            'next_step': 'checkIn',
            'validation_mask': r'\b10\b|\b\d\b',
            'not_valid': 'Maximum amount of hotels per request is 10'
            },
        'checkIn': {
            'text': 'Enter end date in yyyy.mm.dd format',
            'next_step': 'checkOut',
            'validation_mask': r'\b202[2-3].(0?[1-9]|1[012]).(0?[1-9]|[12]['
                               r'0-9]|3[01])$',
            'not_valid': 'wrong data input, use yyyy.mm.dd mask'
            },
        'checkOut': {
            'text': 'Do you need photos?',
            'next_step': 'get_photos',
            'validation_mask': r'\b202[2-3].(0?[1-9]|1[012]).(0?[1-9]|[12]['
                               r'0-9]|3[01])$',
            'not_valid': 'wrong data input, use yyyy.mm.dd mask'
            },
        'get_photos': {
            'text': 'Creating request',
            'next_step': 'finish',
            'validation_mask': r'\bYes|\bNo',
            'not_valid': 'Please input Yes or No only'
            }},
    'best_deal': {
        'query': {
            'text': 'Set lowest price',
            'next_step': 'priceMin',
            'validation_mask': r'\b[a-zA-Z]+',
            'not_valid': 'City name must consist only from letters'
            },
        'priceMin': {
            'text': 'Set highest price',
            'next_step': 'priceMax',
            'validation_mask': r'\d+',
            'not_valid': 'Please input numbers only'
        },
        'priceMax': {
            'text': 'Minimum distance in km from the centre of the city',
            'next_step': 'not_closer',
            'validation_mask': r'\d+',
            'not_valid': 'Please input numbers only'
        },
        'not_closer': {
            'text': 'Maximum distance in km from the centre of the city',
            'next_step': 'not_farther',
            'validation_mask': r'\d+',
            'not_valid': 'Please input numbers only'
        },
        'not_farther': {
            'text': 'How many hotels do you  want to check?',
            'next_step': 'pageSize',
            'validation_mask': r'\d+',
            'not_valid': 'Please input numbers only'
        },
        'pageSize': {
            'text': 'Enter start date in yyyy.dd.mm format',
            'next_step': 'checkIn',
            'validation_mask': r'\b10\b|\b\d\b',
            'not_valid': 'Maximum amount of hotels per request is 10'
            },
        'checkIn': {
            'text': 'Enter end date in yyyy.dd.mm format',
            'next_step': 'checkOut',
            'validation_mask': r'\b202[2-3].(0?[1-9]|1[012]).(0?[1-9]|[12]['
                               r'0-9]|3[01])$',
            'not_valid': 'wrong data input, use yyyy.mm.dd'
            },
        'checkOut': {
            'text': 'Do you need photos?',
            'next_step': 'get_photos',
            'validation_mask': r'\b202[2-3].(0?[1-9]|1[012]).(0?[1-9]|[12]['
                               r'0-9]|3[01])$',
            'not_valid': 'wrong data input, use yyyy.mm.dd'
            },
        'get_photos': {
            'text': 'Creating request',
            'next_step': 'finish',
            'validation_mask': r'\bYes|\bNo',
            'not_valid': 'Please input Yes or No only'
            }
}
}


class CreateParams:
    """
    Class which holds methods for setting required params set for questioning
    """
    @classmethod
    async def get_params(cls, command: str) -> dict:
        if re.match(r'/lowe+|/high+', command):
            return PARAMS.get('low_high')
        elif re.match(r'/best_+', command):
            return PARAMS.get('best_deal')
