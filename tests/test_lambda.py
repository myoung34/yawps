# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
""" lambda tests """
from unittest import mock

from yawps.lambda_function import lambda_handler

from .mock_aws import mock_make_api_call


@mock.patch(
    'botocore.client.BaseClient._make_api_call',
    new=mock_make_api_call,
)
@mock.patch('yawps.lambda_function.Slacker')
def test_securityhub(
    mock_slacker,
    securityhub_finding_fixture,
):
    """ basic securityhub finding test """
    lambda_handler(securityhub_finding_fixture, {})
    assert mock_slacker.mock_calls == [
        mock.call('foo'),
        mock.call().chat.post_message(
            'someteamchannel',
            'SecurityHub Finding `Config.1 AWS Config should be enabled`',
            attachments=[{
                'mrkdwn_in': ['text'],
                'fallback': 'This AWS control checks whether the Config service is enabled in the account for the local region and is recording all resources.',  # noqa
                'message': '',
                'color': 'bad',
                'title': 'For directions on how to fix this issue, consult the AWS Security Hub Foundational Security Best Practices documentation.',  # noqa
                'title_link': 'https://docs.aws.amazon.com/console/securityhub/Config.1/remediation',  # noqa
                'fields': [
                    {
                        'title': 'Severity',
                        'value': 'MEDIUM',
                        'short': True
                    },
                    {
                        'title': 'Security Hub Findings',
                        'value': 'Software and Configuration Checks/Industry and Regulatory Standards/AWS-Foundational-Security-Best-Practices',  # noqa
                        'short': False
                    },
                    {
                        'title': 'Some Team Name That Reads Well (1111111111) - us-east-1',  # noqa
                        'value': 'This AWS control checks whether the Config service is enabled in the account for the local region and is recording all resources.',  # noqa
                        'short': False
                    },
                    {
                        'title': 'Affected resource(s)',
                        'value': 'AWS::::Account:1111111111',
                        'short': False
                    }
                ]
            }]
        )
    ]
