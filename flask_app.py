import json
from os import environ

import azure.functions as func
from flask import Flask, make_response, request
from pyngrok import ngrok

from HTTPWebexBot import main as main_http_func
from TimerCreateWebhooks import main as update_webhooks

app = Flask(__name__)
flask_port = 5000


@app.route('/webexbot', methods=['POST'])
def proxy_call():

    r = func.HttpRequest(
        method=request.method,
        url=request.url,
        headers=request.headers,
        body=request.data
    )

    resp = main_http_func(r)

    return make_response(resp.get_body(), resp.status_code)


if __name__ == '__main__':

    # try the local settings file
    try:
        with open('local.settings.json') as json_file:
            json_data = json.load(json_file)

            environ.update(json_data['Values'])
    except FileNotFoundError:
        pass

    environ['RUNNING_AS_FLASK_APP'] = 'yes'

    class MockTimer():
        def __init__(self):
            self.past_due = False

    # create an ngrok tunnel
    http_tunnel = ngrok.connect(addr=flask_port, proto='http')

    # the tunnel is going to be created showing an http address
    # but ngrok will actually create both http and https so we'll
    # want to use the secured tunnel
    webhook_url = http_tunnel.public_url.replace('http://', 'https://')

    # save the url to an environment variable to use
    environ['NGROK_FLASK_PUBLIC_URL'] = webhook_url

    # update the webhooks
    update_webhooks(MockTimer())

    app.run(host='0.0.0.0', port=flask_port)
