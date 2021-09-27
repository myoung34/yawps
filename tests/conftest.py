# -*- coding: utf-8 -*-
""" Test fixtures """
import json
import os

import pytest


@pytest.fixture()
def securityhub_finding_fixture():
    """ Generic securityhub finding fixture"""
    payload_file = os.path.join(
        os.path.dirname(__file__),
        'fixtures',
        'eventbridge.json'
    )
    with open(payload_file) as data_file:
        return json.load(data_file)
