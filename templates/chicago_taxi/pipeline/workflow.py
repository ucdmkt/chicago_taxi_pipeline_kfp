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
import tensorflow as tf
from typing import Optional, Dict, List, Text

from . import manager

# Following imports define TFX components for this pipeline.
from data_source import bigquery
from data_validation import schema_gen
from data_validation import statistics_gen
from data_validation import example_validator
from data_transformation import transform
from model_training import trainer
from model_evaluation import evaluator
from model_validation import model_validator
from model_serving import savedmodel_pusher

from kfp import dsl
from kfp import gcp
from kfp.compiler import compiler

from tfx.components.pusher import component as pusher_component
from tfx.proto import evaluator_pb2
from tfx.proto import pusher_pb2
from tfx.utils import types
from tfx.utils import channel


@dsl.pipeline(
    name="This is a skeleton template pipeline.",
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
    num_records: int = 10000,        # This works.
    # Transform params
    transform_module: Text = 'gs://muchida-tfx-oss-kfp/taxi_utils.py',
    # Trainer params
    trainer_module: Text = 'gs://muchida-tfx-oss-kfp/taxi_utils.py',
    training_steps: int = 10000,     # This doesn't work.
    eval_steps: int = 100,           # This doesn't work.
    # Evaluator params
    columns_for_slicing: Text = '',  # This doesn't work.
    # Pusher params
    serving_directory: Text = ''     # This works.
):

  common_component_args = {
      'gcp_project_id': gcp_project_id,
      'gcp_region': gcp_region,
      'pipeline_root': pipeline_root,
      'pipeline_name': pipeline_name,
      'log_root': log_root,
  }

  training_data = bigquery(num_records=num_records, **common_component_args)

  statistics = statistics_gen(training_data=training_data,
                              **common_component_args)

  # TODO: Add control flow to retrieve schema from pipeline itself, if exists.

  schema = schema_gen(statistics=statistics,
                      **common_component_args)

  validated_stats = example_validator(statistics=statistics,
                                      schema=schema,
                                      **common_component_args)

  transformed_data = transform(training_data=training_data,
                               schema=schema,
                               module_file=transform_module,
                               **common_component_args)

  trained_model = trainer(transformed_data=transformed_data,
                          schema=schema,
                          module_file=trainer_module,
                          training_steps=training_steps,
                          eval_steps=eval_steps,
                          **common_component_args)

  model_analysis = evaluator(
      training_data,
      trained_model,
      # TODO(muchida): Figure out how to inject PipelineParams to this.
      columns_for_slicing=[
          ['trip_start_hour', 'payment_type'],
          ['company']
      ],
      **common_component_args
  )

  validated_model = model_validator(training_data,
                                    trained_model,
                                    **common_component_args)

  pushed_model = savedmodel_pusher(trained_model,
                                   validated_model,
                                   serving_directory=serving_directory,
                                   **common_component_args)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Chicago Taxi Cab Pipeline")
  parser.add_argument("--filename", type=str)
  args = parser.parse_args()

  fname = args.filename if args.filename else __file__

  compiler.Compiler().compile(pipeline, fname + '.tar.gz')
