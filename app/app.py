import os
from flask import Flask, abort, request, make_response, Response
from pprint import pprint

app = Flask(__name__)

@app.route('/')
def index():
    resp = make_response("hello")

    print('Headers:', request.headers)
    #abort(401)
    #return 'Hello Flask from alpine-linux!'
    #return Response(headers={'Authorized':'ApiKey Nk5XQWZISUI5eHhaR3FmdlJHa0E6UkszVnZYbGxUUjY3bEJyZmVkWGdXdw=='})
    print('cookie:', request.cookies.get('kibana_auth'))

    if request.cookies.get('kibana_auth') == None:
        # Here we need to check the DB for a key and if not, request it from Elasticsearch.
        # Then, we save the key in a cookie on the user's side so that it can be reused later.

        # Set cookie
        resp.set_cookie('kibana_auth', 'ZWxhc3RpYzpjaGFuZ2VtZQ==')
        pprint(vars(resp))
        return resp
    else:
        print('found cookie:', request.cookies.get('kibana_auth'))
        #return resp
        return Response(headers={'Authorization': 'Basic ZWxhc3RpYzpjaGFuZ2VtZQ=='})


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 6000.
    port = int(os.environ.get('PORT', 6000))
    app.run(host='0.0.0.0', port=port, debug=True)
