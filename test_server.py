import requests


root = 'http://localhost:8080'


def test_options_works():
    r = requests.options(root+'/say/hi')
    assert r.status_code == 200
    assert "Says hi if you say please" in r.text
    assert "name" in r.text


def test_post_with_args_works():
    d = {"name": 'myname', 'please': False}
    r = requests.post(root+'/say/hi', json=d)
    assert r.status_code == 200, r.text
    assert 'myname' not in r.text
    d = {"name": 'myname', 'please': True}
    r = requests.post(root+'/say/hi', json=d)
    assert r.status_code == 200, r.text
    assert 'myname' in r.text


def test_wrong_type_raises_error():
    d = {"name": 1, 'please': False}
    r = requests.post(root+'/say/hi', json=d)
    assert r.status_code == 400
