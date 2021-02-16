# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Workflow Engine Serial tasks."""

from __future__ import absolute_import, print_function

import logging
import os

import click
from reana_commons.api_client import JobControllerAPIClient
from reana_commons.config import REANA_LOG_FORMAT, REANA_LOG_LEVEL, SHARED_VOLUME_PATH
from reana_commons.publisher import WorkflowStatusPublisher
from reana_commons.serial import serial_load
from reana_commons.utils import (
    check_connection_to_job_controller,
    handle_workflow_engine_graceful_exit,
)

from .config import CACHE_ENABLED
from .utils import (
    build_job_spec,
    check_cache,
    copy_workspace_from_cache,
    copy_workspace_to_cache,
    get_targeted_workflow_steps,
    load_json,
    poll_job_status,
    publish_cache_copy,
    publish_job_submission,
    publish_job_success,
    publish_workflow_failure,
    publish_workflow_start,
    sanitize_command,
)

RJC_API_CLIENT = JobControllerAPIClient("reana-job-controller")
PUBLISHER = WorkflowStatusPublisher()


@click.command()
@click.option("--workflow-uuid", required=True, help="UUID of workflow to be run.")
@click.option(
    "--workflow-workspace",
    required=True,
    help="Name of workspace in which workflow should run.",
)
@click.option(
    "--workflow-json",
    help="JSON representation of workflow object to be run.",
    callback=load_json,
)
@click.option(
    "--workflow-parameters",
    help="JSON representation of parameters received by" " the workflow.",
    callback=load_json,
)
@click.option(
    "--operational-options",
    help="Options to be passed to the workflow engine" " (e.g. caching).",
    callback=load_json,
)
@handle_workflow_engine_graceful_exit(publisher=PUBLISHER)
def run_serial_workflow(
    workflow_uuid,
    workflow_workspace,
    workflow_json=None,
    workflow_parameters=None,
    operational_options=None,
):
    """Run a serial workflow."""
    try:
        check_connection_to_job_controller()
        workflow_workspace, cache_enabled, = initialize(
            workflow_uuid, workflow_workspace, operational_options
        )

        run(
            workflow_json,
            workflow_parameters,
            operational_options,
            workflow_uuid,
            workflow_workspace,
            PUBLISHER,
            cache_enabled,
        )

        status = "finished"

    except Exception as e:
        logging.debug(str(e))
        status = "failed"
        if PUBLISHER:
            publish_workflow_failure(None, workflow_uuid, PUBLISHER)
        else:
            logging.error(
                "Workflow {workflow_uuid} failed but status "
                "could not be published.".format(workflow_uuid=workflow_uuid)
            )

    finally:
        cleanup(workflow_uuid, workflow_workspace, PUBLISHER, status)


def initialize(workflow_uuid, workflow_workspace, operational_options):
    """Initialize engine."""
    # configure the logger
    logging.basicConfig(level=REANA_LOG_LEVEL, format=REANA_LOG_FORMAT)

    # set cache on or off
    if not operational_options:
        operational_options = {}
    if CACHE_ENABLED:
        if (
            "CACHE" not in operational_options
            or operational_options.get("CACHE", "").lower() != "off"
        ):
            cache_enabled = True
        else:
            cache_enabled = False
    else:
        cache_enabled = False

    # build workspace path
    workflow_workspace = "{0}/{1}".format(SHARED_VOLUME_PATH, workflow_workspace)

    return workflow_workspace, cache_enabled


def run(
    workflow_json,
    workflow_parameters,
    operational_options,
    workflow_uuid,
    workflow_workspace,
    publisher,
    cache_enabled,
):
    """Run a serial workflow."""
    operational_options = operational_options or {}
    expanded_workflow_json = serial_load(None, workflow_json, workflow_parameters)
    steps_to_run = get_targeted_workflow_steps(
        expanded_workflow_json,
        operational_options.get("TARGET", None),
        operational_options.get("FROM", None),
    )
    workflow_json["steps"] = expanded_workflow_json["steps"] = steps_to_run
    publish_workflow_start(steps_to_run, workflow_uuid, publisher)

    for step_number, step in enumerate(steps_to_run):
        status = run_step(
            step_number,
            step,
            workflow_workspace,
            cache_enabled,
            expanded_workflow_json,
            workflow_json,
            publisher,
            workflow_uuid,
        )
        if status != "succeeded":
            break


def run_step(
    step_number,
    step,
    workflow_workspace,
    cache_enabled,
    expanded_workflow_json,
    workflow_json,
    publisher,
    workflow_uuid,
):
    """Run a step of a serial workflow."""
    for command in step["commands"]:
        job_spec = build_job_spec(
            job_name=step.get("name", ""),
            image=step["environment"],
            compute_backend=step.get("compute_backend", ""),
            command=command,
            workflow_workspace=workflow_workspace,
            workflow_uuid=workflow_uuid,
            kerberos=step.get("kerberos", False),
            unpacked_image=step.get("unpacked_image", False),
            kubernetes_uid=step.get("kubernetes_uid", None),
            voms_proxy=step.get("voms_proxy", False),
            htcondor_max_runtime=step.get("htcondor_max_runtime", ""),
            htcondor_accounting_group=step.get("htcondor_accounting_group", ""),
        )

        job_spec_copy = dict(job_spec)
        job_spec_copy["cmd"] = sanitize_command(job_spec_copy["cmd"])

        if cache_enabled:
            cached_info = check_cache(
                RJC_API_CLIENT, job_spec_copy, step, workflow_workspace
            )
            if (
                cached_info.get("result_path")
                and os.path.exists(cached_info.get("result_path"))
                and os.listdir(cached_info.get("result_path"))
            ):
                copy_workspace_from_cache(
                    cached_info["result_path"], workflow_workspace
                )
                publish_cache_copy(
                    cached_info["job_id"],
                    step,
                    expanded_workflow_json,
                    command,
                    publisher,
                    workflow_uuid,
                )
                continue
        response = RJC_API_CLIENT.submit(**job_spec)
        job_id = str(response["job_id"])
        publish_job_submission(
            step_number, command, workflow_json, job_id, publisher, workflow_uuid
        )

        job_status = poll_job_status(RJC_API_CLIENT, job_id)
        if job_status.status == "succeeded":
            cache_dir_path = None
            if cache_enabled:
                cache_dir_path = copy_workspace_to_cache(job_id, workflow_workspace)

            publish_job_success(
                job_id,
                job_spec,
                workflow_workspace,
                expanded_workflow_json,
                step,
                command,
                publisher,
                workflow_uuid,
                cache_dir_path=cache_dir_path,
            )
        else:
            publish_workflow_failure(job_id, workflow_uuid, publisher)
            return job_status.status
    return job_status.status


def cleanup(workflow_uuid, workflow_workspace, publisher, status):
    """Do cleanup tasks before exiting."""
    logging.info(
        f"Workflow {workflow_uuid} {status}. Files available "
        f"at {workflow_workspace}."
    )
    publisher.close()
