"""Defines skeleton of SchemaGen component."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from common.adapter import TfxComponentWrapper

from tfx.components.schema_gen.component import SchemaGen
from tfx.utils import channel


def schema_gen(input_dict, **kwargs) -> TfxComponentWrapper:

  class _SchemaGen(TfxComponentWrapper):

    def __init__(self):
      component = SchemaGen(channel.Channel('ExampleStatisticsPath'))
      super().__init__(component, input_dict, **kwargs)

  return _SchemaGen()
