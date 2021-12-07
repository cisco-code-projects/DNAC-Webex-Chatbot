if __name__ == '__main__' and (__package__ == '' or __package__ is None):
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
    from SharedCode.DNACModule import DNAC
    from SharedCode.WebexTeamsModule import WebexTeams
except ImportError:
    from ..SharedCode.DNACModule import DNAC
    from ..SharedCode.WebexTeamsModule import WebexTeams


def main(req: func.HttpRequest) -> func.HttpResponse:

    logger = logging.getLogger()
    log_level = logging.getLevelName(environ['logging_level'])
    logger.setLevel(log_level)

    try:

        def check_domain(email):

            # if the message is one a bot posted, ignore it
            if '@webex.bot' in email:
                logger.info(f'Message was from a bot: {email}')
                return False

            if environ.get('WEBEX_ALLOWED_DOMAINS') is None:
                # allowed domain list is empty, all allowed
                return True

            # get the domain list
            allowed_domains = environ.get('WEBEX_ALLOWED_DOMAINS').split(',')

            for domain in allowed_domains:
                # strip any whitespace in case it was accidentally added
                domain = domain.strip()

                # add the @ if it isn't there already
                if not domain.startswith('@'):
                    domain = '@' + domain

                # check if the domain is in the email
                if domain in email:
                    return True

            # if all domains were checked and we didn't return True yet
            # then this domain is not allowed
            return False

        data = req.get_json()

        # logger.info(f'Data: {data}')
        person_email = data['data']['personEmail']

        if not check_domain(person_email):
            logger.warning(f'User with email {person_email} not allowed to chat with bot')
            return func.HttpResponse(f'User with email {person_email} not allowed to chat with bot', mimetype='text/html')

        if data['resource'] == 'messages' and data['event'] == 'created':

            teams_api = WebexTeams(environ['WEBEX_TEAMS_ACCESS_TOKEN'])

            # send the default card
            teams_api.send_default_card(person_email=person_email)

            return func.HttpResponse('Done', mimetype='text/html')

        elif data['resource'] == 'attachmentActions' and data['event'] == 'created':

            teams_api = WebexTeams(environ['WEBEX_TEAMS_ACCESS_TOKEN'])

            # get the message contents
            action = teams_api.api.attachment_actions.get(data['data']['id'])

            if action.type != 'submit':
                logger.warning('Action not submit')
                return func.HttpResponse('Action not submit', mimetype='text/html')

            # get the person details
            person = teams_api.api.people.get(action.personId)
            person_email = person.emails[0]

            if '@cisco.com' not in person_email:
                logger.warning(f'Message was not from a Cisco person: {person_email}')
                return func.HttpResponse(f'Message was not from a Cisco person: {person_email}', mimetype='text/html')

            # create the dnac api object
            dnac_api = DNAC()

            # check for the actions
            if action.inputs.get('next_action') == 'list_devices':

                device_list = dnac_api.get_devices_for_card()

                teams_api.send_device_list_card(device_list=device_list, person_email=person_email)

                return func.HttpResponse('Done', mimetype='text/html')

            elif action.inputs.get('next_action') == 'get_device_details':

                details = dnac_api.get_device_details_for_card(d_id=action.inputs.get('device_choice'))

                teams_api.send_device_details_card(details=details, person_email=person_email)

                return func.HttpResponse('Done', mimetype='text/html')

            elif action.inputs.get('next_action') == 'get_device_config':

                config = dnac_api.get_device_config_for_card(d_id=action.inputs.get('device_choice'))

                teams_api.send_device_config(config=config, person_email=person_email)

                return func.HttpResponse('Done', mimetype='text/html')

            elif action.inputs.get('next_action') == 'run_command':

                d_id = action.json_data['inputs']['device_choice']
                command = action.json_data['inputs']['text_command']

                result = dnac_api.run_command_on_device(d_id, command)

                if result:
                    teams_api.send_message(markdown=result, person_email=person_email)
                else:
                    teams_api.send_message(markdown='Command unsuccessful', person_email=person_email)

                # resend the details card
                details = dnac_api.get_device_details_for_card(d_id=action.inputs.get('device_choice'))
                teams_api.send_device_command_card(details=details, person_email=person_email)

                return func.HttpResponse('Done', mimetype='text/html')

            elif action.inputs.get('next_action') == 'get_issues':

                max_issues = action.inputs.get('max_issues')
                priority = action.inputs.get('issue_priority')

                issues = dnac_api.get_issues_for_card(priority=priority)[:max_issues - 1]

                teams_api.send_issue_list_card(
                    text=f'{priority.upper()} issues:', issue_list=issues, person_email=person_email)

                return func.HttpResponse('Done', mimetype='text/html')

            return func.HttpResponse('Done', mimetype='text/html')

    except Exception as e:
        logger.critical(f'Exception: {e}')
        logger.critical(traceback.print_exc())

        raise e


# config to run as a local script vs. function
if __name__ == '__main__':
    with open('local.settings.json') as json_file:
        json_data = json.load(json_file)

        environ.update(json_data['Values'])

    try:
        # get the ngrok tunnel
        r = requests.get('http://localhost:4040/api/tunnels')

        tunnels = r.json()

        ngrok_url = tunnels['tunnels'][0]['public_url']

    except Exception:
        ngrok_url = None

    if ngrok_url:
        print(f'Ngrok tunnel found, updating webhooks with: {ngrok_url}')
        __t = WebexTeams(environ['WEBEX_TEAMS_ACCESS_TOKEN'])
        __t.create_update_webhooks(ngrok_url)

    print()
