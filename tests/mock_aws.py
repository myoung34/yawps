# -*- coding: utf-8 -*-

import botocore


def mock_make_api_call(self, operation_name, kwarg):
    orig = botocore.client.BaseClient._make_api_call
    if operation_name == 'GetParameter':
        return {
            'Parameter': {
                'Name': '/tooling/slack_token',
                'Type': 'SecureString',
                'Value': 'foo',
            }
        }
    elif operation_name == 'ListTagsForResource':
        return {
            'Tags': [
                {
                    'Key': 'slack_channel',
                    'Value': 'someteamchannel'
                },
                {
                    'Key': 'account_name',
                    'Value': 'Some Team Name That Reads Well'
                },
            ]
        }
    return orig(self, operation_name, kwarg)


def mock_make_api_call_no_tags(self, operation_name, kwarg):
    orig = botocore.client.BaseClient._make_api_call
    if operation_name == 'GetParameter':
        return {
            'Parameter': {
                'Name': '/tooling/slack_token',
                'Type': 'SecureString',
                'Value': 'foo',
            }
        }
    elif operation_name == 'ListTagsForResource':
        return {
            'Tags': [
            ]
        }
    return orig(self, operation_name, kwarg)


def mock_make_api_call_only_account_name(self, operation_name, kwarg):
    orig = botocore.client.BaseClient._make_api_call
    if operation_name == 'GetParameter':
        return {
            'Parameter': {
                'Name': '/tooling/slack_token',
                'Type': 'SecureString',
                'Value': 'foo',
            }
        }
    elif operation_name == 'ListTagsForResource':
        return {
            'Tags': [
                {
                    'Key': 'account_name',
                    'Value': 'Some Team Name That Reads Well'
                },
            ]
        }
    return orig(self, operation_name, kwarg)


def mock_make_api_call_only_slack_channel(self, operation_name, kwarg):
    orig = botocore.client.BaseClient._make_api_call
    if operation_name == 'GetParameter':
        return {
            'Parameter': {
                'Name': '/tooling/slack_token',
                'Type': 'SecureString',
                'Value': 'foo',
            }
        }
    elif operation_name == 'ListTagsForResource':
        return {
            'Tags': [
                {
                    'Key': 'slack_channel',
                    'Value': 'someteamchannel'
                },
            ]
        }
    return orig(self, operation_name, kwarg)
