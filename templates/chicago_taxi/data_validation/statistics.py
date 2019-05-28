"""Defines skeleton of StatisticsGen component."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from common.adapter import TfxComponentWrapper

from tfx.components.statistics_gen.component import StatisticsGen
from tfx.utils import channel


def statistics_gen(input_dict, **kwargs) -> TfxComponentWrapper:

  class _StatisticsGen(TfxComponentWrapper):

    def __init__(self):
      component = StatisticsGen(channel.Channel('ExamplesPath'))
      super().__init__(component, input_dict=input_dict, **kwargs)

  return _StatisticsGen()
