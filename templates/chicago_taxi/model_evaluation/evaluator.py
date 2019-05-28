"""Defines skeleton of Evaluator component."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from common.adapter import TfxComponentWrapper

from tfx.components.evaluator.component import Evaluator
from tfx.proto import evaluator_pb2
from tfx.utils import channel


def evaluator(input_dict,
              columns_for_slicing,
              **kwargs) -> TfxComponentWrapper:

  class _Evaluator(TfxComponentWrapper):

    def __init__(self):

      slicing_spec = evaluator_pb2.FeatureSlicingSpec()
      for column_for_slice in columns_for_slicing:
        spec = slicing_spec.specs.add()
        for column in column_for_slice:
          spec.column_for_slicing.append(column)

      component = Evaluator(channel.Channel('ExamplesPath'),
                            channel.Channel('ModelExportPath'),
                            feature_slicing_spec=slicing_spec)

      super().__init__(component, input_dict, **kwargs)

  return _Evaluator()
