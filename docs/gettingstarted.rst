.. _gettingstarted:

Getting Started
===============

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
file. Essentially, for a serial workflow it consists of the ``inputs`` and
``workflow`` sections. The ``inputs`` define any input files that may used in the
steps, and the ``workflow`` defines the actual steps with their environment, i.e. docker images,
and their commands. Each step can run in a different environment.

Currently, the list of commands are executed in a bash shell.
A quick guide on how to structure a reana.yaml file can be found in the :ref:`userguide`.
