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

"""Defines skeleton of Trainer component."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from common.adapter import TfxComponentWrapper

from tfx.components.trainer.component import Trainer
from tfx.proto import trainer_pb2
from tfx.utils import channel


def trainer(transformed_data,
            schema,
            module_file,
            training_steps: int,
            eval_steps: int,
            **kwargs) -> TfxComponentWrapper:

  class _Trainer(TfxComponentWrapper):

    def __init__(self):
      component = Trainer(
          module_file=str(module_file),
          transformed_examples=channel.Channel('ExamplesPath'),
          schema=channel.Channel('SchemaPath'),
          transform_output=channel.Channel('TransformPath'),
          #
          # TODO(muchida): Figure out how to inject integer PipelineParam.
          train_args=trainer_pb2.TrainArgs(
              #num_steps=training_steps
              num_steps=10000
          ),
          eval_args=trainer_pb2.EvalArgs(
              #num_steps=eval_steps
              num_steps=1000
          ),
      )
      super().__init__(
          component,
          {
              'transformed_examples':
              transformed_data.outputs['transformed_examples'],
              'schema': schema.outputs['output'],
              'transform_output': transformed_data.outputs['transform_output'],
          },
          **kwargs)

  return _Trainer()
