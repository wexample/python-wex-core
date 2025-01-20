import pytest
import click

from wexample_wex_core.helpers.click_helper import (
    click_args_convert_dict_to_long_names_dict,
    click_args_convert_to_dict,
    click_args_convert_dict_to_args,
)


@pytest.fixture
def test_command():
    """Create a test command for use in tests"""
    @click.command()
    @click.option('-n', '--name', help='Name option')
    @click.option('-f', '--flag', is_flag=True, help='Flag option')
    @click.option('-c', '--count', type=int, help='Count option')
    def cmd():
        pass
    
    return cmd


def test_click_args_convert_dict_to_long_names_dict(test_command):
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
    assert click_args_convert_dict_to_long_names_dict(test_command, args) == expected

    # Test with long names
    args = {
        'name': 'test',
        'flag': True,
        'count': 5
    }
    assert click_args_convert_dict_to_long_names_dict(test_command, args) == expected

    # Test with mixed names
    args = {
        'name': 'test',
        'f': True,
        'count': 5
    }
    assert click_args_convert_dict_to_long_names_dict(test_command, args) == expected


def test_click_args_convert_to_dict(test_command):
    """Test conversion from args list to dictionary"""
    # Test with long names
    args = ['--name', 'test', '--flag', '--count', '5']
    expected = {
        'name': 'test',
        'flag': True,
        'count': '5'
    }
    assert click_args_convert_to_dict(test_command, args) == expected

    # Test with short names
    args = ['-n', 'test', '-f', '-c', '5']
    expected = {
        'n': 'test',
        'f': True,
        'c': '5'
    }
    assert click_args_convert_to_dict(test_command, args) == expected

    # Test with mixed names
    args = ['--name', 'test', '-f', '--count', '5']
    expected = {
        'name': 'test',
        'f': True,
        'count': '5'
    }
    assert click_args_convert_to_dict(test_command, args) == expected


def test_click_args_convert_dict_to_args(test_command):
    """Test conversion from dictionary to args list"""
    # Test with all options
    args = {
        'name': 'test',
        'flag': True,
        'count': 5
    }
    result = click_args_convert_dict_to_args(test_command, args)
    assert '--name' in result
    assert 'test' in result
    assert '--flag' in result
    assert '--count' in result
    assert '5' in result

    # Test with some options
    args = {
        'name': 'test',
        'count': 5
    }
    result = click_args_convert_dict_to_args(test_command, args)
    assert '--name' in result
    assert 'test' in result
    assert '--count' in result
    assert '5' in result
    assert '--flag' not in result

    # Test with flag set to False
    args = {
        'name': 'test',
        'flag': False,
        'count': 5
    }
    result = click_args_convert_dict_to_args(test_command, args)
    assert '--name' in result
    assert 'test' in result
    assert '--count' in result
    assert '5' in result
    assert '--flag' not in result
