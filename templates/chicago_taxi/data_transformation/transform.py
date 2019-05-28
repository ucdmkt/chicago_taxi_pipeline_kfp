"""Defines skeleton of Transform component."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from common.adapter import TfxComponentWrapper

from tfx.components.transform.component import Transform
from tfx.utils import channel


def transform(input_dict, module_file,  **kwargs) -> TfxComponentWrapper:

  class _Transform(TfxComponentWrapper):

    def __init__(self):
      component = Transform(
          channel.Channel('ExamplesPath'),
          channel.Channel('SchemaPath'),
          module_file=str(module_file),
      )
      super().__init__(component, input_dict, **kwargs)

  return _Transform()
