import unittest
import click
from click.core import Command

from wexample_wex_core.helpers.click_helper import (
    click_args_convert_dict_to_long_names_dict,
    click_args_convert_to_dict,
    click_args_convert_dict_to_args,
)


class TestClickHelper(unittest.TestCase):
    def setUp(self):
        """Create a test command for use in tests"""
        @click.command()
        @click.option('-n', '--name', help='Name option')
        @click.option('-f', '--flag', is_flag=True, help='Flag option')
        @click.option('-c', '--count', type=int, help='Count option')
        def test_command():
            pass
        
        self.test_command = test_command

    def test_click_args_convert_dict_to_long_names_dict(self):
        """Test conversion from short to long names in dictionary"""
        # Test with short names
        args = {
            'n': 'test',
            'f': True,
            'count': 5
        }
        expected = {
            'name': 'test',
            'flag': True,
            'count': 5
        }
        result = click_args_convert_dict_to_long_names_dict(self.test_command, args)
        self.assertEqual(result, expected)

        # Test with long names
        args = {
            'name': 'test',
            'flag': True,
            'count': 5
        }
        result = click_args_convert_dict_to_long_names_dict(self.test_command, args)
        self.assertEqual(result, args)

    def test_click_args_convert_to_dict(self):
        """Test conversion from argument list to dictionary"""
        # Test with long names
        arg_list = ['--name', 'test', '--flag', '--count', '5']
        expected = {
            'name': 'test',
            'flag': True,
            'count': '5'
        }
        result = click_args_convert_to_dict(self.test_command, arg_list)
        self.assertEqual(result, expected)

        # Test with short names
        arg_list = ['-n', 'test', '-f', '-c', '5']
        expected = {
            'n': 'test',
            'f': True,
            'c': '5'
        }
        result = click_args_convert_to_dict(self.test_command, arg_list)
        self.assertEqual(result, expected)

        # Test with mixed names
        arg_list = ['-n', 'test', '--flag', '-c', '5']
        expected = {
            'n': 'test',
            'flag': True,
            'c': '5'
        }
        result = click_args_convert_to_dict(self.test_command, arg_list)
        self.assertEqual(result, expected)

    def test_click_args_convert_dict_to_args(self):
        """Test conversion from dictionary to argument list"""
        # Test with regular options
        args = {
            'name': 'test',
            'count': '5'
        }
        expected = ['--name', 'test', '--count', '5']
        result = click_args_convert_dict_to_args(self.test_command, args)
        self.assertEqual(result, expected)

        # Test with flag option
        args = {
            'name': 'test',
            'flag': True
        }
        expected = ['--name', 'test', '--flag']
        result = click_args_convert_dict_to_args(self.test_command, args)
        self.assertEqual(result, expected)

        # Test with non-existent option
        args = {
            'name': 'test',
            'unknown': 'value'
        }
        expected = ['--name', 'test', '--unknown', 'value']
        result = click_args_convert_dict_to_args(self.test_command, args)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
