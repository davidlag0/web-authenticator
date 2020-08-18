import pytest
import os

@pytest.fixture
def app():
    port = int(os.environ.get('PORT', 6001))
    app.run(host='0.0.0.0', port=port, debug=True)
    return app

def test_basic(client):
    response = client.get('/')
    assert response.status_code == 200
