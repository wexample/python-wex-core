import os
import unittest
import tempfile
import shutil

from wexample_wex_core.common.kernel import Kernel
from wexample_wex_core.common.file.kernel_directory_structure import KernelDirectoryStructure
from wexample_app.utils.abstract_kernel import AbstractKernel
from wexample_app.utils.mixins.command_line_kernel import CommandLineKernel


class TestKernel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create a temporary directory with required structure before any test."""
        cls.temp_dir = tempfile.mkdtemp()
        # Create entrypoint directory
        cls.entrypoint_dir = os.path.join(cls.temp_dir, "entrypoint")
        os.makedirs(cls.entrypoint_dir)
        # Create .env file
        with open(os.path.join(cls.temp_dir, ".env"), "w") as f:
            f.write("APP_ENV=test\n")

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.kernel = Kernel(
            entrypoint_path=self.temp_dir
        )

    def test_inheritance(self):
        """Test that Kernel inherits from correct parent classes."""
        self.assertIsInstance(self.kernel, AbstractKernel)
        self.assertIsInstance(self.kernel, CommandLineKernel)

    def test_initialization(self):
        """Test that Kernel initializes correctly."""
        self.assertIsNotNone(self.kernel)
        # Verify that _init_command_line_kernel was called during initialization
        # This is implicit since no error was raised, but we could add more specific tests
        # if there are specific attributes that should be set

    def test_get_workdir_state_manager_class(self):
        """Test that the correct state manager class is returned."""
        state_manager_class = self.kernel._get_workdir_state_manager_class()
        self.assertEqual(state_manager_class, KernelDirectoryStructure)

    @classmethod
    def tearDownClass(cls):
        """Clean up the temporary directory after all tests."""
        shutil.rmtree(cls.temp_dir)


if __name__ == '__main__':
    unittest.main()
