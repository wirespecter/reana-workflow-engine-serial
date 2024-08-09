# Changelog

## [0.95.0](https://github.com/wirespecter/reana-workflow-engine-serial/compare/0.9.3...0.95.0) (2024-08-09)


### ⚠ BREAKING CHANGES

* **python:** drop support for Python 3.6 and 3.7

### Build

* **docker:** pin setuptools to v70 ([#214](https://github.com/wirespecter/reana-workflow-engine-serial/issues/214)) ([c6ae076](https://github.com/wirespecter/reana-workflow-engine-serial/commit/c6ae076bf4c8be9b5018e6acb7b0f94cce134184))
* **docker:** upgrade to Ubuntu 24.04 and Python 3.12 ([#213](https://github.com/wirespecter/reana-workflow-engine-serial/issues/213)) ([5ded981](https://github.com/wirespecter/reana-workflow-engine-serial/commit/5ded981a6c4b22dc49ee4306aed860a4881c9dd3))
* **python:** add minimal `pyproject.toml` ([#214](https://github.com/wirespecter/reana-workflow-engine-serial/issues/214)) ([c3cd6f6](https://github.com/wirespecter/reana-workflow-engine-serial/commit/c3cd6f65d9450dd40a3f9c49461db27283798925))
* **python:** drop support for Python 3.6 and 3.7 ([#208](https://github.com/wirespecter/reana-workflow-engine-serial/issues/208)) ([c5f68ab](https://github.com/wirespecter/reana-workflow-engine-serial/commit/c5f68aba7305f37755722a88b7a79f49a61b1ebf))
* **python:** remove deprecated `pytest-runner` ([#214](https://github.com/wirespecter/reana-workflow-engine-serial/issues/214)) ([5beb31e](https://github.com/wirespecter/reana-workflow-engine-serial/commit/5beb31efbc5dd7ce688fa559621aaf63ee1ed388))
* **python:** use optional deps instead of `tests_require` ([#214](https://github.com/wirespecter/reana-workflow-engine-serial/issues/214)) ([906d439](https://github.com/wirespecter/reana-workflow-engine-serial/commit/906d4397e9670fac20c515a73eeed78567635fc3))


### Continuous integration

* **actions:** update GitHub actions due to Node 16 deprecation ([#204](https://github.com/wirespecter/reana-workflow-engine-serial/issues/204)) ([8ca85c0](https://github.com/wirespecter/reana-workflow-engine-serial/commit/8ca85c0b85a93b60d6202ebdd8ac955bb635a1a9))
* **commitlint:** improve checking of merge commits ([#215](https://github.com/wirespecter/reana-workflow-engine-serial/issues/215)) ([00514b3](https://github.com/wirespecter/reana-workflow-engine-serial/commit/00514b3639e7b2ded09953628f3ac8346ef57db2))
* **pytest:** invoke `pytest` directly instead of `setup.py test` ([#214](https://github.com/wirespecter/reana-workflow-engine-serial/issues/214)) ([3e58d5a](https://github.com/wirespecter/reana-workflow-engine-serial/commit/3e58d5a0dbe61c5c97c628d243cb639a0b3dfd99))


### Chores

* **master:** release 0.95.0-alpha.1 ([5d34691](https://github.com/wirespecter/reana-workflow-engine-serial/commit/5d34691ed5fde8d38720b742bd9921cd52b7fa0e))

## [0.9.3](https://github.com/reanahub/reana-workflow-engine-serial/compare/0.9.2...0.9.3) (2024-03-04)


### Build

* **docker:** install correct extras of reana-commons submodule ([#196](https://github.com/reanahub/reana-workflow-engine-serial/issues/196)) ([b23f4df](https://github.com/reanahub/reana-workflow-engine-serial/commit/b23f4df602d80d62626e8e907181a8c710eb662f))
* **docker:** non-editable submodules in "latest" mode ([#190](https://github.com/reanahub/reana-workflow-engine-serial/issues/190)) ([03a15cf](https://github.com/reanahub/reana-workflow-engine-serial/commit/03a15cfa7973152f9923ecade412d8eab3ea80e3))
* **python:** bump all required packages as of 2024-03-04 ([#200](https://github.com/reanahub/reana-workflow-engine-serial/issues/200)) ([ffc8aec](https://github.com/reanahub/reana-workflow-engine-serial/commit/ffc8aec739e2284f301586d47618ff6c4142643a))
* **python:** bump shared REANA packages as of 2024-03-04 ([#200](https://github.com/reanahub/reana-workflow-engine-serial/issues/200)) ([47c26cc](https://github.com/reanahub/reana-workflow-engine-serial/commit/47c26ccfbfdfc7419c4a6fab1d7abf95a667e4e2))


### Bug fixes

* **progress:** handle stopped jobs ([#195](https://github.com/reanahub/reana-workflow-engine-serial/issues/195)) ([a232a76](https://github.com/reanahub/reana-workflow-engine-serial/commit/a232a76627e09bfb401de4f547540c6012357986))


### Code refactoring

* **docs:** move from reST to Markdown ([#198](https://github.com/reanahub/reana-workflow-engine-serial/issues/198)) ([7507d12](https://github.com/reanahub/reana-workflow-engine-serial/commit/7507d1243af43f4621e117f4f92569f4dd7271f6))


### Continuous integration

* **commitlint:** addition of commit message linter ([#191](https://github.com/reanahub/reana-workflow-engine-serial/issues/191)) ([b7a6ef1](https://github.com/reanahub/reana-workflow-engine-serial/commit/b7a6ef18dae95efae7af791094b5ff79369705b0))
* **commitlint:** allow release commit style ([#201](https://github.com/reanahub/reana-workflow-engine-serial/issues/201)) ([b50b6d0](https://github.com/reanahub/reana-workflow-engine-serial/commit/b50b6d0398fc6d6e4c4704d3698d811b7088921d))
* **commitlint:** check for the presence of concrete PR number ([#197](https://github.com/reanahub/reana-workflow-engine-serial/issues/197)) ([1813ac3](https://github.com/reanahub/reana-workflow-engine-serial/commit/1813ac3a88cd8e33a59040c6bd72ed048a151654))
* **release-please:** initial configuration ([#191](https://github.com/reanahub/reana-workflow-engine-serial/issues/191)) ([d40a675](https://github.com/reanahub/reana-workflow-engine-serial/commit/d40a675cab6b6e8c7631d503358016d427bdac3c))
* **release-please:** update version in Dockerfile ([#194](https://github.com/reanahub/reana-workflow-engine-serial/issues/194)) ([52c34ec](https://github.com/reanahub/reana-workflow-engine-serial/commit/52c34ec2003fd09b8a65ef3cff61b7f9a105041e))
* **shellcheck:** fix exit code propagation ([#197](https://github.com/reanahub/reana-workflow-engine-serial/issues/197)) ([5565b29](https://github.com/reanahub/reana-workflow-engine-serial/commit/5565b29ac7b431561af2cd43e6ed882bbdf57126))


### Documentation

* **authors:** complete list of contributors ([#199](https://github.com/reanahub/reana-workflow-engine-serial/issues/199)) ([e9b25b6](https://github.com/reanahub/reana-workflow-engine-serial/commit/e9b25b6ab37421971d02c52422ed19fce249b4ea))

## 0.9.2 (2023-12-12)

- Adds automated multi-platform container image building for amd64 and arm64 architectures.
- Adds metadata labels to Dockerfile.
- Fixes container image building on the arm64 architecture.

## 0.9.1 (2023-09-27)

- Fixes container image names to be Podman-compatible.

## 0.9.0 (2023-01-19)

- Adds support for specifying `slurm_partition` and `slurm_time` for Slurm compute backend jobs.
- Adds support for Kerberos authentication for workflow orchestration.
- Adds support for Rucio authentication for workflow jobs.
- Changes the base image of the component to Ubuntu 20.04 LTS and reduces final Docker image size by removing build-time dependencies.

## 0.8.1 (2022-02-07)

- Adds support for specifying `kubernetes_job_timeout` for Kubernetes compute backend jobs.
- Fixes workflow stuck in pending status due to early engine fail.

## 0.8.0 (2021-11-22)

- Adds support for custom workspace paths.

## 0.7.5 (2021-07-05)

- Changes internal dependencies to remove click.

## 0.7.4 (2021-04-28)

- Adds support for specifying `kubernetes_memory_limit` for Kubernetes compute backend jobs.

## 0.7.3 (2021-03-17)

- Changes workflow engine instantiation to use central REANA-Commons factory.
- Changes job command strings by removing interpreter and using central REANA-Commons job command serialisation.
- Changes status `succeeded` to `finished` to use central REANA nomenclature.

## 0.7.2 (2021-02-03)

- Fixes minor code warnings.
- Changes CI system to include Python flake8 and Dockerfile hadolint checkers.

## 0.7.1 (2020-11-10)

- Adds support for specifying `htcondor_max_runtime` and `htcondor_accounting_group` for HTCondor compute backend jobs.

## 0.7.0 (2020-10-20)

- Adds possibility to execute workflow from specified step.
- Adds option to specify unpacked Docker images as workflow step requirement.
- Adds option to specify Kubernetes UID for jobs.
- Adds support for VOMS proxy as a new authentication method.
- Adds pinning of all Python dependencies allowing to easily rebuild component images at later times.
- Changes base image to use Python 3.8.
- Changes code formatting to respect `black` coding style.
- Changes documentation to single-page layout.

## 0.6.1 (2020-05-25)

- Upgrades REANA-Commons package using latest Kubernetes Python client version.

## 0.6.0 (2019-12-20)

- Allows to specify compute backend (HTCondor, Kubernetes or Slurm) and
  Kerberos authentication requirement for Serial workflow jobs.
- Allows partial workflow execution until step specified by the user.
- Moves workflow engine to the same Kubernetes pod with the REANA-Job-Controller
  (sidecar pattern).

## 0.5.0 (2019-04-23)

- Makes workflow engine independent of Celery so that independent workflow
  instances are created on demand for each user.
- Replaces `api_client` module with centralised one from REANA-Commons.
- Introduces CVMFS mounts in job specifications.
- Makes docker image slimmer by using `python:3.6-slim`.
- Centralises log level and log format configuration.

## 0.4.0 (2018-11-06)

- Improves AMQP re-connection handling. Switches from `pika` to `kombu`.
- Utilises common openapi client for communication with REANA-Job-Controller.
- Changes license to MIT.

## 0.3.2 (2018-09-25)

- Modifies OS related commands for CephFS compatibility.

## 0.3.1 (2018-09-07)

- Adds parameter passing to workflow steps.
- Adds user guide and getting started sections to the documentation.

## 0.3.0 (2018-08-10)

- Initial public release.
- Executes serial workflows.
- Tracks progress of workflow runs.
- Caches job results by default.
