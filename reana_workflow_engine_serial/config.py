# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018, 2019, 2020, 2021, 2022 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA Workflow Engine Serial config."""

from distutils.util import strtobool
import os

MOUNT_CVMFS = os.getenv("REANA_MOUNT_CVMFS", "false")

JOB_STATUS_POLLING_INTERVAL = os.getenv("POLLING_INTERVAL", 3)
"""Polling interval in seconds for status of running jobs."""

CACHE_ENABLED = False
"""Determines if jobs caching is enabled."""

WORKFLOW_KERBEROS = bool(strtobool(os.getenv("REANA_WORKFLOW_KERBEROS", "false")))
"""Whether Kerberos is needed for the whole workflow."""
