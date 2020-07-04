# Web Authenticator
#
# The code is based with a mindset of Single-Sign-On (SSO) so when a user
# logs in, all their tools credentials are pulled and they can use any
# tool to which they have access.
#
# That is why, at the current state, a user cannot login/logout of specific
# tools and keep being authenticated to other tools for which they are
# still logged in.
#

import os
import json
from pprint import pprint
from datetime import timedelta
from flask import Flask, abort, request, make_response, Response
from flask import render_template, redirect, url_for, session, jsonify
import pg8000

app = Flask(__name__)

app.secret_key = b'_8#y4L"F4Q5z\m\bgh]/'

HOME_PAGE = '/'

# To automatically log the user out after 120 minutes.
#minutes=120
app.permanent_session_lifetime = timedelta(seconds=15)

@app.before_request
def renew_user_session():
    session.modified = True

@app.route('/')
def index():
    #response = Response('', 401, {'WWW-Authenticate':'Basic realm="Login Required"'})
    #response.headers['X-Original-URI'] = request.headers.get('X-Original-URI')
    #response = Response('', status=200)
    app.logger.info('Authentication request from user: %s for URI %s',
                    session.get('username'), request.headers['X-Original-URI'])

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
        #print('cookie name:', 'username-' + request.headers['Host'].replace('.', '-').replace(':', '-'))
        #print('host:', request.headers['Host'])
        jupyter_notebook_cookie = 'username-' + request.headers['Host'].replace('.', '-').replace(':', '-')
        response.set_cookie(jupyter_notebook_cookie, '', expires=0, path='/jupyter/')
        response.headers['X-Jupyter-Token'] = 'badtoken'

        # Keep for now in case this is useful later.
        #if request.headers.get('Content-Type') == 'application/json':
        #    #response = Response(json.dumps({'statusCode': 401}), status=401, mimetype='application/json')
        #    response = make_response(jsonify({'code': 401, 'message': 'Login required.'}), 401)
        #    return response

        return response

@app.route('/login', methods=['GET', 'POST'])
def login():
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
        
            # Move forward to validate session and request Elasticsearch API key.
            #
            # TODO: Make the actual call to Elasticsearch API to get a new key.
            #
            # TODO: Don't forget to save the expiration time of the key to check it later
            # and refresh the API key as needed.
            #
            session['kibana_auth'] = 'd3VHN2dYSUI5eHhaR3Fmdk1tVUs6b3hnVUJCTDFRMWVoaDhDNS1uTGlIQQ=='

            # TODO: Get credentials for all tools the user has access to to keep them in the
            # session cookie for easier access.
            # TODO: Use the username from a DB call to put in here instead of a static user.
            session['jenkins_user'] = 'davidlag'

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

@app.route('/logout', methods=['GET'])
def logout():
    session['logged_in'] = False

    app.logger.info('User %s logged out successfully',
        session.get('username'))

    # Keep as reference for now.
    #if request.args.get('next'):
    #    response = make_response(redirect(url_for('login', _external=True)))
    #    return response

    # Redirect to home page with links to tools.
    response = make_response(redirect(HOME_PAGE, code=302))
    return response

# TODO: Build this function to do the actual DB call.
def authenticate(username, password):
    '''
    Authenticate the user against the local DB using the provided
    credentials.
    '''

    # TODO: Verify user credentials against LDAP here.

    # TODO: Safeguard credentials in env files.
    # TODO: Deal with errors in case the database is down or not accessible, etc.
    connection = pg8000.connect('testuser', password='testpass', database='testdb')

    # Assume credentials were verified another way so only verify if the user
    # exists in the database at this point.
    if len(connection.run('SELECT * FROM users WHERE username=:user', user=username)) == 1:
        return True
    else:
        return False

def get_redirect_url(request):
    # Web Authenticator.
    if request.args.get('url'):
        return request.args.get('url')
    # Kibana.
    elif request.args.get('next'):
        return request.args.get('next')
    # Jenkins.
    elif request.args.get('from'):
        return request.args.get('from')

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 6000.
    port = int(os.environ.get('PORT', 6000))
    app.run(host='0.0.0.0', port=port, debug=True)
