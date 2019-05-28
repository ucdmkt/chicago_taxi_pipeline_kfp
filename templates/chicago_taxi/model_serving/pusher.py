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
    input_dict,
    serving_directory,
    **kwargs) -> TfxComponentWrapper:

  class _Pusher(TfxComponentWrapper):

    def __init__(self):

      push_destination = pusher_pb2.PushDestination.Filesystem(
          base_directory=str(serving_directory),
      )

      component = Pusher(
          model_export=channel.Channel('ModelExportPath'),
          model_blessing=channel.Channel('ModelBlessingPath'),
          push_destination=push_destination
      )
      super().__init__(component, input_dict, **kwargs)

  return _Pusher()
