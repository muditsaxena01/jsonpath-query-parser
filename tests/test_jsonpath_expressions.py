import unittest

from jsonpath_query_parser import JSONPathParser


class TestJSONPathExpression(unittest.TestCase):
    '''
    Test case for jsonpath query parser
    '''

    def setUp(self):
        self.source_object = {
            "department": "Management",
            "designation": "VP",
            "dob": "1963-03-05T23:11:03.000-06:30",
            "email": "dleethemu@hao123.com",
            "employeeId": 31,
            "exitDate": "2017-08-31T21:25:36.680-06:30",
            "gender": "Female",
            "isActive": False,
            "joiningDate": "2017-01-07T04:37:40.553-06:30",
            "managerId": 1,
            "name": {
                'first': "Deborah",
                'last': "Leethem"
            },
            "salary": 145848.27,
            "attendanceData": [
                {
                    "locationId": 1,
                    "checkedInAt": "2017-01-08T02:34:34.530-06:30",
                    "checkedOutAt": "2017-01-08T13:46:34.530-06:30"
                }, 
                {
                    "locationId": 10,
                    "checkedInAt": "2017-01-10T03:49:11.357-06:30",
                    "checkedOutAt": "2017-01-10T11:29:11.357-06:30"
                }, 
                {
                    "locationId": 3,
                    "checkedInAt": "2017-01-12T03:19:45.408-06:30",
                    "checkedOutAt": "2017-01-12T14:14:45.408-06:30"
                }, 
                {
                    "locationId": 1,
                    "checkedInAt": "2017-01-15T02:56:41.659-06:30",
                    "checkedOutAt": "2017-01-15T09:14:41.659-06:30"
                }, 
                {
                    "locationId": 2,
                    "checkedInAt": "2017-01-18T04:52:44.156-06:30",
                    "checkedOutAt": "2017-01-18T13:46:44.156-06:30"
                }, 
                {
                    "locationId": 6,
                    "checkedInAt": "2017-01-20T05:22:19.348-06:30",
                    "checkedOutAt": "2017-01-20T13:38:19.348-06:30"
                }
            ]
        }
        self.parser = JSONPathParser(self.source_object)

    def test_jsonpath_nested_dict_single_value_expression(self):
        '''
        test to check jsonpath traversal into nested dictionary
        '''

        path = '$.name.first'
        self.assertEqual(self.parser.parse(path), "Deborah", "Failed to fetch correct value from nested dict")

    def test_jsonpath_nested_dict_multi_value_expression(self):
        '''
        test to check jsonpath traversal into nested dictionary
        '''

        path = '$.attendanceData[*].checkedInAt'
        self.assertEqual(
            self.parser.parse(path, return_array=True),
            [
                "2017-01-08T02:34:34.530-06:30",
                "2017-01-10T03:49:11.357-06:30",
                "2017-01-12T03:19:45.408-06:30",
                "2017-01-15T02:56:41.659-06:30",
                "2017-01-18T04:52:44.156-06:30",
                "2017-01-20T05:22:19.348-06:30"
            ],
            "Failed to fetch correct values from list of nested dicts"
        )

    def test_jsonpath_list_of_dict_match_item_single_value_expression(self):
        '''
        test to check jsonpath traversal into nested dictionaries inside list
        '''

        path = '$.attendanceData[?(@.locationId == 3)].checkedOutAt'
        self.assertEqual(
            self.parser.parse(path),
            "2017-01-12T14:14:45.408-06:30",
            "Failed to fetch correct value from nested dicts"
        )

    def test_jsonpath_list_of_dict_match_item_multi_value_expression(self):
        '''
        test to check jsonpath traversal into nested dictionaries inside list
        '''

        path = '$.attendanceData[?(@.locationId == 1)].checkedInAt'
        self.assertEqual(
            self.parser.parse(path, return_array=True),
            [
                "2017-01-08T02:34:34.530-06:30",
                "2017-01-15T02:56:41.659-06:30"
            ],
            "Failed to fetch correct value from nested dicts"
        )

    def test_jsonpath_list_of_dict_multi_condition_match_item_singe_value_expression(self):
        '''
        test to check jsonpath traversal into nested dictionaries inside list
        '''

        path = "$.attendanceData[?(@.locationId == 1 & @.checkedOutAt == '2017-01-15T09:14:41.659-06:30')].checkedInAt"
        self.assertEqual(
            self.parser.parse(path),
            "2017-01-15T02:56:41.659-06:30",
            "Failed to fetch correct value from nested dicts"
        )

    def test_jsonpath_no_value_expression(self):
        '''
        test to check jsonpath traversal into nested dictionaries inside list
        '''

        path = "$.attendanceData[?(@.locationId == 11)].checkedInAt"
        self.assertEqual(
            self.parser.parse(path),
            None,
            "Failed to fetch correct value from nested dicts"
        )

    def test_jsonpath_invalid_expression(self):
        '''
        test to check jsonpath traversal into nested dictionaries inside list
        '''

        path = "$.attendanceData().checkedInAt"
        with self.assertRaises(Exception):
            self.parser.parse(path)
