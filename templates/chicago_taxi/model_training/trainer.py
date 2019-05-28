"""Defines skeleton of Trainer component."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from common.adapter import TfxComponentWrapper

from tfx.components.trainer.component import Trainer
from tfx.proto import trainer_pb2
from tfx.utils import channel


def trainer(input_dict,
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
          # TODO(muchida): Figure out how to inject PipelineParam.
          train_args=trainer_pb2.TrainArgs(
              #num_steps=training_steps
              num_steps=10000
          ),
          eval_args=trainer_pb2.EvalArgs(
              #num_steps=eval_steps
              num_steps=1000
          ),
      )
      super().__init__(component, input_dict, **kwargs)

  return _Trainer()
