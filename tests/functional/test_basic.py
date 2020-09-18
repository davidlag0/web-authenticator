'''Basic Tests'''
import flask


def test_home_page_without_active_session(test_client):
    '''
    GIVEN a Flask application
    WHEN the '/' page is requested (GET) without an active session
    THEN check the response is valid
    '''
    response = test_client.get(
        '/',
        environ_base={'HTTP_X_ORIGINAL_URI': 'http://localhost/test_url'})
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


def test_home_page_with_active_session(test_client):
    '''
    GIVEN a Flask application
    WHEN the '/' page is requested (GET) with an active session
    THEN check the response is valid
    '''

    username = 'testuser_allaccess'

    with test_client as context:
        response = context.post(
            '/login?url=test_url', data={'username': username, 'password': 'testpass'}
        )
        # Confirm the user is really logged in.
        assert flask.session['username'] == username
        assert flask.session['logged_in']

        response = context.get(
            '/', environ_base={'HTTP_X_ORIGINAL_URI': 'http://localhost/test_url'}
        )
        assert response.status_code == 200
        assert response.headers['X-Jenkins-User'] == flask.session['jenkins_user']
        assert response.headers['X-Kibana-Auth'] == 'ApiKey ' + flask.session['kibana_auth']


def test_login_page_without_url(test_client):
    '''
    GIVEN a Flask application
    WHEN the '/login' is requested (GET) without a 'url' query parameter
    THEN check that the user is redirected to the home page
    '''
    response = test_client.get('/login')
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/'


def test_login_page_with_generic_url(test_client):
    '''
    GIVEN a Flask application
    WHEN the '/login' is requested (GET) with a generic 'url' query parameter
    THEN check that the user is shown the login page
    '''
    response = test_client.get('/login?url=test_url')
    assert response.status_code == 200
    assert b'<title>Login</title>' in response.data
    assert b'action="/auth/login?url=test_url"' in response.data


def test_login_page_with_kibana_url(test_client):
    '''
    GIVEN a Flask application
    WHEN the '/login' is requested (GET) with a Kibana 'next' query parameter
    THEN check that the user is shown the login page
    '''
    response = test_client.get('/login?next=test_url')
    assert response.status_code == 200
    assert b'<title>Login</title>' in response.data
    assert b'action="/auth/login?url=test_url"' in response.data


def test_login_page_with_jenkins_url(test_client):
    '''
    GIVEN a Flask application
    WHEN the '/login' is requested (GET) with a Jenkins 'from' query parameter
    THEN check that the user is shown the login page
    '''
    response = test_client.get('/login?from=test_url')
    assert response.status_code == 200
    assert b'<title>Login</title>' in response.data
    assert b'action="/auth/login?url=test_url"' in response.data


def test_successful_user_login_with_kibana_url(test_client, caplog):
    '''
    GIVEN a Flask application
    WHEN credentials are submitted (POST) to the '/login' page with a Kibana 'next' query parameter
    THEN a session cookie is created with user access information
    '''

    # TODO: Mock the database
    username = 'testuser_allaccess'

    with test_client as context:
        response = context.post(
            '/login?next=/kibana/', data={'username': username, 'password': 'testpass'}
        )
        assert response.status_code == 302
        assert response.headers['Location'] == 'http://localhost/kibana/'
        assert flask.session['username'] == username
        assert flask.session['logged_in']
        assert flask.session['kibana_auth']
        assert 'User ' + username + ' logged in successfully' in caplog.text


def test_successful_user_login_with_jenkins_url(test_client, caplog):
    '''
    GIVEN a Flask application
    WHEN credentials are submitted (POST) to the '/login' page with a Jenkins 'from' query parameter
    THEN a session cookie is created with user access information
    '''

    # TODO: Mock the database
    username = 'testuser_allaccess'

    with test_client as context:
        response = context.post(
            '/login?from=/jenkins/', data={'username': username, 'password': 'testpass'}
        )
        assert response.status_code == 302
        assert response.headers['Location'] == 'http://localhost/jenkins/'
        assert flask.session['username'] == username
        assert flask.session['logged_in']
        assert flask.session['jenkins_user'] == username
        assert 'User ' + username + ' logged in successfully' in caplog.text


def test_successful_user_login_with_kibana_url_no_tool_access(test_client, caplog):
    '''
    GIVEN a Flask application
    WHEN credentials are submitted (POST) to the '/login' page with a Kibana 'next' query parameter
         for a user without access to Kibana
    THEN a session cookie is created with invalid user access information
    '''

    # TODO: Mock the database
    username = 'testuser_noaccess'

    with test_client as context:
        response = context.post(
            '/login?next=/kibana/', data={'username': username, 'password': 'testpass'}
        )
        assert response.status_code == 302
        assert response.headers['Location'] == 'http://localhost/kibana/'
        assert flask.session['username'] == username
        assert flask.session['logged_in']
        # TODO: Adjust the below as required once we stop using a fixed API key.
        # assert flask.session['kibana_auth']
        assert 'User ' + username + ' logged in successfully' in caplog.text


def test_successful_user_login_with_jenkins_url_no_tool_access(test_client, caplog):
    '''
    GIVEN a Flask application
    WHEN credentials are submitted (POST) to the '/login' page with a Jenkins 'from' query parameter
         for a user without access to Jenkins
    THEN a session cookie is created with invalid user access information
    '''

    # TODO: Mock the database
    username = 'testuser_noaccess'

    with test_client as context:
        response = context.post(
            '/login?from=/jenkins/', data={'username': username, 'password': 'testpass'}
        )
        assert response.status_code == 302
        assert response.headers['Location'] == 'http://localhost/jenkins/'
        assert flask.session['username'] == username
        assert flask.session['logged_in']
        assert flask.session['jenkins_user'] == ''
        assert 'User ' + username + ' logged in successfully' in caplog.text


def test_failed_user_login(test_client, caplog):
    '''
    GIVEN a Flask application
    WHEN bad credentials are submitted (POST) to the '/login' page with a generic 'url' query
         parameter
    THEN ?
    '''

    # TODO: Mock the database.
    username = 'does_not_exist'

    with test_client as context:
        response = context.post(
            '/login?url=test_url', data={'username': username, 'password': 'testpass'}
        )
        assert response.status_code == 200
        assert 'User ' + username + ' failed to log in' in caplog.text


def test_user_logout(test_client, caplog):
    '''
    GIVEN a Flask application
    WHEN the '/logout' is requested
    THEN the user is logged out and redirected to the home page.
    '''

    username = 'testuser_allaccess'

    with test_client as context:
        response = context.post(
            '/login?url=test_url', data={'username': username, 'password': 'testpass'}
        )
        # Confirm the user is really logged in.
        assert flask.session['username'] == username
        assert flask.session['logged_in']

        # Proceed with logout
        response = context.get('/logout')
        assert not flask.session['logged_in']
        assert 'User ' + username + ' logged out successfully' in caplog.text
        assert response.status_code == 302
        assert response.headers['Location'] == 'http://localhost/'
