from wexample_wex_addon_app.utils.app_directory_structure import AppDirectoryStructure


class KernelDirectoryStructure(AppDirectoryStructure):
    should_exist: bool = True


KernelDirectoryStructure.model_rebuild()
