import os
import unittest
import tempfile
import shutil

from wexample_wex_core.common.workdir import Workdir
from wexample_wex_core.common.kernel import Kernel


class TestWorkdir(unittest.TestCase):
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
        self.workdir = Workdir()

    def test_initialization(self):
        """Test that Workdir initializes correctly."""
        self.assertIsNotNone(self.workdir)

    @classmethod
    def tearDownClass(cls):
        """Clean up the temporary directory after all tests."""
        shutil.rmtree(cls.temp_dir)


if __name__ == '__main__':
    unittest.main()
