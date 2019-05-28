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
