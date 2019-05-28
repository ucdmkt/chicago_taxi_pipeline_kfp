"""Defines skeleton of ModelValidator component."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from common.adapter import TfxComponentWrapper

from tfx.components.model_validator.component import ModelValidator
from tfx.proto import evaluator_pb2
from tfx.utils import channel


def model_validator(input_dict, **kwargs) -> TfxComponentWrapper:

  class _ModelValidator(TfxComponentWrapper):

    def __init__(self):
      component = ModelValidator(channel.Channel('ExamplesPath'),
                                 channel.Channel('ModelExportPath'))

      super().__init__(component, input_dict, **kwargs)

  return _ModelValidator()
