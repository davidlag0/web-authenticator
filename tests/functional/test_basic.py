'''Basic Tests'''


def test_home_page_without_active_session(test_client):
    '''
    GIVEN a Flask application
    WHEN the '/' page is requested (GET) without an active session
    THEN check the response is valid
    '''
    response = test_client.get(
        '/',
        environ_base={'HTTP_X_ORIGINAL_URI': 'http://1.1.1.1:8080/kibana'})
    assert response.status_code == 200
    assert response.headers['X-Kibana-Auth'] == ''
    assert response.headers['X-Jenkins-User'] == ''


def test_home_page_without_x_original_uri_header(test_client, caplog):
    '''
    GIVEN a Flask application
    WHEN the '/' page is requested (GET) without a X-Original-URI header
    THEN check the response is valid and error message about the missing header is output
    '''
    response = test_client.get('/')
    assert response.status_code == 200
    assert 'Missing header from NGINX: X-Original-URI' in caplog.text


def test_login_without_url(test_client):
    '''
    GIVEN a Flask application
    WHEN the '/login' is requested (GET) without a 'url' query parameter
    THEN check that the user is redirected to the home page
    '''
    response = test_client.get('/login')
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/'


def test_login_with_generic_url(test_client):
    '''
    GIVEN a Flask application
    WHEN the '/login' is requested (GET) with a generic 'url' query parameter
    THEN check that the user is shown the login page
    '''
    response = test_client.get('/login?url=test_url')
    assert response.status_code == 200
    print('response:', vars(response))
    assert b'<title>Login</title>' in response.data
    assert b'action="/auth/login?url=test_url"' in response.data


def test_login_with_kibana_url(test_client):
    '''
    GIVEN a Flask application
    WHEN the '/login' is requested (GET) with a Kibana 'next' query parameter
    THEN check that the user is shown the login page
    '''
    response = test_client.get('/login?next=test_url')
    assert response.status_code == 200
    print('response:', vars(response))
    assert b'<title>Login</title>' in response.data
    assert b'action="/auth/login?url=test_url"' in response.data


def test_login_with_jenkins_url(test_client):
    '''
    GIVEN a Flask application
    WHEN the '/login' is requested (GET) with a Jenkins 'from' query parameter
    THEN check that the user is shown the login page
    '''
    response = test_client.get('/login?from=test_url')
    assert response.status_code == 200
    print('response:', vars(response))
    assert b'<title>Login</title>' in response.data
    assert b'action="/auth/login?url=test_url"' in response.data
