import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
import flask_unittest
from app import app


class TestLanguages(flask_unittest.ClientTestCase):
    # Assign the flask app object otherwise you will get
    # "property `app` must be assigned in ClientTestCase":
    app = app

    def test_add_language(self, client):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = client.post('/languages/add', headers=headers, data='name=abc')
        assert response.status_code == 200

    def test_list_languages(self, client):
        response = client.get('/languages/list')
        assert response.status_code == 200

    def test_view_language0(self, client):
        response = client.get('/languages/view/0')
        assert response.status_code == 200

    def test_view_language_1(self, client):
        response = client.get('/languages/view/-1')
        assert response.status_code == 404


class TestSnippets(flask_unittest.ClientTestCase):
    # Assign the flask app object otherwise you will get
    # "property `app` must be assigned in ClientTestCase":
    app = app

    def test_add_snippet(self, client):
        # at least 1 language should exist - this is done by TestLanguages.test_add_language() test
        data = 'language=1&description=abc-desc&snippet=foo+bar%0D%0Abaz&comment=abc+-+comment'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = client.post('/snippets/add', headers=headers, data=data)
        assert response.status_code == 200

    def test_list_snippets(self, client):
        response = client.get('/snippets/list')
        assert response.status_code == 200

    def test_view_snippet0(self, client):
        response = client.get('/snippets/view/0')
        assert response.status_code == 500  # TODO: fix this bug!

    def test_view_snippet_1(self, client):
        response = client.get('/snippets/view/-1')
        assert response.status_code == 404

class TestAjax(flask_unittest.ClientTestCase):
    app = app

    def test_statistics(self, client):
        response = client.get('/_statistics')
        print(response.json)
        assert response.status_code == 200
        assert 'result' in response.json


# Pass the flask app to suite
suite = flask_unittest.LiveTestSuite(app)
# Add the suites
suite.addTest(unittest.makeSuite(TestSnippets))
suite.addTest(unittest.makeSuite(TestLanguages))
suite.addTest(unittest.makeSuite(TestAjax))
# Run the suite
unittest.TextTestRunner(verbosity=2).run(suite)
