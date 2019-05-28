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

import argparse
import json
import os

from typing import Optional, Dict, List, Text

from common.adapter import TfxComponentWrapper

from data_source import bigquery
from data_validation import schema_gen
from data_validation import statistics_gen
from data_validation import example_validator
from data_transformation import transform
from model_training import trainer

from kfp import dsl
from kfp import gcp
from kfp.compiler import compiler

import tensorflow as tf
from . import manager

from tfx.components.trainer import component as trainer_component
from tfx.components.evaluator import component as evaluator_component
from tfx.components.model_validator import component as model_validator_component
from tfx.components.pusher import component as pusher_component
from tfx.components.base import base_component
from tfx.proto import evaluator_pb2
from tfx.proto import pusher_pb2
from tfx.utils import types
from tfx.utils import channel


# TODO(muchida): Modularize other component definitions as well.


class Trainer(TfxComponentWrapper):

  def __init__(self, module_file: str, transformed_examples: str, schema: str,
               transform_output: str, training_steps: int,
               eval_training_steps: int):
    component = trainer_component.Trainer(
        module_file=module_file,
        transformed_examples=channel.Channel('ExamplesPath'),
        schema=channel.Channel('SchemaPath'),
        transform_output=channel.Channel('TransformPath'),
        train_args=trainer_pb2.TrainArgs(num_steps=training_steps),
        eval_args=trainer_pb2.EvalArgs(num_steps=eval_training_steps))

    super().__init__(
        component, {
            "transformed_examples": transformed_examples,
            "schema": schema,
            "transform_output": transform_output
        })


class Evaluator(TfxComponentWrapper):

  def __init__(self, examples: str, model_exports: str,
               feature_slicing_spec: List[List[str]]):
    slicing_spec = evaluator_pb2.FeatureSlicingSpec()
    for slice_spec in feature_slicing_spec:
      spec = slicing_spec.specs.add()
      for column in slice_spec:
        spec.column_for_slicing.append(column)

    component = evaluator_component.Evaluator(
        channel.Channel('ExamplesPath'),
        channel.Channel('ModelExportPath'),
        feature_slicing_spec=slicing_spec)

    super().__init__(component, {
        "examples": examples,
        "model_exports": model_exports,
    })


class ModelValidator(TfxComponentWrapper):

  def __init__(self, examples: str, model: str):
    component = model_validator_component.ModelValidator(
        channel.Channel('ExamplesPath'), channel.Channel('ModelExportPath'))

    super().__init__(component, {
        "examples": examples,
        "model": model,
    })


class Pusher(TfxComponentWrapper):

  def __init__(self, model_export: str, model_blessing: str,
               serving_directory: str):
    push_destination = pusher_pb2.PushDestination(
        filesystem=pusher_pb2.PushDestination.Filesystem(
            base_directory=serving_directory))

    component = pusher_component.Pusher(
        model_export=channel.Channel('ModelExportPath'),
        model_blessing=channel.Channel('ModelBlessingPath'),
        push_destination=push_destination)

    super().__init__(component, {
        "model_export": model_export,
        "model_blessing": model_blessing,
    })


_taxi_utils = "gs://muchida-tfx-oss-kfp/taxi_utils.py"


@dsl.pipeline(
    name="Chicago Taxi Cab Tip Prediction Pipeline",
    description="TODO"
)
def pipeline(
    # Pipeline-level parames
    gcp_project_id: Text=manager.PROJECT_ID,
    gcp_region: Text=manager.GCP_REGION,
    pipeline_root: Text=manager.PIPELINE_ROOT,
    pipeline_name: Text=manager.PIPELINE_NAME,
    log_root: Text=manager.LOG_ROOT,
    # ExampleGen params
    num_records: int = 10000,
    # Transform params
    transform_module: Text = 'gs://muchida-tfx-oss-kfp/taxi_utils.py',
    # Trainer params
    trainer_module: Text = 'gs://muchida-tfx-oss-kfp/taxi_utils.py',
    training_steps: Text = '10000',
    eval_steps: Text = '100',
    # Evaluator params

    # Validator params
):

  common_component_args = {
      'gcp_project_id': gcp_project_id,
      'gcp_region': gcp_region,
      'pipeline_root': pipeline_root,
      'pipeline_name': pipeline_name,
      'log_root': log_root,
  }

  training_data = bigquery(num_records=num_records, **common_component_args)

  statistics = statistics_gen(
      input_dict={'input_data': training_data.outputs['examples']},
      **common_component_args
  )

  schema = schema_gen(
      input_dict={'stats': statistics.outputs['output']},
      **common_component_args
  )

  validated_stats = example_validator(
      input_dict={
          'stats': statistics.outputs['output'],
          'schema': schema.outputs['output']
      },
      **common_component_args
  )

  transformed_data = transform(
      input_dict={
          'examples': training_data.outputs['examples'],
          'schema': schema.outputs['output'],
      },
      module_file=transform_module,
      **common_component_args,
  )

  trained_model = trainer(
      input_dict={
          'transformed_examples':
          transformed_data.outputs['transformed_examples'],
          'schema': schema.outputs['output'],
          'transform_output': transformed_data.outputs['transform_output'],
      },
      module_file=trainer_module,
      training_steps=training_steps,
      eval_steps=eval_steps,
  )

#  model_analyzer = Evaluator(
#      examples=example_gen.outputs['examples'],
#      model_exports=trainer.outputs['output'],
#      feature_slicing_spec=[['trip_start_hour']])
#
#  model_validator = ModelValidator(
#      examples=example_gen.outputs['examples'], model=trainer.outputs['output'])
#
#  pusher = Pusher(
#      model_export=trainer.outputs['output'],
#      model_blessing=model_validator.outputs['blessing'],
#      serving_directory="")


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Chicago Taxi Cab Pipeline")
  parser.add_argument("--filename", type=str)
  args = parser.parse_args()

  fname = args.filename if args.filename else __file__

  compiler.Compiler().compile(pipeline, fname + '.tar.gz')
