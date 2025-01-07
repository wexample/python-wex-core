import os
import pytest
import tempfile
import shutil

from wexample_wex_core.common.workdir import Workdir
from wexample_wex_core.common.kernel import Kernel


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


@pytest.fixture
def workdir():
    """Create a workdir instance for each test."""
    return Workdir()


def test_initialization(workdir):
    """Test that Workdir initializes correctly."""
    assert workdir is not None


def test_kernel_integration(kernel, workdir):
    """Test workdir integration with kernel."""
    assert workdir is not None
    # Add more specific tests for workdir-kernel interaction if needed
