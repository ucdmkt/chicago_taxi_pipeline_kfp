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
