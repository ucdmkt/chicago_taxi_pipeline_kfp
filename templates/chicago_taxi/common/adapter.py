# Copyright 2019 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This code defines adapter code for Components."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os

from typing import Optional, Dict, List

from kfp import dsl
from kfp import gcp
from kfp.compiler import compiler
from kubernetes import client as k8s_client

from tfx.components.base import base_component
from tfx.utils import types

_IMAGE = 'gcr.io/caipe-dev/tensorflow/tfx-muchida:latest'

_COMMAND = [
    'python',
    '/tfx-src/tfx/orchestration/kubeflow/container_entrypoint.py',
]

class TfxComponentWrapper(dsl.ContainerOp):

  def __init__(
      self,
      component: base_component.BaseComponent,
      input_dict: Optional[Dict] = None,
      **kwargs):

    self.component = component

    executor_class_path = '.'.join(
        [component.executor.__module__, component.executor.__name__])

    output_dict = dict(
        (k, v.get()) for k, v in component.outputs.get_all().items())

    outputs = output_dict.keys()
    file_outputs = {
        output: '/output/ml_metadata/{}'.format(output) for output in outputs
    }

    exec_properties = component.exec_properties

    # extra exec properties that is needed for KubeflowExecutorWrapper.
    exec_properties['output_dir'] = os.path.join(
        str(kwargs.get('pipeline_root')), str(kwargs.get('pipeline_name')))
    exec_properties['beam_pipeline_args'] = [
        '--runner=DataflowRunner',
        '--experiments=shuffle_mode=auto',
        '--project=' + str(kwargs.get('gcp_project_id')),
        '--temp_location=' + os.path.join(
            str(kwargs.get('pipeline_root')), 'tmp'),
        '--region=' + str(kwargs.get('gcp_region')),
    ]

    arguments = [
        '--exec_properties',
        json.dumps(component.exec_properties),
        '--outputs',
        types.jsonify_tfx_type_dict(output_dict),
        '--executor_class_path',
        executor_class_path,
        component.component_name,
    ]

    if input_dict:
      for k, v in input_dict.items():
        if isinstance(v, float) or isinstance(v, int):
          v = str(v)
        arguments.append('--{}'.format(k))
        arguments.append(v)

    super().__init__(
        name=component.component_name,
        # TODO(muchida): each component could take different child image,
        # while maintaining the common entry point. It is nice because it could
        # cleanly embeds user code and/or configuration.
        image=_IMAGE,
        command=_COMMAND,
        arguments=arguments,
        file_outputs=file_outputs,
    )
    self.apply(gcp.use_gcp_secret('user-gcp-sa'))

    field_path = "metadata.labels['workflows.argoproj.io/workflow']"
    self.add_env_variable(
        k8s_client.V1EnvVar(
            name='WORKFLOW_ID',
            value_from=k8s_client.V1EnvVarSource(
                field_ref=k8s_client.V1ObjectFieldSelector(
                    field_path=field_path))))
