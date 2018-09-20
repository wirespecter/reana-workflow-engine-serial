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

"""REANA Workflow Engine Serial tasks."""

from __future__ import absolute_import, print_function

from distutils.dir_util import copy_tree
import json
import logging
import os
from time import sleep

from reana_commons.publisher import Publisher
from reana_commons.serial import serial_load

from .api_client import create_openapi_client
from .celeryapp import app
from .config import SHARED_VOLUME_PATH

log = logging.getLogger(__name__)

rjc_api_client = create_openapi_client('reana-job-controller')


def get_job_status(job_id):
    """Get the result from a job launched in reana-job-controller."""
    response, http_response = rjc_api_client.jobs.get_job(
        job_id=job_id).result()
    return response


def _check_if_cached(job_spec, step, workflow_workspace):
    """Query job controller job cache."""
    try:
        return rjc_api_client.job_cache.check_if_cached(
            job_spec=json.dumps(job_spec),
            workflow_json=json.dumps(step),
            workflow_workspace=workflow_workspace).\
            result()
    except ConnectionError:
        _check_if_cached(job_spec, step, workflow_workspace)


def _create_job(job):
    """Call job controller to create a job."""
    try:
        return rjc_api_client.jobs.create_job(
            job=job).result()
    except ConnectionError:
        _create_job(job)


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
                        toplevel=os.getcwd(), workflow_parameters=None,
                        engine_parameters=None):
    """Run a serial workflow."""
    workflow_workspace = '{0}/{1}'.format(SHARED_VOLUME_PATH,
                                          workflow_workspace)
    publisher = Publisher()
    publisher.connect()

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
                "job_name": command,
                "experiment": os.getenv("REANA_WORKFLOW_ENGINE_EXPERIMENT",
                                        "serial_experiment"),
                "docker_img": step["environment"],
                "cmd": "bash -c \"cd {0} ; {1} \"".format(
                    workflow_workspace, escape_shell_arg(command)),
                'prettified_cmd': command,
                "max_restart_count": 0,
                "env_vars": {},
                "job_type": "kubernetes",
                "shared_file_system": True,
                "workflow_workspace": workflow_workspace
            }
            job_spec_copy = dict(job_spec)
            clean_cmd = ';'.join(job_spec_copy['cmd'].split(';')[1:])
            job_spec_copy['cmd'] = clean_cmd
            if 'CACHE' not in engine_parameters or \
                    engine_parameters.get('CACHE').lower() != 'off':
                _, http_response = _check_if_cached(job_spec_copy,
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
                    if step == workflow_json['steps'][-1] and \
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
            response, http_response = _create_job(job=job_spec)
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
            job_status = get_job_status(job_id)

            while job_status.status not in ['succeeded', 'failed']:
                job_status = get_job_status(job_id)
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
                if step == workflow_json['steps'][-1] and \
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

    if last_step != workflow_json['steps'][-1]:
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
