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

"""Defines skeleton of Pusher component."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from common.adapter import TfxComponentWrapper

from tfx.components.pusher.component import Pusher
from tfx.proto import pusher_pb2
from tfx.utils import channel


# TODO(muchida): Add Cloud AI Platform pusher.

def savedmodel_pusher(
    trained_model,
    validated_model,
    serving_directory,
    **kwargs) -> TfxComponentWrapper:

  class _Pusher(TfxComponentWrapper):

    def __init__(self):

      push_destination = pusher_pb2.PushDestination(
          filesystem=pusher_pb2.PushDestination.Filesystem(
              base_directory=str(serving_directory)
          ),
      )

      component = Pusher(
          model_export=channel.Channel('ModelExportPath'),
          model_blessing=channel.Channel('ModelBlessingPath'),
          push_destination=push_destination
      )
      super().__init__(
          component,
          {
              "model_export": trained_model.outputs['output'],
              "model_blessing": validated_model.outputs['blessing'],
          },
          **kwargs)

  return _Pusher()
