from requester import ReqParams

tes_form = {'sortOrder': 'PRICE', 'params': '/lowest_price', 'query': 'h h',
            'pageSize': '4', 'checkIn': '2022-12-12', 'checkOut': '2022-12-12',
            'get_photos': 'Yes'}


def test_get_locals():
    t_form = {'query': 'moscow'}
    test_req = ReqParams(t_form)
    test_locals = test_req.get_locals()
    assert isinstance(test_locals, dict)


def test_get_properties():
    test_req = ReqParams(tes_form)
    test_props = test_req.get_properties('1234')
    print(test_props)
    assert isinstance(test_props, dict)
