import unittest
import analytics
import pandas as pd
from analytics.models import column_format


class ColumnFormatTest(unittest.TestCase):
    def setUp(self):
        self.app = analytics.create_app('test')

    def test_should_change_column_scale_according_to_scale(self):
        settings = {
            'Very bad': 1,
            'Bad': 1,
            'Fair': 2,
            'Good': 3,
            'Very good': 3,
            'Default': 0
        }
        ds = pd.DataFrame([["Very bad"], ["Bad"], ["Fair"]], columns=['Rating'])
        ds['Rating'] = analytics.models.column_format.change_column_scale(ds['Rating'], settings)
        self.assertEqual(ds['Rating'].tolist(), [1, 1, 2])

    def test_should_throw_exception_if_default_value_is_missing_in_settings(self):
        settings = {
            'Very bad': 1,
            'Bad': 1,
            'Fair': 2,
            'Good': 3,
            'Very good': 3,
        }
        ds = pd.DataFrame([["Very bad"], ["Bad"], ["Fair"]], columns=['Rating'])
        self.assertRaises(Exception, analytics.models.column_format.change_column_scale, ds['Rating'], settings)

    def test_should_set_default_value_when_scale_column_and_value_absent_in_settings(self):
        settings = {
            'Very bad': 1,
            'Bad': 1,
            'Fair': 2,
            'Good': 3,
            'Very good': 3,
            'Default': 0
        }
        ds = pd.DataFrame([["Very bad"], ["Bad"], ["Excellent"]], columns=['Rating'])
        ds['Rating'] = analytics.models.column_format.change_column_scale(ds['Rating'], settings)
        self.assertEqual(ds['Rating'].tolist(), [1, 1, 0])

    if __name__ == '__main__':
        unittest.main()