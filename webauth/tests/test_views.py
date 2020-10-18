'''Tests for webauth views'''
from django.test import TestCase

class HomePageTests(TestCase):
    '''Tests for the home (/) URI'''

    def test_kibana_home_page_without_active_session(self):
        '''
        GIVEN a Django application
        WHEN the '/' page is requested (GET) without an active session
        THEN check the response is valid
        '''
        response = self.client.get(
            '/kibana',
            HTTP_X_ORIGINAL_URI='http://localhost/test_url')
        assert response.status_code == 200
        assert response['X-Kibana-Auth'] == ''
        assert response['X-Jenkins-User'] == ''

    # @patch('webauth.logger')
    def test_kibana_home_page_without_x_original_uri_header(self):
        '''
        GIVEN a Django application
        WHEN the '/' page is requested (GET) without a X-Original-URI header
        THEN check the response is valid and error message about the missing header is output
        '''
        with self.assertLogs(logger='webauth', level='ERROR') as logger_messages:
            response = self.client.get('/kibana')
            assert response.status_code == 200
            self.assertIn(
                'ERROR:webauth.views:Missing header from NGINX: X-Original-URI',
                logger_messages.output
            )
