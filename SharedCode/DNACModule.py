import json
import logging
from json import JSONDecodeError
from os import environ
from time import sleep

from dnacentersdk import DNACenterAPI
from dnacentersdk.exceptions import ApiError

logger = logging.getLogger()


class DNAC():

    def __init__(self):

        verify = environ['DNA_CENTER_VERIFY'].lower() == 'true'

        self.api = DNACenterAPI(
            base_url=environ['DNA_CENTER_BASE_URL'],
            username=environ['DNA_CENTER_USERNAME'],
            password=environ['DNA_CENTER_PASSWORD'],
            verify=verify
        )

    def get_devices_for_card(self):

        device_list = self.api.devices.get_device_list()

        return [{'hostname': x['hostname'], 'id': x['id']} for x in device_list['response'] if x['hostname']]

    def get_device_details_for_card(self, d_id):

        d = self.api.devices.get_device_by_id(d_id)

        return d['response']

    def get_device_config_for_card(self, d_id):

        try:

            d = self.api.devices.get_device_config_by_id(d_id)

            return d['response']

        except ApiError as e:

            if e.status_code == 501:
                logger.warning(f'ApiError getting config: {e}')
                return None

    def run_command_on_device(self, d_id, command):

        r = self.api.command_runner.run_read_only_commands_on_devices(
            commands=[command], deviceUuids=[d_id], description='Run from Webex Bot'
        )

        for _ in range(60):

            progress = self.api.task.get_task_by_id(r['response']['taskId'])

            try:
                f_id = json.loads(progress['response']['progress'])['fileId']
                break
            except JSONDecodeError:
                logger.info(f"Progress: {progress['response']['progress']}")
                sleep(1)

        file_resp = self.api.file.download_a_file_by_fileid(f_id)

        data = json.loads(file_resp.data)[0]

        if data['commandResponses']['SUCCESS']:
            for output in data['commandResponses']['SUCCESS'].values():
                return "```" + output

        # if the command was not successful
        return None

    def get_user_enrichment_for_card(self, username):

        return self.api.users.get_user_enrichment_details({'entity_type': 'network_user_id', 'entity_value': username})

    def get_issues_for_card(self, priority=None):
        """
            priority (str): p1, p2, p3, p4
        """

        d = self.api.issues.issues(priority=priority, issue_status='active')

        # sort the issues by most recent first
        return sorted(
            d['response'], key=lambda x: x['last_occurence_time'], reverse=True
        )
