# -*- coding: utf-8 -*-
# pylint:disable=line-too-long
""" Lambda to handle dynamic security hub slack messages """
import ast
import base64
import json
import logging
import os
import sys

import boto3
from slacker import Slacker

from yawps.exceptions import NoSlackChannelException

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
LOGGER.addHandler(handler)


org_client = boto3.client('organizations')


def get_account_tag(
    account_id: str,
    tag_key: str,
    fallback_value: str = ""
) -> str:
    """ Call ListTagsForResource on an account and return the specified
        value for a tag.

    Args:
        account_id (str): the account ID to get tags for
        tag_key (str): the key to look for in the tags searched
    """
    value = ""
    try:
        value = [
            tag for tag in org_client.list_tags_for_resource(
                ResourceId=account_id
            )['Tags'] if tag['Key'] == tag_key][0]['Value']
    except IndexError:
        value = fallback_value
    return value


def parse(finding, account_name):
    """ Parse the securityhub finding for slacker

    Args:
      finding (Dict): security hub finding
      account_name (str): human readable name for the account
    """
    LOGGER.info('Parsing security hub finding')

    attachments = []

    fields = [
        {
            "title": 'Severity',
            "value": finding['FindingProviderFields']['Severity']['Label'],
            "short": True
        },
        {
            "title": 'Security Hub Findings',
            "value": finding['Types'][0],
            "short": False
        },
        {
            "title": f"{account_name} ({finding['AwsAccountId']}) - {finding['Region']}",  # noqa
            "value": finding['Description'],
            "short": False
        },
        {
            "title": "Affected resource(s)",
            "value": ','.join([resource['Id'] for resource in finding['Resources']]),  # noqa
            "short": False
        },

    ]
    title = None
    title_link = None
    if finding.get('Remediation'):
        title = finding['Remediation']['Recommendation']['Text']
        title_link = finding['Remediation']['Recommendation']['Url']

    attachments = [{
        "mrkdwn_in": ["text"],
        'fallback': finding['Description'],
        'message': '',
        'color': 'bad',
        'title': title,
        'title_link': title_link,
        "fields": fields
    }]
    return {
        'message': f"SecurityHub Finding `{finding['Title']}`",
        'attachments': attachments
    }


def lambda_handler(event, context):  # pylint: disable=unused-argument
    """ Main method handler for lambda

    Arg: event (dict)
    Arg: context (dict)
    """
    ssm_client = boto3.client('ssm')
    fallback_channel = os.environ.get('SLACK_FALLBACK_CHANNEL')
    slack_token = os.environ.get(
        'SLACK_TOKEN',
        ssm_client.get_parameter(
            Name=os.environ.get(
                'SLACK_TOKEN_SSM_PATH',
                '/ops/slack_token'
            ),
            WithDecryption=True,
        )['Parameter']['Value']
    )
    slack = Slacker(slack_token)

    LOGGER.setLevel(logging.getLevelName(
        os.environ.get('LOGGING_LEVEL', 'INFO')
    ))

    LOGGER.info(
        '[Debug] Base64 encoded payload: %s',
        base64.b64encode(json.dumps(event).encode('ascii'))
    )

    finding = event['detail']['findings'][0]

    slack_channel = get_account_tag(
        finding['AwsAccountId'],
        'slack_channel',
        fallback_channel
    )
    if not slack_channel:
        raise NoSlackChannelException('No slack channel found. Either add a slack_channel tag to all accounts or set a SLACK_FALLBACK_CHANNEL environment variable')  # noqa

    account_name = get_account_tag(
        finding['AwsAccountId'],
        'account_name',
        event['account']
    )
    parsed_message = parse(finding, account_name)
    _severity = finding['FindingProviderFields']['Severity']
    severity = int(_severity['Normalized'])

    if ast.literal_eval(os.environ.get('ENABLE_FORK_COPY_SEVERITY', 'False')):
        if severity == int(os.environ.get('FORK_COPY_SEVERITY_VALUE', '90')):
            slack.chat.post_message(
                fallback_channel,
                parsed_message['message'],
                attachments=parsed_message['attachments']
            )
            LOGGER.debug(
                'sent to fallback channel %s due to severity %s',
                fallback_channel,
                severity
            )

    if ast.literal_eval(os.environ.get('ENABLE_FORK_ONLY_SEVERITY', 'False')):

        if severity == int(os.environ.get('FORK_ONLY_SEVERITY_VALUE', '100')):
            slack.chat.post_message(
                fallback_channel,
                parsed_message['message'],
                attachments=parsed_message['attachments']
            )
            LOGGER.debug(
                'sent to fallback channel %s due to severity %s',
                fallback_channel,
                severity
            )

    # Send if were not doing fork only, or if fork only is on
    # but the severity doesnt match
    if not ast.literal_eval(
        os.environ.get('ENABLE_FORK_ONLY_SEVERITY', 'False')
    ) or severity != int(os.environ.get('FORK_ONLY_SEVERITY_VALUE', '100')):
        slack.chat.post_message(
            slack_channel,
            parsed_message['message'],
            attachments=parsed_message['attachments']
        )

    LOGGER.debug(
        'Sent to main channel %s',
        slack_channel
    )
