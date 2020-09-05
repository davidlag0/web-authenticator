'''App Helpers'''
import pg8000
from elasticsearch import Elasticsearch


HOME_PAGE = '/'
ES_SESSION_ABOUT_TO_EXPIRE = 1

# Session expiration in minutes.
SESSION_EXPIRATION = 120
ES_SESSION_EXPIRATION = 15

# TODO: Safeguard credentials in env files.
# TODO: Add error checking for the DB (DB down, unreachable, access denied, etc.)
DB_CONNECTION = pg8000.connect('testuser', password='testpass', database='testdb')
# TODO: Add error checking if ELK cluster is down, unreachable, API key expired, etc.
ELASTICSEARCH = Elasticsearch(
    ['https://elastic:changeme@localhost:9200/'],
    verify_certs=False
)

API_KEY_REQUEST_BODY = {
    'name': 'davidlag',
    'expiration': str(ES_SESSION_EXPIRATION) + 'm',
    'role_descriptors': {
        'role': {
            'cluster': ['all'],
            'index': [
                {
                    'names': ['*'],
                    'privileges': ['all']
                }
            ],
            'applications': [
                {
                    'application': 'kibana-.kibana',
                    'privileges': ['all'],
                    'resources': ['*']
                }
            ]
        }
    }
}


# TODO: Build this function to do the actual DB call.
# pylint: disable=unused-argument
def authenticate(username, password):
    '''
    Authenticate the user against the local DB using the provided
    credentials.
    '''

    # TODO: Verify user credentials against LDAP here.

    # Assume credentials were verified another way so only verify if the user
    # exists in the database at this point.
    if len(DB_CONNECTION.run('SELECT * FROM users WHERE username=:user', user=username)) == int(1):
        return True
    else:
        return False


def get_redirect_url(request):
    '''
    Return URL to redirect to based on URL query parameters used for redirection
    by various applications.
    '''
    # Web Authenticator.
    if request.args.get('url'):
        return request.args.get('url')
    # Kibana.
    elif request.args.get('next'):
        return request.args.get('next')
    # Jenkins.
    elif request.args.get('from'):
        return request.args.get('from')
    else:
        return ''
