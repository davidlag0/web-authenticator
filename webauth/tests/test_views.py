'''Tests for webauth views'''
from django.test import TestCase

class HomePageTests(TestCase):
    '''Tests for the home (/) URI'''

    def test_kibana_home_page_without_active_session(self):
        '''
        GIVEN a Django application
        WHEN the '/kibana' page is requested (GET) without an active session
        THEN check the response is valid
        '''
        response = self.client.get(
            '/kibana',
            HTTP_X_ORIGINAL_URI='http://localhost/test_url')
        assert response.status_code == 200
        assert response['X-Kibana-Auth'] == ''
        assert response['X-Jenkins-User'] == ''

    def test_jenkins_home_page_without_active_session(self):
        '''
        GIVEN a Django application
        WHEN the '/jenkins' page is requested (GET) without an active session
        THEN check the response is valid
        '''
        response = self.client.get(
            '/jenkins',
            HTTP_X_ORIGINAL_URI='http://localhost/test_url')
        assert response.status_code == 200
        assert response['X-Kibana-Auth'] == ''
        assert response['X-Jenkins-User'] == ''

    def test_jupyter_home_page_without_active_session(self):
        '''
        GIVEN a Django application
        WHEN the '/jupyter' page is requested (GET) without an active session
        THEN check the response is valid
        '''
        response = self.client.get(
            '/jupyter',
            HTTP_X_ORIGINAL_URI='http://localhost/test_url')
        assert response.status_code == 200
        assert response['X-Kibana-Auth'] == ''
        assert response['X-Jenkins-User'] == ''

    def test_kibana_home_page_without_x_original_uri_header(self):
        '''
        GIVEN a Django application
        WHEN the '/kibana' page is requested (GET) without a X-Original-URI header
        THEN check the response is valid and error message about the missing header is output
        '''
        with self.assertLogs(logger='webauth', level='ERROR') as logger_messages:
            response = self.client.get('/kibana')
            assert response.status_code == 200
            self.assertIn(
                'ERROR:webauth.views:Missing header from NGINX: X-Original-URI',
                logger_messages.output
            )

    def test_jenkins_home_page_without_x_original_uri_header(self):
        '''
        GIVEN a Django application
        WHEN the '/jenkins' page is requested (GET) without a X-Original-URI header
        THEN check the response is valid and error message about the missing header is output
        '''
        with self.assertLogs(logger='webauth', level='ERROR') as logger_messages:
            response = self.client.get('/jenkins')
            assert response.status_code == 200
            self.assertIn(
                'ERROR:webauth.views:Missing header from NGINX: X-Original-URI',
                logger_messages.output
            )

    def test_jupyter_home_page_without_x_original_uri_header(self):
        '''
        GIVEN a Django application
        WHEN the '/jupyter' page is requested (GET) without a X-Original-URI header
        THEN check the response is valid and error message about the missing header is output
        '''
        with self.assertLogs(logger='webauth', level='ERROR') as logger_messages:
            response = self.client.get('/jupyter')
            assert response.status_code == 200
            self.assertIn(
                'ERROR:webauth.views:Missing header from NGINX: X-Original-URI',
                logger_messages.output
            )

    def test_home_page_without_active_session_and_for_no_specific_tool(self):
        '''
        GIVEN a Django application
        WHEN the '/' page is requested (GET) without an active session
             and without specifying a tool
        THEN check the response is valid
        '''
        response = self.client.get(
            '/',
            HTTP_X_ORIGINAL_URI='http://localhost/test_url')
        assert response.status_code == 404

    def test_home_page_without_active_session_for_unknown_tool(self):
        '''
        GIVEN a Django application
        WHEN the '/unknowntool' page is requested (GET) without an active session
        THEN check the response is valid
        '''
        response = self.client.get(
            '/unknowntool',
            HTTP_X_ORIGINAL_URI='http://localhost/test_url')
        assert response.status_code == 404

    def test_login_page_without_url_and_no_specific_tool(self):
        '''
        GIVEN a Django application
        WHEN the '/login/' is requested (GET) without a 'url' query parameter
             and for no specific tool
        THEN check that the user is redirected to the home page
        '''
        response = self.client.get('/login/')
        assert response.status_code == 404

    def test_kibana_login_page_without_url(self):
        '''
        GIVEN a Django application
        WHEN the '/login/kibana' is requested (GET) without a 'url' query parameter
        THEN check that the user is redirected to the home page
        '''
        response = self.client.get('/login/kibana')
        assert response.status_code == 302
        assert response['Location'] == '/'

    def test_kibana_login_page_with_generic_url(self):
        '''
        GIVEN a Django application
        WHEN the '/login/kibana' is requested (GET) with a generic 'url' query parameter
        THEN check that the user is shown the login page
        '''
        response = self.client.get('/login/kibana?url=test_url')
        assert response.status_code == 200
        assert b'<title>Login</title>' in response.content
        assert b'action="/auth/login/kibana?url=test_url"' in response.content

    def test_kibana_login_page_with_kibana_url(self):
        '''
        GIVEN a Django application
        WHEN the '/login/kibana' is requested (GET) with a Kibana 'next' query parameter
        THEN check that the user is shown the login page
        '''
        response = self.client.get('/login/kibana?next=test_url')
        assert response.status_code == 200
        assert b'<title>Login</title>' in response.content
        assert b'action="/auth/login/kibana?url=test_url"' in response.content

    def test_jenkins_login_page_without_url(self):
        '''
        GIVEN a Django application
        WHEN the '/login/jenkins' is requested (GET) without a 'url' query parameter
        THEN check that the user is redirected to the home page
        '''
        response = self.client.get('/login/jenkins')
        assert response.status_code == 302
        assert response['Location'] == '/'

    def test_jenkins_login_page_with_generic_url(self):
        '''
        GIVEN a Django application
        WHEN the '/login/jenkins' is requested (GET) with a generic 'url' query parameter
        THEN check that the user is shown the login page
        '''
        response = self.client.get('/login/jenkins?url=test_url')
        assert response.status_code == 200
        assert b'<title>Login</title>' in response.content
        assert b'action="/auth/login/jenkins?url=test_url"' in response.content

    def test_jenkins_login_page_with_jenkins_url(self):
        '''
        GIVEN a Django application
        WHEN the '/login/jenkins' is requested (GET) with a Jenkins 'from' query parameter
        THEN check that the user is shown the login page
        '''
        response = self.client.get('/login/jenkins?from=test_url')
        assert response.status_code == 200
        assert b'<title>Login</title>' in response.content
        assert b'action="/auth/login/jenkins?url=test_url"' in response.content
