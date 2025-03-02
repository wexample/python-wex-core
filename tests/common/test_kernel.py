import os
import pytest
import tempfile
import shutil

from wexample_wex_core.common.kernel import Kernel
from wexample_wex_core.common.file.kernel_directory_structure import KernelDirectoryStructure
from wexample_app.common.abstract_kernel import AbstractKernel
from wexample_app.common.mixins.command_line_kernel import CommandLineKernel


@pytest.fixture(scope="class")
def temp_dir():
    """Create a temporary directory with required structure."""
    dir_path = tempfile.mkdtemp()
    # Create entrypoint directory
    entrypoint_dir = os.path.join(dir_path, "entrypoint")
    os.makedirs(entrypoint_dir)
    # Create .env file
    with open(os.path.join(dir_path, ".env"), "w") as f:
        f.write("APP_ENV=test\n")
    
    yield dir_path
    
    # Cleanup after all tests
    shutil.rmtree(dir_path)


@pytest.fixture
def kernel(temp_dir):
    """Create a kernel instance for each test."""
    return Kernel(entrypoint_path=temp_dir)


def test_inheritance(kernel):
    """Test that Kernel inherits from correct parent classes."""
    assert isinstance(kernel, AbstractKernel)
    assert isinstance(kernel, CommandLineKernel)


def test_initialization(kernel):
    """Test that Kernel initializes correctly."""
    assert kernel is not None
    # Verify that _init_command_line_kernel was called during initialization
    # This is implicit since no error was raised, but we could add more specific tests
    # if there are specific attributes that should be set


def test_get_workdir_state_manager_class(kernel):
    """Test that the correct state manager class is returned."""
    state_manager_class = kernel._get_workdir_state_manager_class()
    assert state_manager_class == KernelDirectoryStructure

