import pytest

from wexample_wex_core.addons.default.default_addon_manager import DefaultAddonManager
from wexample_wex_core.common.kernel import Kernel
from wexample_wex_core.const.globals import CORE_COMMAND_NAME


@pytest.fixture
def kernel(tmp_path):
    wex_dir = tmp_path / CORE_COMMAND_NAME
    wex_dir.mkdir()
    (tmp_path / ".env").write_text("APP_ENV=test\n")
    k = Kernel(entrypoint_path=wex_dir)
    k.setup(addons=[DefaultAddonManager])
    return k


@pytest.fixture
def kernel_stdout(kernel):
    from wexample_app.const.output import OUTPUT_TARGET_STDOUT

    kernel.set_output_target([OUTPUT_TARGET_STDOUT])
    return kernel
