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

"""Defines skeleton of SchemaGen component."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from common.adapter import TfxComponentWrapper

from tfx.components.schema_gen.component import SchemaGen
from tfx.utils import channel


def schema_gen(statistics, **kwargs) -> TfxComponentWrapper:

  class _SchemaGen(TfxComponentWrapper):

    def __init__(self):
      component = SchemaGen(channel.Channel('ExampleStatisticsPath'))
      super().__init__(
          component, {'stats': statistics.outputs['output']}, **kwargs)

  return _SchemaGen()
