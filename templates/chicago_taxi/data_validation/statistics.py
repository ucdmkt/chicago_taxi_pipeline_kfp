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

"""Defines skeleton of StatisticsGen component."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from common.adapter import TfxComponentWrapper

from tfx.components.statistics_gen.component import StatisticsGen
from tfx.utils import channel


def statistics_gen(training_data, **kwargs) -> TfxComponentWrapper:

  class _StatisticsGen(TfxComponentWrapper):

    def __init__(self):
      component = StatisticsGen(channel.Channel('ExamplesPath'))
      super().__init__(
          component, {'input_data': training_data.outputs['examples']}, **kwargs)

  return _StatisticsGen()
