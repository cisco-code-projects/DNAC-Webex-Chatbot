if __name__ == '__main__' and (__package__ == '' or __package__ is None):
    # this is necessary to get SharedCode importing to work
    # when running this as a local script for testing/dev
    from os.path import dirname
    from sys import path as syspath
    syspath.append(dirname(syspath[0]))

import json
import logging
import traceback
from os import environ

import azure.functions as func
import requests

try:
    from SharedCode.WebexTeamsModule import WebexTeams
except ImportError:
    from ..SharedCode.WebexTeamsModule import WebexTeams


def main(mytimer: func.TimerRequest) -> None:

    logger = logging.getLogger()
    log_level = logging.getLevelName(environ['logging_level'])
    logger.setLevel(log_level)

    [logging.getLogger(name).setLevel(
        logging.getLevelName(environ['other_modules_logging_level']))
        for name in logging.root.manager.loggerDict]

    try:

        teams_api = WebexTeams(access_token=environ['WEBEX_TEAMS_ACCESS_TOKEN'])

        if __name__ == '__main__' or environ.get('RUNNING_AS_FLASK_APP'):

            logger.info('Running as local script, looking for ngrok tunnel')

            try:

                # if we've set the environ variable for the ngrok tunnel, use that
                if type(environ.get('NGROK_FLASK_PUBLIC_URL')) is str:
                    ngrok_url = environ.get('NGROK_FLASK_PUBLIC_URL') + '/webexbot'

                else:
                    # otherwise, find the first tunnel that's running
                    r = requests.get('http://localhost:4040/api/tunnels')

                    tunnels = r.json()

                    ngrok_url = tunnels['tunnels'][0]['public_url'] + '/webexbot'

            except Exception:
                ngrok_url = None
                logger.warning('No ngrok tunnels found!')

            if ngrok_url:
                logger.info(f'Ngrok tunnel found, updating webhooks with: {ngrok_url}')
                teams_api.create_update_webhooks(ngrok_url)

        else:
            teams_api.create_update_webhooks(environ.get('WEBEX_TEAMS_WEBHOOK_URL'))

        logger.info('Done')

    except Exception as e:
        logger.critical(f'Exception: {e}')
        logger.critical(traceback.print_exc())
        raise e


# config to run as a local script vs. function
if __name__ == '__main__':
    with open('local.settings.json') as json_file:
        json_data = json.load(json_file)

        environ.update(json_data['Values'])

    # for some reason we don't get any logging unless a message is logged outside the function first
    # when running locally
    logging.debug('Kickstart Message')

    # execute with a dummy timer
    main('LocalRun')
