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

from google.protobuf import text_format

from common.adapter import TfxComponentWrapper
import data_source

from kfp import dsl
from kfp import gcp
from kfp.compiler import compiler

import tensorflow as tf
from . import manager

from tfx.components.example_gen.big_query_example_gen import component as big_query_example_gen_component
from tfx.components.statistics_gen import component as statistics_gen_component
from tfx.components.schema_gen import component as schema_gen_component
from tfx.components.example_validator import component as example_validator_component
from tfx.components.transform import component as transform_component
from tfx.components.trainer import component as trainer_component
from tfx.components.evaluator import component as evaluator_component
from tfx.components.model_validator import component as model_validator_component
from tfx.components.pusher import component as pusher_component
from tfx.components.base import base_component
from tfx.proto import evaluator_pb2
from tfx.proto import pusher_pb2
from tfx.proto import trainer_pb2
from tfx.utils import types
from tfx.utils import channel


# TODO(muchida): Modularize other component definitions as well.

class StatisticsGen(TfxComponentWrapper):

  def __init__(self, input_data: str):
    component = statistics_gen_component.StatisticsGen(
        channel.Channel('ExamplesPath'))
    super().__init__(component, {"input_data": input_data})


class SchemaGen(TfxComponentWrapper):

  def __init__(self, stats: str):
    component = schema_gen_component.SchemaGen(
        channel.Channel('ExampleStatisticsPath'))
    super().__init__(component, {"stats": stats})


class ExampleValidator(TfxComponentWrapper):

  def __init__(self, stats: str, schema: str):
    component = example_validator_component.ExampleValidator(
        channel.Channel('ExampleStatisticsPath'), channel.Channel('SchemaPath'))

    super().__init__(component, {"stats": stats, "schema": schema})


class Transform(TfxComponentWrapper):

  def __init__(self, input_data: str, schema: str, module_file: str):
    component = transform_component.Transform(
        input_data=channel.Channel('ExamplesPath'),
        schema=channel.Channel('SchemaPath'),
        module_file=module_file)

    super().__init__(component, {"input_data": input_data, "schema": schema})


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
    # ExampleGen parames
    num_records: int = 10000,
):

  common_component_args = {
      'gcp_project_id': gcp_project_id,
      'gcp_region': gcp_region,
      'pipeline_root': pipeline_root,
      'pipeline_name': pipeline_name,
      'log_root': log_root,
  }

  example_gen = data_source.bigquery(
      num_records=num_records, **common_component_args)

#  statistics_gen = StatisticsGen(input_data=example_gen.outputs['examples'])
#
#  infer_schema = SchemaGen(stats=statistics_gen.outputs['output'])
#
#  validate_stats = ExampleValidator(
#      stats=statistics_gen.outputs['output'],
#      schema=infer_schema.outputs['output'])
#
#  transform = Transform(
#      input_data=example_gen.outputs['examples'],
#      schema=infer_schema.outputs['output'],
#      module_file=_taxi_utils)
#
#  trainer = Trainer(
#      module_file=_taxi_utils,
#      transformed_examples=transform.outputs['transformed_examples'],
#      schema=infer_schema.outputs['output'],
#      transform_output=transform.outputs['transform_output'],
#      training_steps=10000,
#      eval_training_steps=5000)
#
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
