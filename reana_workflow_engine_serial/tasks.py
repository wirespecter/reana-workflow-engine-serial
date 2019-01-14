# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Workflow Engine Serial tasks."""

from __future__ import absolute_import, print_function

import click
import base64
import json
import logging
import os
from distutils.dir_util import copy_tree
from time import sleep

from reana_commons.api_client import JobControllerAPIClient
from reana_commons.publisher import WorkflowStatusPublisher
from reana_commons.serial import serial_load

from .config import SHARED_VOLUME_PATH

log = logging.getLogger(__name__)

rjc_api_client = JobControllerAPIClient('reana-job-controller')


def escape_shell_arg(shell_arg):
    """Escapes double quotes.

    :param shell_arg: The shell argument to be escaped.
    """
    if type(shell_arg) is not str:
        msg = "ERROR: escape_shell_arg() expected string argument but " \
              "got '%s' of type '%s'." % (repr(shell_arg), type(shell_arg))
        raise TypeError(msg)

    return "%s" % shell_arg.replace('"', '\\"')


def load_json(ctx, param, value):
    """Callback function for click option"""
    value = str.encode(value[1:])
    return json.loads(base64.standard_b64decode(value).decode())


@click.command()
@click.option('--workflow-uuid',
              required=True,
              help='UUID of workflow to be run.')
@click.option('--workflow-workspace',
              required=True,
              help='Name of workspace in which workflow should run.')
@click.option('--workflow-json',
              help='JSON representation of workflow object to be run.',
              callback=load_json)
@click.option('--workflow-parameters',
              help='JSON representation of parameters received by'
                   ' the workflow.',
              callback=load_json)
@click.option('--operational-options',
              help='Options to be passed to the workflow engine'
                   ' (e.g. caching).',
              callback=load_json)
def run_serial_workflow(workflow_uuid, workflow_workspace,
                        workflow_json=None, workflow_parameters=None,
                        operational_options=None):
    """Run a serial workflow."""
    if not operational_options:
        operational_options = {}
    workflow_workspace = '{0}/{1}'.format(SHARED_VOLUME_PATH,
                                          workflow_workspace)
    publisher = WorkflowStatusPublisher()

    last_step = 'START'
    total_commands = 0
    for step in workflow_json['steps']:
        total_commands += len(step['commands'])
    publisher.publish_workflow_status(workflow_uuid, 1,
                                      message={
                                          "progress": {
                                              "total":
                                              {"total": total_commands,
                                               "job_ids": []},
                                          }})

    expanded_workflow_json = serial_load(None, workflow_json,
                                         workflow_parameters)

    current_command_idx = 0
    for step_number, step in enumerate(expanded_workflow_json['steps']):
        last_command = 'START'
        for command in step['commands']:
            current_command_idx += 1
            job_spec = {
                "experiment": os.getenv("REANA_WORKFLOW_ENGINE_EXPERIMENT",
                                        "default"),
                "image": step["environment"],
                "cmd": "bash -c \"cd {0} ; {1} \"".format(
                    workflow_workspace, escape_shell_arg(command)),
                "prettified_cmd": command,
                "workflow_workspace": workflow_workspace,
                "job_name": command,
            }
            job_spec_copy = dict(job_spec)
            clean_cmd = ';'.join(job_spec_copy['cmd'].split(';')[1:])
            job_spec_copy['cmd'] = clean_cmd
            if 'CACHE' not in operational_options or \
                    operational_options.get('CACHE').lower() != 'off':
                http_response = rjc_api_client.check_if_cached(
                    job_spec_copy,
                    step,
                    workflow_workspace)
                result = http_response.json()
                if result['cached']:
                    os.system('cp -R {source} {dest}'.format(
                        source=os.path.join(result['result_path'], '*'),
                        dest=workflow_workspace))
                    print('~~~~~ Copied from cache')
                    last_step = step
                    job_id = result['job_id']
                    if step == expanded_workflow_json['steps'][-1] and \
                            command == step['commands'][-1]:
                        workflow_status = 2
                    else:
                        workflow_status = 1
                    succeeded_jobs = {"total": 1, "job_ids": [job_id]}
                    publisher.publish_workflow_status(
                        workflow_uuid, workflow_status,
                        message={
                            "progress": {
                                "finished":
                                succeeded_jobs,
                                "cached":
                                succeeded_jobs
                            }})
                    continue
            response = rjc_api_client.submit(**job_spec)
            job_id = str(response['job_id'])
            print('~~~~~~ Publishing step:{0}, cmd: {1},'
                  ' total steps {2} to MQ'.
                  format(step_number, command, len(workflow_json['steps'])))
            running_jobs = {"total": 1, "job_ids": [job_id]}

            publisher.publish_workflow_status(workflow_uuid, 1,
                                              logs='',
                                              message={
                                                  "progress": {
                                                      "running":
                                                      running_jobs,
                                                  }})
            job_status = rjc_api_client.check_status(job_id)

            while job_status.status not in ['succeeded', 'failed']:
                job_status = rjc_api_client.check_status(job_id)
                sleep(1)

            if job_status.status == 'succeeded':
                finished_jobs = {"total": 1, "job_ids": [job_id]}
                last_command = command
                log.info('Caching result to ../archive/{}'.format(job_id))
                log.info('workflow_workspace: {}'.format(workflow_workspace))
                # Create the cache directory if it doesn't exist
                cache_dir_path = os.path.abspath(os.path.join(
                    workflow_workspace, os.pardir, 'archive', job_id))
                log.info('cache_dir_path: {}'.format(cache_dir_path))
                os.makedirs(cache_dir_path)
                # Copy workspace contents to cache directory
                copy_tree(workflow_workspace, cache_dir_path)
                if step == expanded_workflow_json['steps'][-1] and \
                        command == step['commands'][-1]:
                    workflow_status = 2
                else:
                    workflow_status = 1
                # Publish workflow status with cache details
                publisher.publish_workflow_status(
                    workflow_uuid, workflow_status,
                    message={
                        "progress": {
                            "finished":
                            finished_jobs,
                        },
                        'caching_info':
                            {'job_spec': job_spec,
                             'job_id': job_id,
                             'workflow_workspace': workflow_workspace,
                             'workflow_json': step,
                             'result_path': cache_dir_path}
                    })
            else:
                break

        if last_command == step['commands'][-1]:
            last_step = step

    if last_step != expanded_workflow_json['steps'][-1]:
        failed_jobs = {"total": 1, "job_ids": [job_id]}
        publisher.publish_workflow_status(workflow_uuid, 3,
                                          message={
                                              "progress": {
                                                  "failed":
                                                  failed_jobs
                                              }
                                          })
    publisher.close()
    log.info('Workflow {workflow_uuid} finished. Files available '
             'at {workflow_workspace}.'.format(
                 workflow_uuid=workflow_uuid,
                 workflow_workspace=workflow_workspace))
