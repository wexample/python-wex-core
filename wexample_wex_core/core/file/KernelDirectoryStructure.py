from wexample_wex_addon_app.utils.AppDirectoryStructure import AppDirectoryStructure


class KernelDirectoryStructure(AppDirectoryStructure):
    should_exist: bool = True


KernelDirectoryStructure.model_rebuild()
