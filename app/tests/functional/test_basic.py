import pytest
import os

def test_home_page(test_client):
    """
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/',
                    environ_base={'HTTP_X_ORIGINAL_URI': 'http://1.1.1.1:8080/kibana'})
    assert response.status_code == 200
