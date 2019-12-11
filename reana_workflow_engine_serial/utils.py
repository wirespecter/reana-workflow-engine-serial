# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA-Workflow-Engine-Serial utilities."""

import base64
import json
import logging
import os
from distutils.dir_util import copy_tree
from time import sleep

from reana_commons.utils import (build_caching_info_message,
                                 build_progress_message)

from .config import JOB_STATUS_POLLING_INTERVAL, MOUNT_CVMFS


def sanitize_command(command):
    """Sanitize command."""
    return ';'.join(command.split(';')[1:])


def load_json(ctx, param, value):
    """Load json callback function."""
    value = str.encode(value[1:])
    return json.loads(base64.standard_b64decode(value).decode())


def escape_shell_arg(shell_arg):
    """Escape double quotes.

    :param shell_arg: The shell argument to be escaped.
    """
    if type(shell_arg) is not str:
        msg = "ERROR: escape_shell_arg() expected string argument but " \
              "got '%s' of type '%s'." % (repr(shell_arg), type(shell_arg))
        raise TypeError(msg)

    return "%s" % shell_arg.replace('"', '\\"')


def build_job_spec(job_name, image, compute_backend, command,
                   workflow_workspace, workflow_uuid, kerberos):
    """Build job specification to passed to RJC."""
    job_spec = {
        "image": image,
        "compute_backend": compute_backend,
        "cmd": "bash -c \"cd {0} ; {1} \"".format(
            workflow_workspace, escape_shell_arg(command)),
        "prettified_cmd": command,
        "workflow_workspace": workflow_workspace,
        "job_name": job_name,
        "cvmfs_mounts": MOUNT_CVMFS,
        "workflow_uuid": workflow_uuid,
        "kerberos": kerberos,
    }
    return job_spec


def check_cache(rjc_api_client,
                job_spec_copy,
                step,
                workflow_workspace):
    """Check if job exists in cache."""
    http_response = rjc_api_client.check_if_cached(
                        job_spec_copy,
                        step,
                        workflow_workspace)
    result = http_response.json()
    if result['cached']:
        return result
    return {}


def copy_workspace_from_cache(result_path,
                              workflow_workspace):
    """Restore workspace contents from cache."""
    os.system('cp -R {source} {dest}'.format(
        source=os.path.join(result_path, '*'),
        dest=workflow_workspace))


def copy_workspace_to_cache(job_id,
                            workflow_workspace):
    """Copy workspace contents to cache."""
    logging.info('Caching result to ../archive/{}'.format(job_id))
    logging.info('workflow_workspace: {}'.format(workflow_workspace))

    # Create the cache directory if it doesn't exist
    cache_dir_path = os.path.abspath(os.path.join(
        workflow_workspace, os.pardir, 'archive', job_id))
    logging.info('cache_dir_path: {}'.format(cache_dir_path))
    os.makedirs(cache_dir_path)

    # Copy workspace contents to cache directory
    copy_tree(workflow_workspace, cache_dir_path)
    return cache_dir_path


def publish_cache_copy(job_id,
                       step,
                       expanded_workflow_json,
                       command,
                       publisher,
                       workflow_uuid):
    """Publish to MQ the cache hit."""
    logging.info('Copied from cache')
    if step == expanded_workflow_json['steps'][-1] and \
            command == step['commands'][-1]:
        workflow_status = 2
    else:
        workflow_status = 1
    succeeded_jobs = {"total": 1, "job_ids": [job_id]}
    publisher.publish_workflow_status(
        workflow_uuid, workflow_status,
        message={
            "progress": build_progress_message(
                finished=succeeded_jobs,
                cached=succeeded_jobs
            )
        }
    )


def publish_job_submission(step_number,
                           command,
                           workflow_json,
                           job_id,
                           publisher,
                           workflow_uuid):
    """Publish to MQ the job submission."""
    logging.info(
        'Publishing step:{0}, cmd: {1},'
        ' total steps {2} to MQ'.
        format(
            step_number,
            command,
            len(workflow_json['steps']))
    )
    running_jobs = {"total": 1, "job_ids": [job_id]}

    publisher.publish_workflow_status(
        workflow_uuid, status=1,
        message={
            "progress":
            build_progress_message(running=running_jobs)
        }
    )


def poll_job_status(rjc_api_client,
                    job_id):
    """Poll for job status."""
    job_status = rjc_api_client.check_status(job_id)

    while job_status.status not in ['succeeded', 'failed']:
        job_status = rjc_api_client.check_status(job_id)
        sleep(JOB_STATUS_POLLING_INTERVAL)

    return job_status


def publish_job_success(job_id,
                        job_spec,
                        workflow_workspace,
                        expanded_workflow_json,
                        step,
                        command,
                        publisher,
                        workflow_uuid,
                        cache_dir_path=None):
    """Publish to MQ the job success."""
    finished_jobs = {"total": 1, "job_ids": [job_id]}
    if step == expanded_workflow_json['steps'][-1] and \
            command == step['commands'][-1]:
        workflow_status = 2
    else:
        workflow_status = 1

    message = {}
    message["progress"] = build_progress_message(finished=finished_jobs)
    if cache_dir_path:
        message["caching_info"] = build_caching_info_message(
            job_spec,
            job_id,
            workflow_workspace,
            step,
            cache_dir_path
        )
    publisher.publish_workflow_status(workflow_uuid,
                                      workflow_status,
                                      message=message)


def publish_workflow_start(workflow_json,
                           workflow_uuid,
                           publisher):
    """Publish to MQ the start of the workflow."""
    total_commands = 0
    for step in workflow_json['steps']:
        total_commands += len(step['commands'])
    total_jobs = {"total": total_commands, "job_ids": []}
    publisher.publish_workflow_status(workflow_uuid, 1,
                                      message={
                                          "progress":
                                          build_progress_message(
                                              total=total_jobs)
                                      })


def publish_workflow_failure(job_id,
                             workflow_uuid,
                             publisher):
    """Publish to MQ the workflow failure."""
    failed_jobs = {"total": 1, "job_ids": [job_id]} if job_id else None

    publisher.publish_workflow_status(workflow_uuid, 3,
                                      message={
                                          "progress":
                                          build_progress_message(
                                              failed=failed_jobs)
                                      })


def get_targeted_workflow_steps(workflow_json, target_step):
    """Build the workflow steps until the given target step.

    :param workflow_json: Dictionary representing the serial workflow spec.
    :type dict:
    :param target_step: Step until which the workflow will be run identified
        by name.
    :type str:
    :returns: A list of the steps which should be run.
    :rtype: dict
    """
    selected_steps = []
    if target_step:
        target_step_matched = False
        for step in workflow_json['steps']:
            selected_steps.append(step)
            if step['name'] == target_step:
                target_step_matched = True
                break
        if not target_step_matched:
            logging.info(f'The target step {target_step} was not found, '
                         f'running the complete workflow.')
    else:
        selected_steps = workflow_json['steps']
    return selected_steps
