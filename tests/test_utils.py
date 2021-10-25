# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2019, 2020, 2021 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Workflow Engine Serial utils tests."""

import logging

from reana_workflow_engine_serial.utils import get_targeted_workflow_steps


def test_partial_workflow(caplog, multiple_named_steps_workflow):
    """Test that the produced workflow has only the specified steps."""
    caplog.set_level(logging.INFO)
    num_steps, step_prefix, workflow_spec = multiple_named_steps_workflow
    # Test that all subsets of the workflow steps are targetable and respected
    for step_num in range(num_steps):
        steps_by_name = get_targeted_workflow_steps(
            workflow_spec, f"{step_prefix}{step_num}"
        )
        assert len(steps_by_name) == step_num + 1
    # User does not specify a target
    assert len(get_targeted_workflow_steps(workflow_spec)) == len(
        workflow_spec["steps"]
    )
    # User specifies a no existing target
    wrong_step_name = "wrong_name"
    wrong_step_name_workflow = get_targeted_workflow_steps(
        workflow_spec, wrong_step_name
    )
    assert len(wrong_step_name_workflow) == num_steps


def test_from_step_workflow_execution(multiple_named_steps_workflow):
    """Test workflow execution from certain step."""
    num_steps, step_prefix, workflow_spec = multiple_named_steps_workflow
    for step_num in range(num_steps):
        steps_by_name = get_targeted_workflow_steps(
            workflow_spec, None, f"{step_prefix}{step_num}"
        )
        assert len(steps_by_name) == num_steps - step_num
    # from 2nd to 3d step
    second_third_step_workflow = get_targeted_workflow_steps(
        workflow_spec, f"{step_prefix}{3}", f"{step_prefix}{2}"
    )
    assert len(second_third_step_workflow) == 2
    assert second_third_step_workflow[0]["name"] == f"{step_prefix}{2}"
    assert second_third_step_workflow[1]["name"] == f"{step_prefix}{3}"
