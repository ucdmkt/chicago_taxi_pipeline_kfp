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

"""Defines skeleton of ExampleGen component."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import app
from absl import flags

from tfx.components.example_gen.big_query_example_gen.component import BigQueryExampleGen
from tfx.proto import example_gen_pb2

from common.adapter import TfxComponentWrapper

from typing import Optional, Dict, Text


def bigquery(num_records: int, **kwargs) -> TfxComponentWrapper:
  """Defines data generation from BigQuery."""

  ### NOTE: This is vulnerable to SQL Injection.
  QUERY_TMPL = """
      SELECT
        pickup_community_area,
        fare,
        EXTRACT(MONTH FROM trip_start_timestamp) AS trip_start_month,
        EXTRACT(HOUR FROM trip_start_timestamp) AS trip_start_hour,
        EXTRACT(DAYOFWEEK FROM trip_start_timestamp) AS trip_start_day,
        UNIX_SECONDS(trip_start_timestamp) AS trip_start_timestamp,
        pickup_latitude,
        pickup_longitude,
        dropoff_latitude,
        dropoff_longitude,
        trip_miles,
        pickup_census_tract,
        dropoff_census_tract,
        payment_type,
        company,
        trip_seconds,
        dropoff_community_area,
        tips
      FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
      LIMIT {}
  """

  class _BigQueryExampleGen(TfxComponentWrapper):

    def __init__(self):
      component = BigQueryExampleGen(QUERY_TMPL.format(num_records))
      super().__init__(component, **kwargs)

  return _BigQueryExampleGen()
