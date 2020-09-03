'''Web Authenticator Routes'''
#
# The code is based with a mindset of Single-Sign-On (SSO) so when a user
# logs in, all their tools credentials are pulled and they can use any
# tool to which they have access.
#
# That is why, at the current state, a user cannot login/logout of specific
# tools and keep being authenticated to other tools for which they are
# still logged in.
#

from datetime import timedelta, datetime
from flask import session, request, Response, make_response
from flask import redirect, render_template, Blueprint
from flask import current_app as app
from app.auth.helper import DB_CONNECTION, authenticate, get_redirect_url
from app.auth.helper import ELASTICSEARCH, ES_SESSION_ABOUT_TO_EXPIRE
from app.auth.helper import HOME_PAGE

routes_blueprint = Blueprint('auth', __name__)


@routes_blueprint.before_request
def renew_user_session():
    '''Force a renewal of the user session'''
    session.modified = True


@routes_blueprint.route('/')
def index():
    '''Route for root URI'''
    #response = Response('', 401, {'WWW-Authenticate':'Basic realm="Login Required"'})
    #response.headers['X-Original-URI'] = request.headers.get('X-Original-URI')
    #response = Response('', status=200)
    if 'X-Original-URI' in request.headers:
        app.logger.info('Authentication request from user: %s for URI %s',
                        session.get('username'), request.headers['X-Original-URI'])
    else:
        app.logger.error('Missing header from NGINX: X-Original-URI')

    # As this is the entrypoint of web-auth, save the original URI to use
    # it later to redirect the browser after the auth has passed. Only set
    # it if empty to avoid overwriting it with subsequent calls to this function.
    if session.get('logged_in'):

        # Keep for now but as this is the reply to the proxy, probably
        # useless to specify the mimetype.
        #response = Response('', status=200, mimetype='application/json')
        response = Response('', status=200)

        response.headers['X-Jenkins-User'] = session.get('jenkins_user')

        # TODO: For Kibana, check if the API key is close to expiration and
        # request a new one as needed in the background and update cookie.
        response.headers['X-Kibana-Auth'] = 'ApiKey ' + session.get('kibana_auth')

        # Get the global/shared token from a DB so that it can be changed easily.
        response.headers['X-Jupyter-Token'] = 'blopblop'

        return response

    else:
        # We need to return 200 OK with bad credentials. This forces a service
        # to request auth and we can then catch this behavior through NGINX and
        # redirect to our own login page.

        # Kibana and Jenkins.
        # We simply send a 200 OK with no authentication information and we let
        # these tools handle part of the redirection.
        response = Response('', status=200)
        response.headers['X-Kibana-Auth'] = ''
        response.headers['X-Jenkins-User'] = ''

        # Jupyter Notebook.
        #print('cookies:', request.cookies)
        # print('cookie name:',
        #      'username-' + request.headers['Host'].replace('.', '-').replace(':', '-'))
        #print('host:', request.headers['Host'])
        jupyter_notebook_cookie = 'username-' + \
            request.headers['Host'].replace('.', '-').replace(':', '-')
        response.set_cookie(jupyter_notebook_cookie, '', expires=0, path='/jupyter/')
        response.headers['X-Jupyter-Token'] = 'badtoken'

        # Keep for now in case this is useful later.
        # if request.headers.get('Content-Type') == 'application/json':
        #    response = Response(json.dumps({'statusCode': 401}),
        #                         status=401,
        #                         mimetype='application/json')
        #    response = make_response(jsonify({'code': 401, 'message': 'Login required.'}), 401)
        #    return response

        return response


@routes_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    '''Route for /login URI'''
    # TODO: Improve user workflow when a user does not have access to
    # a tool to give him/her a meaningful error message about it.

    # If we get a URI to redirect to then redirect to the login page and
    # save that URI to use it.
    url = get_redirect_url(request)

    # Credentials are validated against the DB and if they are valid, the username
    # only is saved. We would also validate credentials against LDAP or such another
    # mean here as well.
    if request.method == 'POST':
        if authenticate(request.form['username'], request.form['password']):
            response = make_response(redirect(url))

            session['username'] = request.form['username']
            session['logged_in'] = True
            session.permanent = True

            app.logger.info('User %s logged in successfully',
                            session.get('username'))

            # Get credentials for all the tools the user has access to so
            # they are kept in the session cookie for easier access and less
            # database queries.
            # TODO: Possible error checking to do here in case the DB returns nothing.
            db_tools_access_results = DB_CONNECTION.run(
                # pylint: disable=line-too-long
                'SELECT tools.short_name FROM users INNER JOIN user_access ON users.user_id = user_access.user_id INNER JOIN tools ON tools.tool_id = user_access.tool_id WHERE users.username=:user', user=session['username'])
            tools_access = [tool[0] for tool in db_tools_access_results]

            # Kibana.
            # Move forward to validate session and request Elasticsearch API key.
            #
            # TODO: Make the actual call to Elasticsearch API to get a new key.
            #
            # TODO: Don't forget to save the expiration time of the key to check it later
            # and refresh the API key as needed.
            #

            # Verify if the user already has a valid API key and if so, use it.
            es_user_api_keys = ELASTICSEARCH.security.get_api_key(
                params={'name': session['username']})

            for key in es_user_api_keys.get('api_keys'):
                if not key.get('invalidated') and \
                    (int(key.get('expiration')) - int(datetime.now().timestamp() * 1000)) \
                        > int(timedelta(minutes=ES_SESSION_ABOUT_TO_EXPIRE).total_seconds() * 1000):

                    session['kibana_auth'] = key.get('id') + ':' + key.get('')

            #print('es:', ELASTICSEARCH.security.create_api_key(body=API_KEY_REQUEST_BODY))
            # print('get es:', ELASTICSEARCH.security.get_api_key(
            #                    params={ 'name': session['username'] }
            #                    ))

            session['kibana_auth'] = 'd3VHN2dYSUI5eHhaR3Fmdk1tVUs6b3hnVUJCTDFRMWVoaDhDNS1uTGlIQQ=='

            # Jenkins.
            if 'jenkins' in tools_access:
                session['jenkins_user'] = session['username']
            else:
                session['jenkins_user'] = ''

            return response

        else:
            app.logger.warning('User %s failed to log in',
                               request.form['username'])

            # TODO: Better handling of this to give the user an error message.
            return 'Wrong password!'

    if not url:
        # To manage the case where a user tries to logout of Kibana only.
        # As NGINX would be setup to redirect to the login page with the query
        # params to ensure a proper flow, there is the case for the
        # "Logout" link that provides no query parameters so if we do not
        # detect any query parameters that would have been added another way
        # we redirect to the main page with the links to the tools.
        response = make_response(redirect(HOME_PAGE, code=302))
        return response

    # Login page is shown when the user does not POST any credentials.
    return render_template('login.html', url=url)


@routes_blueprint.route('/logout', methods=['GET'])
def logout():
    '''Route for /logout URI'''
    session['logged_in'] = False

    app.logger.info('User %s logged out successfully',
                    session.get('username'))

    # Keep as reference for now.
    # if request.args.get('next'):
    #    response = make_response(redirect(url_for('login', _external=True)))
    #    return response

    # Redirect to home page with links to tools.
    response = make_response(redirect(HOME_PAGE, code=302))
    return response
