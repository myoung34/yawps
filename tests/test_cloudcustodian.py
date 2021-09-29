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
def test_cloudcustodian(
    mock_slacker,
    cloudcustodian_fixture,
):
    """ cloudcustodian finding test """
    with mock.patch.dict('os.environ', {
        }
    ):
        lambda_handler(cloudcustodian_fixture, {})
        assert mock_slacker.mock_calls == [
            mock.call('foo'),
            mock.call().chat.post_message(
                'someteamchannel',
                'SecurityHub Finding `engine-admin-login-detected`',
                attachments=[{
                    'mrkdwn_in': ['text'],
                    'fallback': 'A Team Engine admin sso login has occurred',
                    'message': '',
                    'color': 'bad',
                    'title': None,
                    'title_link': None,
                    'fields': [
                        {
                            'title': 'Severity',
                            'value': 'INFORMATIONAL',
                            'short': True
                        },
                        {
                            'title': 'Security Hub Findings',
                            'value': 'Software and Configuration Checks/AWS Security Best Practices',  # noqa
                            'short': False
                        },
                        {
                            'title': 'Some Team Name That Reads Well (3333333333) - us-east-1',  # noqa
                            'value': 'A Team Engine admin sso login has occurred',  # noqa
                            'short': False
                        },
                        {
                            'title': 'Affected resource(s)',
                            'value': 'arn:::3333333333',
                            'short': False
                        }
                    ]
                }]
            )
        ]
