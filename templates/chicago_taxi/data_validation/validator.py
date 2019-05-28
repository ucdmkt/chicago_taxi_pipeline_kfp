"""Defines skeleton of ExampleValidator component."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from common.adapter import TfxComponentWrapper

from tfx.components.example_validator.component import ExampleValidator
from tfx.utils import channel


def example_validator(input_dict, **kwargs) -> TfxComponentWrapper:

  class _ExampleValidator(TfxComponentWrapper):

    def __init__(self):
      component = ExampleValidator(
          channel.Channel('ExampleStatisticsPath'),
          channel.Channel('SchemaPath'))
      super().__init__(component, input_dict, **kwargs)

  return _ExampleValidator()
