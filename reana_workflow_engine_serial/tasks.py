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

import logging
import os
from time import sleep

from .api_client import create_openapi_client
from .config import SHARED_VOLUME_PATH
from .celeryapp import app

log = logging.getLogger(__name__)
outputs_dir_name = 'outputs'
known_dirs = ['inputs', 'logs', outputs_dir_name]

rjc_api_client = create_openapi_client('reana-job-controller')


def get_job_status(job_id):
    """Get the result from a job launched in reana-job-controller."""
    response, http_response = rjc_api_client.jobs.get_job(
        job_id=job_id).result()
    return response


@app.task(name='tasks.run_serial_workflow',
          ignore_result=True)
def run_serial_workflow(workflow_uuid, workflow_workspace,
                        workflow=None, workflow_json=None,
                        toplevel=os.getcwd(), parameters=None):
    workflow_workspace = '{0}/{1}'.format(SHARED_VOLUME_PATH, workflow_workspace)

    # use API of Workflow Controller and Job Controller to update status
    # and not have access to the DB.
    # TODO
    for step in workflow_json['steps']:
        job_spec = {
            'experiment': os.getenv('REANA_WORKFLOW_ENGINE_EXPERIMENT',
                                    'serial_experiment'),
            'docker_img': step['environment'],
            'cmd': ' && '.join(step['commands']),
            'max_restart_count': 0,
            'env_vars': {},
            'job_type': 'kubernetes'
        }
        response, http_response = rjc_api_client.jobs.create_job(
            job=job_spec).result()
        job_id = str(response['job_id'])
        print('job_id:', job_id)
        job_status = get_job_status(job_id)
        while job_status.status not in ['succeeded', 'failed']:
            job_status = get_job_status(job_id)
            print('Status is still:', job_status.status)
            sleep(1)

    print('done')
