from wexample_app.workdir.app_workdir import AppWorkdir


class KernelDirectoryStructure(AppWorkdir):
    should_exist: bool = True


KernelDirectoryStructure.model_rebuild()
