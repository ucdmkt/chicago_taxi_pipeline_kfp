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

"""Defines skeleton of Transform component."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from common import features
from common.adapter import TfxComponentWrapper

import tensorflow as tf
import tensorflow_transform as tft

from tfx.components.transform.component import Transform
from tfx.utils import channel


# TFX Transform component calls in to this function.
def preprocessing_fn(inputs):
  """tf.transform's callback function for preprocessing inputs.

  Args:
    inputs: map from feature keys to raw not-yet-transformed features.

  Returns:
    Map from string feature key to transformed feature operations.
  """
  outputs = {}
  for key in features.DENSE_FLOAT_FEATURE_KEYS:
    # Preserve this feature as a dense float, setting nan's to the mean.
    outputs[_transformed_name(key)] = tft.scale_to_z_score(
        features.fill_in_missing(inputs[key]))

  for key in features.VOCAB_FEATURE_KEYS:
    # Build a vocabulary for this feature.
    outputs[features.transformed_name(key)] = tft.compute_and_apply_vocabulary(
        features.fill_in_missing(inputs[key]),
        top_k=features.VOCAB_SIZE,
        num_oov_buckets=features.OOV_SIZE)

  for key in features.BUCKET_FEATURE_KEYS:
    outputs[features.transformed_name(key)] = tft.bucketize(
        features.fill_in_missing(inputs[key]), features.FEATURE_BUCKET_COUNT)

  for key in _CATEGORICAL_FEATURE_KEYS:
    outputs[
        features.transformed_name(key)] = features.fill_in_missing(inputs[key])

  # Was this passenger a big tipper?
  taxi_fare = features.fill_in_missing(inputs[features.FARE_KEY])
  tips = features.fill_in_missing(inputs[features.LABEL_KEY])
  outputs[features.transformed_name(features.LABEL_KEY)] = tf.where(
      tf.is_nan(taxi_fare),
      tf.cast(tf.zeros_like(taxi_fare), tf.int64),
      # Test if the tip was > 20% of the fare.
      tf.cast(
          tf.greater(tips, tf.multiply(taxi_fare, tf.constant(0.2))), tf.int64))

  return outputs

#####

def transform(training_data,
              schema,
              **kwargs) -> TfxComponentWrapper:
  """Factory function of ContainerOp for Transform."""

  class _Transform(TfxComponentWrapper):

    def __init__(self):
      component = Transform(
          # Find user code implementation from inside of the container.
          module_file="/pipeline-srcs/model_training/taxi_utils.py",
          # TODO: When TFX binary enables Py3 runtime, retire taxi_utils.py.
          #module_file="/pipeline-srcs/data_transfomration/tranform.py",
          input_data=channel.Channel('ExamplesPath'),
          schema=channel.Channel('SchemaPath'),
      )
      super().__init__(
          component,
          {
              'input_data': training_data.outputs['examples'],
              'schema': schema.outputs['output'],
          },
          **kwargs)

  return _Transform()
