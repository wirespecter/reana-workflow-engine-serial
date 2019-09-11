.. _userguide:

User Guide
==========

Writing a ``reana.yaml`` file
-----------------------------

Let's assuming you have created an analysis that is condensed in a single bash
script, ``myanalysis.sh``. Your workflow consists of a single command:

.. code-block:: console

    $ bash myanalysis.sh

So the single command in ``yaml`` list format is:

.. code-block:: yaml

    commands:
    - bash myanalysis.sh

To be able to run a command you need to have the tool for it available
in your environment, i.e. the docker image. So for this example you need
a docker image with bash installed, like the official bash image
``library/bash``. You can add it in the following way:

.. code-block:: yaml

    - environment: 'library/bash'
      commands:
      - bash myanalysis.sh

The workflow step definition is now complete:

.. code-block:: yaml

    steps:
      - environment: 'library/bash'
        commands:
        - bash myanalysis.sh

You specify that the workflow is of serial type:

.. code-block:: yaml

    workflow:
      type: serial
      specification:
        steps:
          - environment: 'library/bash'
            commands:
            - bash myanalysis.sh

and you write in the inputs section that you are using ``myanalysis.sh``
as an input file, so the finished ``reana.yaml`` is the following:

.. code-block:: yaml

    inputs:
      files:
        - myanalysis.sh
    workflow:
      type: serial
      specification:
        steps:
          - environment: 'library/bash'
            commands:
            - bash myanalysis.sh

This analysis is ready to be run on REANA, using the
REANA `Client <https://reana-client.readthedocs.io/en/latest/gettingstarted.html#run-example-analysis>`_.

Result Caching
--------------

REANA Workflow Engine Serial will cache the result of each step by default,
for faster execution of subsequent workflow runs. This can lead to confusion in
case the workflow has steps that are expected to not have deterministic results,
such as e.g. a generation of random points in a cartesian plane. In this case,
the workflow should be started with ``CACHE=off`` parameter.

To read more on how to start a workflow with specific parameters, please refer to the
following section in the REANA `Client <https://reana-client.readthedocs.io/en/latest/cliapi.html#reana-client-start>`__
documentation.

Partial workflow execution
--------------------------

Typically your workflow is composed of several steps, for example *gendata* and
*fitdata*. You can name them like this:

.. code-block:: yaml

    workflow:
      type: serial
      specification:
        steps:
          - name: gendata
            environment: 'reanahub/reana-env-root6'
            commands:
            - mkdir -p results
            - root -b -q 'code/gendata.C(${events},"${data}")' | tee gendata.log
          - name: fitdata
            environment: 'reanahub/reana-env-root6'
            commands:
            - root -b -q 'code/fitdata.C("${data}","${plot}")' | tee fitdata.log

If you would like to run the serial workflow only up to a certain step, you can
specify operational option TARGET when starting the workflow:

.. code-block:: console

    $ reana-client start -o TARGET=gendata

which will run only the generation data step.

This can be used for debugging parts of workflows faster.
