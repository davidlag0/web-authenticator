'''pytest Configuration for tests'''
import pytest
# pylint: disable=import-error
from app import create_app


@pytest.fixture(scope='module')
def test_client():
    '''Test Client'''
    flask_app = create_app('flask_test.cfg')

    # Flask provides a way to test your application by exposing the Werkzeug
    # test Client and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


class AuthActions(object):
    '''AuthActions'''
    def __init__(self, client):
        self._client = client

    def login(self, username='davidlag', password='blop'):
        '''Log the user in'''
        return self._client.post(
            '/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        '''Log the user out'''
        return self._client.get('/logout')


@pytest.fixture
# pylint: disable=redefined-outer-name
def auth(test_client):
    '''Authenticate test user'''
    return AuthActions(test_client)


# TODO: Could be useful later.
"""
@pytest.fixture(scope='module')
def init_database():
    # Create the database and the database table
    db.create_all()

    # Insert user data
    user1 = User(email='patkennedy79@gmail.com',
                 plaintext_password='FlaskIsAwesome')
    user2 = User(email='kennedyfamilyrecipes@gmail.com',
                plaintext_password='PaSsWoRd')
    db.session.add(user1)
    db.session.add(user2)

    # Commit the changes for the users
    db.session.commit()

    yield db  # this is where the testing happens!

    db.drop_all()
"""
