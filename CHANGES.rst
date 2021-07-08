Changes
=======

Version 0.7.5 (2021-07-05)
--------------------------
- Changes internal dependencies to remove click.

Version 0.7.4 (2021-04-28)
--------------------------

- Adds support for specifying ``kubernetes_memory_limit`` for Kubernetes compute backend jobs.

Version 0.7.3 (2021-03-17)
--------------------------

- Changes workflow engine instantiation to use central REANA-Commons factory.
- Changes job command strings by removing interpreter and using central REANA-Commons job command serialisation.
- Changes status ``succeeded`` to ``finished`` to use central REANA nomenclature.

Version 0.7.2 (2021-02-03)
--------------------------

- Fixes minor code warnings.
- Changes CI system to include Python flake8 and Dockerfile hadolint checkers.

Version 0.7.1 (2020-11-10)
--------------------------

- Adds support for specifying ``htcondor_max_runtime`` and ``htcondor_accounting_group`` for HTCondor compute backend jobs.

Version 0.7.0 (2020-10-20)
--------------------------

- Adds possibility to execute workflow from specified step.
- Adds option to specify unpacked Docker images as workflow step requirement.
- Adds option to specify Kubernetes UID for jobs.
- Adds support for VOMS proxy as a new authentication method.
- Adds pinning of all Python dependencies allowing to easily rebuild component images at later times.
- Changes base image to use Python 3.8.
- Changes code formatting to respect ``black`` coding style.
- Changes documentation to single-page layout.

Version 0.6.1 (2020-05-25)
--------------------------

- Upgrades REANA-Commons package using latest Kubernetes Python client version.

Version 0.6.0 (2019-12-20)
--------------------------

- Allows to specify compute backend (HTCondor, Kubernetes or Slurm) and
  Kerberos authentication requirement for Serial workflow jobs.
- Allows partial workflow execution until step specified by the user.
- Moves workflow engine to the same Kubernetes pod with the REANA-Job-Controller
  (sidecar pattern).

Version 0.5.0 (2019-04-23)
--------------------------

- Makes workflow engine independent of Celery so that independent workflow
  instances are created on demand for each user.
- Replaces ``api_client`` module with centralised one from REANA-Commons.
- Introduces CVMFS mounts in job specifications.
- Makes docker image slimmer by using ``python:3.6-slim``.
- Centralises log level and log format configuration.

Version 0.4.0 (2018-11-06)
--------------------------

- Improves AMQP re-connection handling. Switches from ``pika`` to ``kombu``.
- Utilises common openapi client for communication with REANA-Job-Controller.
- Changes license to MIT.

Version 0.3.2 (2018-09-25)
--------------------------

- Modifies OS related commands for CephFS compatibility.

Version 0.3.1 (2018-09-07)
--------------------------

- Adds parameter passing to workflow steps.
- Adds user guide and getting started sections to the documentation.

Version 0.3.0 (2018-08-10)
--------------------------

- Initial public release.
- Executes serial workflows.
- Tracks progress of workflow runs.
- Caches job results by default.
