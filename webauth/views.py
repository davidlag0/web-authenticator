'''webauth Views'''
import logging
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from webauth.models import User, UserAccess

logger = logging.getLogger(__name__)

def get_redirect_url(request):
    '''
    Return URL to redirect to based on URL query parameters used for redirection
    by various applications.
    '''
    # Web Authenticator.
    if request.GET.get('url'):
        return request.GET.get('url')
    # Kibana.
    elif request.GET.get('next'):
        return request.GET.get('next')
    # Jenkins.
    elif request.GET.get('from'):
        return request.GET.get('from')
    else:
        return ''

# TODO: Build this function to do the actual DB call.
# pylint: disable=unused-argument
def authenticate(username, password):
    '''
    Authenticate the user against LDAP and against the local DB using the provided
    credentials.
    '''

    # TODO: Verify user credentials against LDAP here.

    # Assume credentials were verified another way so only verify if the user
    # exists in the database at this point.
    if User.objects.get(username=username):
        return True

def index(request):
    '''Route for root URI'''
    if 'X-Original-URI' in request.headers:
        logger.info('Authentication request from user: %s for URI %s',
                        request.session.get('username'), request.headers['X-Original-URI'])
    else:
        logger.error('Missing header from NGINX: X-Original-URI')

    if 'X-Tool' in request.headers:
        logger.info('tool:%s', request.headers['X-Tool'])

    # As this is the entrypoint of web-auth, save the original URI to use
    # it later to redirect the browser after the auth has passed. Only set
    # it if empty to avoid overwriting it with subsequent calls to this function.
    if request.session.get('logged_in'):

        response = HttpResponse()

        # TODO: To fix when the bottom code block will be uncommented.
        # response['X-Jenkins-User'] = request.session['jenkins_user']

        # TODO: For Kibana, check if the API key is close to expiration and
        # request a new one as needed in the background and update cookie.
        response['X-Kibana-Auth'] = 'ApiKey ' + request.session.get('kibana_auth')

        # Get the global/shared token from a DB so that it can be changed easily.
        response['X-Jupyter-Token'] = 'blopblop'

        return response

    else:
        # We need to return 200 OK with bad credentials. This forces a service
        # to request auth and we can then catch this behavior through NGINX and
        # redirect to our own login page.

        # Kibana and Jenkins.
        # We simply send a 200 OK with no authentication information and we let
        # these tools handle part of the redirection.
        response = HttpResponse()
        response['X-Kibana-Auth'] = ''
        response['X-Jenkins-User'] = ''

        # Jupyter Notebook.
        #print('cookies:', request.cookies)
        # print('cookie name:',
        #      'username-' + request.headers['Host'].replace('.', '-').replace(':', '-'))
        #print('host:', request.headers['Host'])
        # TODO: Commented for now.
        #jupyter_notebook_cookie = 'username-' + \
        #    request['Host'].replace('.', '-').replace(':', '-')
        #response.set_cookie(jupyter_notebook_cookie, '', expires=0, path='/jupyter/')
        #response['X-Jupyter-Token'] = 'badtoken'

        # Keep for now in case this is useful later.
        # if request.headers.get('Content-Type') == 'application/json':
        #    response = Response(json.dumps({'statusCode': 401}),
        #                         status=401,
        #                         mimetype='application/json')
        #    response = make_response(jsonify({'code': 401, 'message': 'Login required.'}), 401)
        #    return response

        return response

@require_http_methods(['GET', 'POST'])
def login(request, tool=''):
    '''Route for /login URI'''
    # TODO: Improve user workflow when a user does not have access to
    # a tool to give him/her a meaningful error message about it.

    logger.info('tool received:%s', tool)

    # If we get a URI to redirect to then redirect to the login page and
    # save that URI to use it.
    url = get_redirect_url(request)

    # Credentials are validated against the DB and if they are valid, the username
    # only is saved. We would also validate credentials against LDAP or such another
    # mean here as well.
    if request.method == 'POST':
        if authenticate(request.POST.get('username'), request.POST.get('password')):
            response = HttpResponseRedirect(url)

            request.session['username'] = request.POST.get('username')
            request.session['logged_in'] = True

            logger.info('User %s logged in successfully', request.session.get('username'))

            # Get credentials for all the tools the user has access to so
            # they are kept in the session cookie for easier access and less
            # database queries.
            # TODO: Possible error checking to do here in case the DB returns nothing.
            # TODO: To fix, put DB call here.
            # db_tools_access_results = DB_CONNECTION.run(
                # pylint: disable=line-too-long
            #     'SELECT tools.short_name FROM users INNER JOIN user_access ON users.user_id = user_access.user_id INNER JOIN tools ON tools.tool_id = user_access.tool_id WHERE users.username=:user', user=session['username'])
            # tools_access = [tool[0] for tool in db_tools_access_results]
            user_obj = User.objects.get(username=request.session.get('username'))
            logger.info('user:%s', user_obj.id)
            logger.info('access:%s', UserAccess.objects.get(user_id=user_obj.id))

            # Kibana.
            # Move forward to validate session and request Elasticsearch API key.
            #
            # TODO: Make the actual call to Elasticsearch API to get a new key.
            #
            # TODO: Don't forget to save the expiration time of the key to check it later
            # and refresh the API key as needed.
            #

            # TODO: Commented this for now. Need to find a stratey that works.
            # # Verify if the user already has a valid API key and if so, use it.
            # es_user_api_keys = ELASTICSEARCH.security.get_api_key(
            #     params={'name': session['username']})

            # for key in es_user_api_keys.get('api_keys'):
            #     if not key.get('invalidated') and \
            #         (int(key.get('expiration')) - int(datetime.now().timestamp() * 1000)) \
            # pylint: disable=line-too-long
            #             > int(timedelta(minutes=ES_SESSION_ABOUT_TO_EXPIRE).total_seconds() * 1000):

            #         session['kibana_auth'] = key.get('id') + ':' + key.get('')

            #print('es:', ELASTICSEARCH.security.create_api_key(body=API_KEY_REQUEST_BODY))
            # print('get es:', ELASTICSEARCH.security.get_api_key(
            #                    params={ 'name': session['username'] }
            #                    ))

            request.session['kibana_auth'] = 'd3VHN2dYSUI5eHhaR3Fmdk1tVUs6b3hnVUJCTDFRMWVoaDhDNS1uTGlIQQ=='

            # TODO: To fix.
            # Jenkins.
            # if 'jenkins' in tools_access:
            #     request.session['jenkins_user'] = request.session['username']
            # else:
            #     request.session['jenkins_user'] = ''

            return response

        else:
            logger.info('User %s failed to log in', request.POST.get('username'))

            # TODO: Better handling of this to give the user an error message.
            return HttpResponse('Wrong password!')

    if not url:
        # To manage the case where a user tries to logout of Kibana only.
        # As NGINX would be setup to redirect to the login page with the query
        # params to ensure a proper flow, there is the case for the
        # "Logout" link that provides no query parameters so if we do not
        # detect any query parameters that would have been added another way
        # we redirect to the main page with the links to the tools.
        response = HttpResponseRedirect('/')
        return response

    # Login page is shown when the user does not POST any credentials.
    context = {'url': url}
    return render(request, 'webauth/index.html', context)

@require_http_methods(['GET'])
def logout(request):
    '''Route for /logout URI'''
    try:
        del request.session['logged_in']
    except KeyError:
        pass

    logger.info('User %s logged out successfully', request.session.get('username'))

    return HttpResponseRedirect('/')
