import logging
from time import sleep

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from webexteamssdk import WebexTeamsAPI

logger = logging.getLogger()


class WebexTeams():

    def __init__(self, access_token):

        self.api = WebexTeamsAPI(access_token=access_token)

    def send_message(self, markdown, person_email=None, room_id=None, attachments=None):
        """
            Sends a message to the room
            Arguments:
                markdown (str):  Message text with optional markdown formatting
                room_name (str):  Room to send to
                attachments (card):  Adaptive card
                (https://dev-preview.webex.com/formatting-messages.html)
            Returns:
                Nothing
        """

        if not person_email and not room_id:
            logger.warning('No person_email or room_id supplied, not sending message')
            return

        elif person_email and room_id:
            logger.warning('Both person_email AND room_id supplied, not sending message')
            return

        try:

            self.api.messages.create(
                roomId=room_id,
                toPersonEmail=person_email,
                markdown=markdown,
                attachments=attachments
            )

        except Exception as e:
            logger.warning(
                f'Exception occurred while trying to send message: {e}')

    def create_update_webhooks(self, target_url):
        """
            Create or update the webhooks with the supplied URL
        """
        existing_webhooks = self.api.webhooks.list()

        # delete existing webhooks
        for wh in existing_webhooks.arguments['self'].list():
            self.api.webhooks.delete(wh.id)

        # message create webhook
        webhook_name = 'DNAC Bot Message Created'
        self.api.webhooks.create(
            name=webhook_name,
            targetUrl=target_url,
            resource='messages',
            event='created'
        )

        # attachment submit webhook
        webhook_name = 'DNAC Bot Attachment Created'
        self.api.webhooks.create(
            name=webhook_name,
            targetUrl=target_url,
            resource='attachmentActions',
            event='created'
        )

    def send_default_admin_card(self, text=None, person_email=None, room_id=None):

        if text is None:
            text = 'What do you want to do?'

        card = {
            'contentType': 'application/vnd.microsoft.card.adaptive',
            'content': {
                '$schema': 'http://adaptivecards.io/schemas/adaptive-card.json',
                'type': 'AdaptiveCard',
                'version': '1.2',
                'body': [
                    {
                        'type': 'TextBlock',
                        'text': text,
                        'size': 'Medium',
                        'weight': 'Bolder',
                        'wrap': True
                    }
                ],
                'actions': [
                    {
                        'type': 'Action.Submit',
                        'title': 'P1 Issues',
                        'data': {
                            'next_action': 'get_issues',
                            'max_issues': 10,
                            'issue_priority': 'p1'
                        }
                    },
                    {
                        'type': 'Action.Submit',
                        'title': 'List Devices',
                        'data': {
                            'next_action': 'list_devices'
                        }
                    }
                ]
            }
        }

        self.send_message('Landing Card', person_email=person_email, room_id=room_id, attachments=[card])

    def send_device_list_card(self, text=None, device_list=[], person_email=None, room_id=None):

        if text is None:
            text = 'Choose a device:'

        choice_list = [
            {
                'title': x['hostname'],
                'value': x['id']
            } for x in device_list
        ]

        card = {
            'contentType': 'application/vnd.microsoft.card.adaptive',
            'content': {
                '$schema': 'http://adaptivecards.io/schemas/adaptive-card.json',
                'type': 'AdaptiveCard',
                'version': '1.2',
                'body': [
                    {
                        'type': 'TextBlock',
                        'text': text,
                        'size': 'Medium',
                        'weight': 'Bolder',
                        'wrap': True
                    },
                    {
                        'type': 'Input.ChoiceSet',
                        'id': 'device_choice',
                        'style': 'compact',
                        'wrap': True,
                        'isMultiSelect': False,
                        'choices': choice_list
                    }
                ],
                'actions': [
                    {
                        'type': 'Action.Submit',
                        'title': 'Get Details',
                        'data': {
                            'next_action': 'get_device_details'
                        }
                    },
                    {
                        'type': 'Action.Submit',
                        'title': 'Get Config',
                        'data': {
                            'next_action': 'get_device_config'
                        }
                    },
                    {
                        'type': 'Action.Submit',
                        'title': 'Home',
                        'data': {
                            'next_action': 'go_home'
                        }
                    }
                ]
            }
        }

        self.send_message('Devices Card', person_email=person_email, room_id=room_id, attachments=[card])

    def send_device_details_card(self, text=None, details={}, person_email=None, room_id=None):

        if text is None:
            text = details['hostname']

        card = {
            'contentType': 'application/vnd.microsoft.card.adaptive',
            'content': {
                '$schema': 'http://adaptivecards.io/schemas/adaptive-card.json',
                'type': 'AdaptiveCard',
                'version': '1.2',
                'body': [
                    {
                        'type': 'TextBlock',
                        'text': text,
                        'size': 'Medium',
                        'weight': 'Bolder',
                        'wrap': True
                    },
                    {
                        'type': 'ColumnSet',
                        'columns': [
                            {
                                'type': 'Column',
                                'items': [
                                    {
                                        'type': 'TextBlock',
                                        'text': 'Platform:'
                                    },
                                    {
                                        'type': 'TextBlock',
                                        'text': 'Software Version:'
                                    },
                                    {
                                        'type': 'TextBlock',
                                        'text': 'Serial Number:'
                                    },
                                    {
                                        'type': 'TextBlock',
                                        'text': 'Status:'
                                    },
                                    {
                                        'type': 'TextBlock',
                                        'text': 'Uptime:'
                                    }
                                ]
                            },
                            {
                                'type': 'Column',
                                'items': [
                                    {
                                        'type': 'TextBlock',
                                        'text': details['platformId']
                                    },
                                    {
                                        'type': 'TextBlock',
                                        'text': details['softwareVersion']
                                    },
                                    {
                                        'type': 'TextBlock',
                                        'text': details['serialNumber']
                                    },
                                    {
                                        'type': 'TextBlock',
                                        'text': details['reachabilityStatus']
                                    },
                                    {
                                        'type': 'TextBlock',
                                        'text': details['upTime']
                                    }
                                ]
                            }
                        ]
                    }
                ],
                'actions': [
                    {
                        'type': 'Action.Submit',
                        'title': 'Get Config',
                        'data': {
                            'next_action': 'get_device_config',
                            'device_choice': details['id']
                        }
                    },
                    {
                        'type': 'Action.ShowCard',
                        'title': 'Run Command',
                        'card': {
                            'type': 'AdaptiveCard',
                            'body': [
                                {
                                    'type': 'Input.Text',
                                    'id': 'text_command',
                                    'placeholder': 'Enter command',
                                    'inlineAction': {
                                        'type': 'Action.Submit',
                                        'title': 'Enter',
                                        'data': {
                                            'next_action': 'run_command',
                                            'device_choice': details['id']
                                        }
                                    }
                                }
                            ],
                            'actions': []
                        }
                    },
                    {
                        'type': 'Action.Submit',
                        'title': 'Home',
                        'data': {
                            'next_action': 'go_home'
                        }
                    }

                ]
            }
        }

        self.send_message('Run Command Card', person_email=person_email, room_id=room_id, attachments=[card])

    def send_device_command_card(self, details, person_email=None, room_id=None):

        card = {
            'contentType': 'application/vnd.microsoft.card.adaptive',
            'content': {
                '$schema': 'http://adaptivecards.io/schemas/adaptive-card.json',
                'type': 'AdaptiveCard',
                'version': '1.2',
                'body': [
                    {
                        'type': 'TextBlock',
                        'text': details['hostname'],
                        'size': 'Medium',
                        'weight': 'Bolder',
                        'wrap': True
                    },
                    {
                        'type': 'Input.Text',
                        'id': 'text_command',
                        'placeholder': 'Enter command',
                        'inlineAction': {
                            'type': 'Action.Submit',
                            'title': 'Enter',
                            'data': {
                                'next_action': 'run_command',
                                'device_choice': details['id']
                            }
                        }
                    }
                ],
                'actions': [
                    {
                        'type': 'Action.Submit',
                        'title': 'Home',
                        'data': {
                            'next_action': 'go_home'
                        }
                    }
                ]
            }
        }

        self.send_message('Device Details Card', person_email=person_email, room_id=room_id, attachments=[card])

    def send_device_config(self, config, person_email=None, room_id=None):

        if config is None:
            self.send_message(
                'No configuration available for device (might be an AP)', person_email=person_email, room_id=room_id)
            return

        try:

            if person_email:

                m = MultipartEncoder(
                    {
                        'toPersonEmail': person_email,
                        'markdown': 'config',
                        'files': ('config.txt', config, 'text/plain')
                    }
                )
            elif room_id:

                m = MultipartEncoder(
                    {
                        'roomId': room_id,
                        'markdown': 'config',
                        'files': ('config.txt', config, 'text/plain')
                    }
                )
            else:
                return

            for _ in range(5):
                r = requests.post(
                    f'{self.api.base_url}messages',
                    data=m,
                    headers={
                        'Authorization': f'Bearer {self.api.access_token}',
                        'Content-Type': m.content_type}
                )

                if r.status_code == 200:
                    break

                sleep(3)

        except Exception as e:
            logger.warning(
                f'Exception occurred while trying to send message: {e}')

    def send_issue_list_card(self, text=None, issue_list=[], person_email=None, room_id=None):

        if text is None:
            text = 'Issues:'

        body = [
            {
                'type': 'TextBlock',
                'text': f"- {x['name']}",
                'wrap': True
            } for x in issue_list
        ]

        body.insert(0, {
                'type': 'TextBlock',
                'text': text,
                'size': 'Medium',
                'weight': 'Bolder',
                'wrap': True
            }
        )

        card = {
            'contentType': 'application/vnd.microsoft.card.adaptive',
            'content': {
                '$schema': 'http://adaptivecards.io/schemas/adaptive-card.json',
                'type': 'AdaptiveCard',
                'version': '1.2',
                'body': body,
                'actions': [
                    {
                        'type': 'Action.Submit',
                        'title': 'Home',
                        'data': {
                            'next_action': 'go_home'
                        }
                    }

                ]
            }
        }

        self.send_message('Issues Card', person_email=person_email, room_id=room_id, attachments=[card])

    def send_default_user_card(self, text=None, person_email=None, room_id=None):

        if text is None:
            text = 'What do you want to do?'

        card = {
            'contentType': 'application/vnd.microsoft.card.adaptive',
            'content': {
                '$schema': 'http://adaptivecards.io/schemas/adaptive-card.json',
                'type': 'AdaptiveCard',
                'version': '1.2',
                'body': [
                    {
                        'type': 'TextBlock',
                        'text': text,
                        'size': 'Medium',
                        'weight': 'Bolder',
                        'wrap': True
                    }
                ],
                'actions': [
                    {
                        'type': 'Action.Submit',
                        'title': 'Check My Network Health',
                        'data': {
                            'next_action': 'check_my_user_health'
                        }
                    },
                    {
                        'type': 'Action.ShowCard',
                        'title': "Check Another User's Network Health",
                        'card': {
                            'type': 'AdaptiveCard',
                            'body': [
                                {
                                    'type': 'Input.Text',
                                    'id': 'username_input',
                                    'placeholder': 'Enter username',
                                    'inlineAction': {
                                        'type': 'Action.Submit',
                                        'title': 'Enter',
                                        'data': {
                                            'next_action': 'user_enrichment'
                                        }
                                    }
                                }
                            ],
                            'actions': []
                        }
                    }
                ]
            }
        }

        self.send_message('Landing Card', person_email=person_email, room_id=room_id, attachments=[card])

    def send_user_details_card(self, details={}, person_email=None, room_id=None):

        body = [
            {
                'type': 'TextBlock',
                'text': f'User Devices for "{person_email}"',
                'size': 'Large',
                'weight': 'Bolder',
                'wrap': True
            }
        ]

        i = 0
        for s in ['connected', 'connecting', 'disconnected']:

            for d in details:
                ud = d['userDetails']
                if ud['connectionStatus'].lower() == s:

                    hs = {h['healthType'].lower(): h['score'] for h in ud['healthScore']}

                    i += 1
                    body.append(
                        {
                            'type': 'TextBlock',
                            'text': f"------\n[**Device #{i:,.0f}** -- Open Helpdesk Ticket](http://myhelpdesklink.local/open-dnac-ticket?user={person_email}&device_id={ud['id']})",  # noqa: E501
                            'size': 'Medium',
                            'weight': 'Bolder'
                        }
                    )

                    body.append(
                        {
                            'type': 'FactSet',
                            'facts': [
                                {
                                    'title': 'Hostname:',
                                    'value': ud['hostName']
                                },
                                {
                                    'title': 'Conn Type:',
                                    'value': ud['hostType'].lower()
                                },
                                {
                                    'title': 'Status:',
                                    'value': ud['connectionStatus'].lower()
                                },
                                {
                                    'title': 'OS:',
                                    'value': ud['hostOs']
                                },
                                {
                                    'title': 'Overall Health:',
                                    'value': str(hs['overall'])
                                },
                                {
                                    'title': 'Onboarding Health:',
                                    'value': str(hs['onboarded'])
                                },
                                {
                                    'title': 'Connected Health:',
                                    'value': str(hs['connected'])
                                },
                                {
                                    'title': 'Issues:',
                                    'value': str(ud['issueCount'])
                                }
                            ]
                        }
                    )

        card = {
            'contentType': 'application/vnd.microsoft.card.adaptive',
            'content': {
                '$schema': 'http://adaptivecards.io/schemas/adaptive-card.json',
                'type': 'AdaptiveCard',
                'version': '1.2',
                'body': body,
                'actions': []
            }
        }

        self.send_message('User Details', person_email=person_email, room_id=room_id, attachments=[card])
