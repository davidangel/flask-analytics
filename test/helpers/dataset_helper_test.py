import unittest
import analytics
import pandas as pd
import numpy as np
import datetime
from unittest.mock import patch

class DatasetHelperTest(unittest.TestCase):
    def setUp(self):
        self.app = analytics.create_app('test')

    def test_should_get_entries_after(self):
        df = pd.DataFrame([["2017-05-07"], ["2017-05-08"], ["2017-05-09"]], columns=['EndDate'])
        filter_date = datetime.datetime(2017, 5, 8).strftime('%Y-%m-%d')
        filtered_ds = analytics.helpers.dataset_helper.get_entries_after(df, filter_date, 'EndDate')
        self.assertEquals(len(filtered_ds), 2)

    def test_should_throw_exception_if_column_does_not_exist_when_getting_entries_after(self):
        df = pd.DataFrame([["2017-05-07"], ["2017-05-08"], ["2017-05-09"]], columns=['ColumnName'])
        filter_date = datetime.datetime(2017, 5, 8).strftime('%Y-%m-%d')
        with self.assertRaises(Exception) as error:
            analytics.helpers.dataset_helper.get_entries_after(df, filter_date, 'EndDate')
        self.assertEqual(str(error.exception), 'Column EndDate is missing in the dataset')

    def test_should_merge_datasets_vertically(self):
        df1 = pd.DataFrame([['c', 3, 'cat'], ['d', 4, 'dog']], columns=['letter', 'number', 'animal'])
        df2 = pd.DataFrame([['a', 1], ['b', 2]], columns=['letter', 'number'])
        merged = analytics.helpers.dataset_helper.merge_datasets_vertically(df1, df2)
        self.assertEquals(len(merged), 4)

    def test_should_rename_columns(self):
        df = pd.DataFrame([["2017-05-07"], ["2017-05-08"], ["2017-05-09"]], columns=['EndDate'])
        renamed_dataset = analytics.helpers.dataset_helper.rename_columns(df, {'EndDate': 'NewEndDate'})
        self.assertIn('NewEndDate', renamed_dataset.columns.values)
        self.assertNotIn('EndDate', renamed_dataset.columns.values)

    def test_should_filter_requested_columns(self):
        df = pd.DataFrame([["2017-05-07", 'Type1', 'True'], ["2017-05-08", 'Type2', 'False']], columns=['Date', 'Type', 'Exclude'])
        filtered_dataset = analytics.helpers.dataset_helper.filter_columns(df, ['Date', 'Type'])
        self.assertIn('Date', filtered_dataset.columns.values)
        self.assertIn('Type', filtered_dataset.columns.values)
        self.assertNotIn('Exclude', filtered_dataset.columns.values)

    def test_should_throw_exception_if_filtered_columns_are_missing_in_dataset(self):
        df = pd.DataFrame([["2017-05-07", 'Type1', 'True'], ["2017-05-08", 'Type2', 'False']], columns=['Date', 'Type', 'Exclude'])
        with self.assertRaises(Exception) as error:
            analytics.helpers.dataset_helper.filter_columns(df, ['Date', 'NotColumn'])
        self.assertEqual(str(error.exception), 'Column(s) are missing in the dataset')

    def test_should_add_columns_if_not_exist(self):
        columns = ['Date', 'Type', 'Exclude']
        df = pd.DataFrame([["2017-05-07", 'Type1'], ["2017-05-08", 'Type2']], columns=['Date', 'Type'])
        analytics.helpers.dataset_helper.add_columns_if_not_exist(df, columns)
        self.assertIn('Date', df.columns.values)
        self.assertIn('Type', df.columns.values)
        self.assertIn('Exclude', df.columns.values)

    def test_should_add_column_by_merging_two_others_by_order(self):
        df = pd.DataFrame([[1, None], [None, 3], [5, None]], columns=['WebsiteRating', 'ProductRating'])
        df['OverallRating'] = analytics.helpers.dataset_helper.merge_columns(df, ['WebsiteRating', 'ProductRating'])
        self.assertEqual(df['OverallRating'].tolist(), [1, 3, 5])

    def test_should_add_column_by_merging_three_others_by_order(self):
        df = pd.DataFrame([[1, None, None], [None, 3, None], [None, None, 5]], columns=['WebsiteRating', 'ProductRating', 'ServiceRating'])
        df['OverallRating'] = analytics.helpers.dataset_helper.merge_columns(df, ['WebsiteRating', 'ProductRating', 'ServiceRating'])
        self.assertEqual(df['OverallRating'].tolist(), [1, 3, 5])

    def test_trim_heading_rows_if_greater_then_dataset_length(self):
        rows_number = 2
        ds = pd.DataFrame([["2017-05-07"], ["2017-05-08"], ["2017-05-09"]], columns=['EndDate'])
        trimmed_ds = analytics.helpers.dataset_helper.trim_heading_rows(ds, rows_number)
        self.assertEqual(len(trimmed_ds), 1)

    def test_should_raise_exception_if_amount_of_rows_to_remove_greater_dataset_lenth(self):
        rows_number = 4
        ds = pd.DataFrame([["2017-05-07"], ["2017-05-08"], ["2017-05-09"]], columns=['EndDate'])
        self.assertRaises(Exception, analytics.helpers.dataset_helper.trim_heading_rows, ds, rows_number)

    def test_should_drop_rows_with_missing_data(self):
        ds = pd.DataFrame([["2017-05-07"], [None], ["2017-05-09"]], columns=['EndDate'])
        new_ds = analytics.helpers.dataset_helper.drop_rows_with_missing_data(ds)
        self.assertEqual(len(new_ds), 2)

    def test_should_count_values_by_grouping(self):
        ds = pd.DataFrame([["2015-07-01", True],
                           ["2015-07-01", False],
                           ["2015-07-02", True],
                           ["2015-07-03", False]], columns=['Date', 'Finished'])

        grouped_ds = analytics.helpers.\
            dataset_helper.\
            count_values_by_grouping(ds, group_by='Date', value_column='Total')
        expected_ds = pd.DataFrame([["2015-07-01", 2], ["2015-07-02", 1], ["2015-07-03", 1]],
                                   columns=['Date', 'Total'])
        self.assertTrue(grouped_ds.equals(expected_ds))

    def test_should_merge_datasets_horizontally(self):
        ds1 = pd.DataFrame([["2015-07-01", 1],
                           ["2015-07-02", 1]], columns=['Date', 'Finished'])

        ds2 = pd.DataFrame([["2015-07-01", 1],
                            ["2015-07-02", 2],
                            ["2015-07-03", 3]], columns=['Date', 'Total'])

        merged_ds = analytics.helpers\
            .dataset_helper.\
            merge_datasets_horizontally(ds1, ds2, column='Date', how='outer',
                                        na_values={'Total': 0, 'Finished': 0})

        expected_ds = pd.DataFrame([["2015-07-01", 1.0, 1],
                                    ["2015-07-02", 1.0, 2],
                                    ["2015-07-03", 0.0, 3]], columns=['Date', 'Finished', 'Total'])
        self.assertTrue(merged_ds.equals(expected_ds))

    def test_should_count_values_grouped_by_column(self):
        ds = pd.DataFrame([["2015-07-01", True],
                           ["2015-07-01", False],
                           ["2015-07-02", True],
                           ["2015-07-03", False]], columns=['Date', 'Finished'])
        compare_ds = pd.DataFrame([["2015-07-01", 1, 2], ["2015-07-02", 1, 1], ["2015-07-03", 0, 1]],
                                  columns=['Date', 'Finished', 'Total'])
        ds_result = analytics.helpers.dataset_helper\
            .count_values_grouped_by_column(ds, group_by='Date',
                                            value_column='Finished',
                                            count_values=True,
                                            count_proportion=False)
        self.assertTrue(ds_result.equals(compare_ds))

    def test_should_include_proportion_if_requested(self):
        ds = pd.DataFrame([["2015-07-01", True],
                           ["2015-07-01", False],
                           ["2015-07-02", True],
                           ["2015-07-03", False]], columns=['Date', 'Finished'])
        compare_ds = pd.DataFrame([["2015-07-01", 1, 2, 50.0], ["2015-07-02", 1, 1, 100.0], ["2015-07-03", 0, 1, 0.0]],
                                  columns=['Date', 'Finished', 'Total', 'Proportion'])
        ds_result = analytics.helpers.dataset_helper\
            .count_values_grouped_by_column(ds, group_by='Date',
                                            value_column='Finished',
                                            count_values=True,
                                            count_proportion=True)
        self.assertTrue(ds_result.equals(compare_ds))

    def test_should_return_dataset_column_types(self):
        ds = pd.DataFrame([["2015-07-01", True, 2.0, 6]], columns=['StringC', 'BooleanC', 'FloatC', 'IntegerC'])
        type_lists = analytics.helpers.dataset_helper.get_dataset_column_types(ds)
        self.assertEqual({'StringC': np.dtype('O'),
                          'BooleanC': np.dtype('bool'),
                          'FloatC': np.dtype('float64'),
                          'IntegerC': np.dtype('int64')}, type_lists)

    @patch('analytics.helpers.dataset_helper.column_types', {'BooleanC': 'bool'})
    def test_should_set_column_types(self):
        ds = pd.DataFrame([['True'], ['False'], ['False']], columns=['BooleanC'])
        ds = analytics.helpers.dataset_helper.set_column_types(ds, ['BooleanC'])
        self.assertEqual(ds['BooleanC'].dtype, np.dtype('bool'))
        self.assertEqual(ds['BooleanC'].tolist(), [True, False, False])

    @patch('analytics.helpers.dataset_helper.column_types', {})
    def test_should_throw_exception_if_column_is_missing_from_types_dict(self):
        ds = pd.DataFrame([['True'], ['False'], ['False']], columns=['BooleanC'])
        with self.assertRaises(Exception) as error:
            analytics.helpers.dataset_helper.set_column_types(ds, ['BooleanC'])
        self.assertEqual(str(error.exception), 'Column(s) are missing from types dictionary')

    def test_should_convert_column_values(self):
        ds = pd.DataFrame([['True'], ['False'], ['False'], [True], ['Yes'], ['No']], columns=['BooleanC'])
        bool_conversion = {'True': True, 'False': False, True: True, False: False, 'Yes': True, 'No': False}

        ds['BooleanC'] = analytics.helpers.dataset_helper.\
            convert_column_values(ds['BooleanC'], bool_conversion)
        expected_values = [True, False, False, True, True, False]
        self.assertEqual(ds['BooleanC'].tolist(), expected_values)

    if __name__ == '__main__':
        unittest.main()