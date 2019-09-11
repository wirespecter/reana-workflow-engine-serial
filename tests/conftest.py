# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2019 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration for REANA Workflow Engine Serial."""

import pytest


@pytest.fixture
def multiple_named_steps_workflow(serial_workflow):
    """Multiple named steps workflow."""
    num_steps = 4
    step_name_prefix = 'step_'
    named_steps = []
    serial_workflow_spec = \
        serial_workflow['reana_specification']['workflow']['specification']

    for step_number in range(num_steps):
        named_steps.append(
            {'name': f'{step_name_prefix}{step_number}',
             'environment': 'busybox',
             'commands': [f'echo "Step number {step_number}."']})
    serial_workflow_spec['steps'] = named_steps
    return num_steps, step_name_prefix, serial_workflow_spec
