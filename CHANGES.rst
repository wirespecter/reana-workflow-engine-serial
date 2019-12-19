Changes
=======

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
