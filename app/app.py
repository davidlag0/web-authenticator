import os
from flask import Flask, abort, request, make_response, Response
from flask import render_template, redirect, url_for, session
from pprint import pprint

app = Flask(__name__)

app.secret_key = b'_8#y4L"F4Q5z\m\bgh]/'

@app.route('/')
def index():
    response = Response('', 401, {'WWW-Authenticate':'Basic realm="Login Required"'})
    response.headers['X-Original-URI'] = request.headers.get('X-Original-URI')

    # As this is the entrypoint of web-auth, save the original URI to use
    # it later to redirect the browser after the auth has passed. Only set
    # it if empty to avoid overwriting it with subsequent calls to this function.
    if session.get('logged_in'):
        response = Response('', status=200, mimetype='application/json')

        # TODO: Use the username from a DB call to put in here instead of a static user.
        response.headers['X-Jenkins-User'] = 'davidlag'
        return response

    else:
        # As this is evaluated first, we need to return a 401 so that NGINX redirects
        # to the login page.
        return response

    # If we ever get here, deny access.
    return response

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Credentials are validated against the DB and if they are valid, the username
    # only is saved. We would also validate credentials against LDAP or such another
    # mean here as well.
    if request.method == 'POST':
        # TODO: Don't use static credentials but make an actual call to a DB.
        if (request.form['username'] == 'blop') and (request.form['password'] == 'blop'):
            response = make_response(redirect(request.args.get('url')))

            session['username'] = request.form['username']
            session['logged_in'] = True
        
            # Move forward to validate session and request Elasticsearch API key.
            # TODO: Make the actual call to Elasticsearch API to get a new key.
            session['kibana_auth'] = 'd3VHN2dYSUI5eHhaR3Fmdk1tVUs6b3hnVUJCTDFRMWVoaDhDNS1uTGlIQQ=='
            response.set_cookie('kibana_auth', 'd3VHN2dYSUI5eHhaR3Fmdk1tVUs6b3hnVUJCTDFRMWVoaDhDNS1uTGlIQQ==')

            return response

        else:
            # TODO: Better handling of this to give the user an error message.
            return 'Wrong password!'
    
    # Login page is shown when the user does not POST any credentials.
    return render_template('login.html', url=request.args.get('url'))

@app.route('/logout', methods=['GET'])
def logout():
    session['logged_in'] = False
    response = make_response(redirect(url_for('login', _external=True)))
    response.set_cookie('kibana_auth', expires=0)
    return response

# TODO: Build this function to do the actual DB call.
def authenticate(username, password):
    '''
    Authenticate the user against the local DB using the provided
    credentials.
    '''
    return 'Credentials:' + username + ':' + password

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 6000.
    port = int(os.environ.get('PORT', 6000))
    app.run(host='0.0.0.0', port=port, debug=True)
