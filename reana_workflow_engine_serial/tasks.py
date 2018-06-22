# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# REANA is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# REANA; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization or
# submit itself to any jurisdiction.

from __future__ import absolute_import, print_function

import json
import logging
import os
from time import sleep

import pika

from .api_client import create_openapi_client
from .celeryapp import app
from .config import (BROKER_PASS, BROKER_PORT, BROKER_URL, BROKER_USER,
                     OUTPUTS_DIRECTORY_RELATIVE_PATH, SHARED_VOLUME_PATH)

log = logging.getLogger(__name__)
outputs_dir_name = 'outputs'
known_dirs = ['inputs', 'logs', outputs_dir_name]

rjc_api_client = create_openapi_client('reana-job-controller')


def get_job_status(job_id):
    """Get the result from a job launched in reana-job-controller."""
    response, http_response = rjc_api_client.jobs.get_job(
        job_id=job_id).result()
    return response


def declare_job_status_queue():
    broker_credentials = pika.PlainCredentials(BROKER_USER,
                                               BROKER_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(BROKER_URL,
                                  BROKER_PORT,
                                  '/',
                                  broker_credentials))
    channel = connection.channel()
    channel.queue_declare(queue='jobs-status')
    return channel


def publish_workflow_status(channel, workflow_uuid, status,
                            logs='',
                            message=None):
    """Update database workflow status.

    :param workflow_uuid: UUID which represents the workflow.
    :param status: String that represents the analysis status.
    :param status_message: String that represents the message related with the
       status, if there is any.
    """
    log.info('Publishing Workflow: {0} Status: {1}'.
             format(workflow_uuid, status))
    channel.basic_publish(exchange='',
                          routing_key='jobs-status',
                          body=json.dumps({"workflow_uuid": workflow_uuid,
                                           "logs": logs,
                                           "status": status,
                                           "message": message}),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # msg persistent
                          ))


def escape_shell_arg(shell_arg):
    """Escapes double quotes.

    :param shell_arg: The shell argument to be escaped.
    """
    if type(shell_arg) is not str:
        msg = "ERROR: escape_shell_arg() expected string argument but " \
              "got '%s' of type '%s'." % (repr(shell_arg), type(shell_arg))
        raise TypeError(msg)

    return "%s" % shell_arg.replace('"', '\\"')


@app.task(name='tasks.run_serial_workflow',
          ignore_result=True)
def run_serial_workflow(workflow_uuid, workflow_workspace,
                        workflow=None, workflow_json=None,
                        toplevel=os.getcwd(), parameters=None):
    workflow_workspace = '{0}/{1}'.format(SHARED_VOLUME_PATH,
                                          workflow_workspace)
    channel = declare_job_status_queue()

    last_step = 'START'
    total_commands = 0
    for step in workflow_json['steps']:
        total_commands += len(step['commands'])
    planned_jobs = {"total": total_commands, "job_ids": []}
    publish_workflow_status(channel, workflow_uuid, 1,
                            logs='',
                            message={
                                "progress": {
                                    "planned":
                                    planned_jobs,
                                }})
    current_command_idx = 0

    for step_number, step in enumerate(workflow_json['steps']):
        last_command = 'START'
        for command in step['commands']:
            current_command_idx += 1
            job_spec = {
                'experiment': os.getenv('REANA_WORKFLOW_ENGINE_EXPERIMENT',
                                        'serial_experiment'),
                'docker_img': step['environment'],
                'cmd': 'bash -c \"cd {0} ; {1} \"'.format(
                    workflow_workspace, escape_shell_arg(command)),
                'max_restart_count': 0,
                'env_vars': {},
                'job_type': 'kubernetes',
                'shared_file_system': True,
            }
            response, http_response = rjc_api_client.jobs.create_job(
                job=job_spec).result()
            job_id = str(response['job_id'])
            print('~~~~~~ Publishing step:{0}, cmd: {1},'
                  ' total steps {2} to MQ'.
                  format(step_number, command, len(workflow_json['steps'])))
            submitted_jobs = {"total": 1, "job_ids": [job_id]}

            publish_workflow_status(channel, workflow_uuid, 1,
                                    logs='',
                                    message={
                                        "progress": {
                                            "submitted":
                                            submitted_jobs,
                                        }})
            job_status = get_job_status(job_id)

            while job_status.status not in ['succeeded', 'failed']:
                job_status = get_job_status(job_id)
                sleep(1)

            if job_status.status == 'succeeded':
                succeeded_jobs = {"total": 1, "job_ids": [job_id]}
                last_command = command
                if step == workflow_json['steps'][-1] and \
                        command == step['commands'][-1]:
                    publish_workflow_status(channel, workflow_uuid, 2,
                                            message={
                                                "progress": {
                                                    "succeeded":
                                                    succeeded_jobs,
                                                }
                                            })
                else:
                    publish_workflow_status(channel, workflow_uuid, 1,
                                            message={
                                                "progress": {
                                                    "succeeded":
                                                    succeeded_jobs,
                                                }
                                            })
            else:
                break

        if last_command == step['commands'][-1]:
            last_step = step

    if last_step != workflow_json['steps'][-1]:
        publish_workflow_status(channel, workflow_uuid, 3,
                                message={
                                    "progress": {
                                        "failed": {"total": 1,
                                                   "job_ids": [job_id]}
                                    }
                                })

    workflow_workspace_content = \
        os.path.join(workflow_workspace, '*')
    absolute_outputs_directory_path = os.path.join(
        workflow_workspace, '..', OUTPUTS_DIRECTORY_RELATIVE_PATH)
    log.info('Copying {source} to {dest}.'.format(
        source=workflow_workspace_content,
        dest=absolute_outputs_directory_path))
    os.system('cp -R {source} {dest}'.format(
        source=workflow_workspace_content,
        dest=absolute_outputs_directory_path))
    log.info('Workflow outputs copied to `/outputs` directory.')
