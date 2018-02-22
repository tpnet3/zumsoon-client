import json
from flask import Flask, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth


CLIENT_ID = ""
CLIENT_SECRET = ""


app = Flask(__name__)
app.debug = True
app.secret_key = 'secret'
oauth = OAuth(app)

remote = oauth.remote_app(
    'remote',
    consumer_key=CLIENT_ID,
    consumer_secret=CLIENT_SECRET,
    request_token_params={'scope': 'email address'},
    base_url='http://www.zumsoon.com/api/v1.0/',
    request_token_url=None,
    access_token_url='http://www.zumsoon.com/oauth/token',
    authorize_url='http://www.zumsoon.com/oauth/authorize'
)


@app.route('/')
def home():
    return jsonify(Hello='World')


#############  OAUTH  #######################
@app.route('/oauth')
def oauth():
    next_url = request.args.get('next') or request.referrer or None
    return remote.authorize(
        callback=url_for('authorized', next=next_url, _external=True)
    )


# Redirect uris
# 'http://localhost:8000/authorized http://127.0.0.1:8000/authorized http://127.0.1:8000/authorized http://127.1:8000/authorized'
# 'http://www.zumsoon.com/authorized'
# The first uri is the base uri.
@app.route('/authorized')
def authorized():
    try:
        resp = remote.authorized_response()
    except:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['remote_oauth'] = (resp['access_token'], '')
    return jsonify(oauth_token=session['remote_oauth'])


@remote.tokengetter
def get_oauth_token():
    return session.get('remote_oauth')


@app.route('/token')
def token():
    resp = session.get('remote_oauth')
    return jsonify(oauth_token=resp[0])


#############  USER API  #######################

@app.route('/api/v1.0/user/me')
def user_me():
    resp = remote.get('user/me')
    return resp.raw_data


@app.route('/api/v1.0/user/client')
def user_client_api():
    resp = remote.get('user/client')
    return resp.raw_data


############# ACCOUNT API #########################
@app.route('/api/v1.0/account', methods=['GET', 'POST', 'PUT', 'DELETE'])
def account():
    if request.method == 'GET':
        resp = remote.get('account')
        return resp.raw_data
    elif request.method == 'POST':
        pass
    else:
        pass


@app.route('/api/v1.0/account/ledger', methods=['GET', 'POST', 'PUT', 'DELETE'])
def account_ledger():
    resp = remote.get('account/ledger')
    return resp.raw_data


############# BROKER API #########################

@app.route('/api/v1.0/broker')
def broker():
    ret = remote.get('broker')
    return ret.raw_data


@app.route('/api/v1.0/broker/current-quote/<commodity>')
def broker_current_quote(commodity):
    ret = remote.get('broker/current-quote/{}'.format(commodity))
    return ret.raw_data


@app.route('/api/v1.0/broker/lob/<commodity>')
def broker_lob(commodity):
    ret = remote.get('broker/lob/{}'.format(commodity))
    return ret.raw_data


@app.route('/api/v1.0/broker/order')
def broker_order():
    """
    order = {'commodity': string, 'quote': integer, 'qty': integer}
            (qty<0 -> ask, qty>0 -> bid)
    Only normal order is allowed, not market order!
    """
    order = {'commodity': 11, 'quote': 1500000, 'qty': -3}
    order = json.dumps(order)
    ret = remote.post('broker/order', data={'order': order})
    return ret.raw_data


@app.route('/api/v1.0/broker/cancel')
def broker_cancel():
    cancel = {'commodity': 11, 'order_id': '2018-02-13:2'}
    cancel = json.dumps(cancel)
    ret = remote.post('broker/cancel', data={'cancel': cancel})
    return ret.raw_data


@app.route('/api/v1.0/broker/chart/<commodity>')
def broker_chart(commodity):
    ret = remote.get('chat/{}'.format(commodity))
    return ret.raw_data


############# RISK MANAGER API #########################
@app.route('/api/v1.0/risk-manager/report/<report_name>')
def risk_manager_report(report_name):
    ret = remote.get('risk-manager/report/{}'.format(report_name))
    return ret.raw_data


############# TEST API #########################
@app.route('/api/v1.0/test/address')
def address():
    ret = remote.get('address/hangzhou')
    if ret.status not in (200, 201):
        return ret.raw_data, ret.status
    return ret.raw_data


@app.route('/api/v1.0/test/method/<name>')
def method(name):
    func = getattr(remote, name)
    ret = func('method')
    return ret.raw_data


@app.route('/api/v1.0/test/hello')
def hello():
    resp = remote.get('hello')
    return jsonify(resp.data)


if __name__ == '__main__':
    import os
    os.environ['DEBUG'] = 'true'
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
    app.run(host='0.0.0.0', port=8000)
