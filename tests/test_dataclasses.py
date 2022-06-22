from dataclasses_for_parsing import CommonParams, PropParams, BestDeal, asdict


def test_req_params():
    t1 = CommonParams(query='New york')
    assert t1.locale == 'en-US', t1.currency == 'USD'
    assert asdict(t1) == {'query': 'New york', 'locale': 'en-US',
                          'currency': 'USD'}


def test_prop_params():
    t2 = PropParams(
        query='moscow',
        pageSize='3',
        checkOut='2022.12.12',
        checkIn='2022.12.12',
        sortOrder='PRICE',
        destinationId='123444'
    )
    assert t2
    assert t2.locale == 'en-US'
    assert t2.currency == 'USD'


def test_best_deal():
    t3 = BestDeal(
        query='moscow',
        pageSize='3',
        checkOut='2022.12.12',
        checkIn='2022.12.12',
        sortOrder='PRICE',
        priceMax='500',
        priceMin='100',
        destinationId='123444'
    )
    assert t3
    assert t3.locale == 'en-US'
    assert t3.currency == 'USD'

