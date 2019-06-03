"""Tests for features."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from . import features


class FeaturesTest(tf.test.TestCase):

  def test_transformed_name(self):
    key = 'fare'
    xfm_key = features.transformed_name(key)
    self.assertEqual(xfm_key, 'fare_xf')

  def test_transformed_names(self):
    keys = ['fare', 'tips']
    xfm_keys = features.transformed_names(keys)
    self.assertAllEqual(xfm_keys, ['fare_xf', 'tips_xf'])


if __name__ == '__main__':
  tf.test.main()
