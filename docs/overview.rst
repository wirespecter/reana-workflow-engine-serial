.. _overview:

Overview
========

The serial engine can be used to run `sequential workflows <http://www.workflowpatterns.com/patterns/control/basic/wcp1.php>`_.

.. code-block:: console

     inputs
        |
        V
    +-------+
    | step1 |   ... in environment E1
    +-------+
        |
        V
    +-------+
    | step2 |   ... in environment E2
    +-------+
        |
        V
       ...
        |
        V
    +-------+
    | stepN |   ... in environment EN
    +-------+
        |
        V
     outputs

An example of a real sequential workflow can be seen in the
`reana-demo-root6-roofit <https://github.com/reanahub/reana-demo-root6-roofit>`_ repository.

The workflow as in all workflow engine is defined in a `reana.yaml <https://github.com/reanahub/reana-demo-root6-roofit/blob/master/reana.yaml>`_
file. Essentially, for a serial workflow it consists of the `inputs` and
`workflow` sections. The `inputs` define any input files that may used in the
steps, and the `workflow` defines the actual steps with their environment, i.e. docker images,
and their commands. Each step can run in a different environment.

Writing a ``reana.yaml`` file
-------------------------

Assuming an analysis has been condensed to a single bash script, 
``myanalysis.sh``, our workflow consists of a single command

.. code-block:: console

    $ bash myanalysis.sh

So the single command in yaml list format is:

.. code-block:: yaml

    commands:
    - bash myanalysis.sh

To be able to run a command we need to have the tool for it available
in our environment, i.e. the docker image. So for this example we need
a docker image with bash installed, like the official bash image ``library/bash``.
We add it in the following way:

.. code-block:: yaml

    - environment: 'library/bash'
      commands:
      - bash myanalysis.sh

So the workflow step definition is complete:

.. code-block:: yaml

    steps:
      - environment: 'library/bash'
        commands:
        - bash myanalysis.sh

We specify that the workflow is of serial type:

.. code-block:: yaml

    workflow:
      type: serial
      specification:
        steps:
          - environment: 'library/bash'
            commands:
            - bash myanalysis.sh

and finally we write in the inputs section that we are using ``myanalysis.sh``
as an input file, so the finished reana.yaml is the following:

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
`reana-client <http://reana-client.readthedocs.io/en/latest/gettingstarted.html#run-example-analysis>`_.
