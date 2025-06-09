from wexample_wex_core.middleware.abstract_each_path_middleware import AbstractEachPathMiddleware


class EachDirectoryMiddleware(AbstractEachPathMiddleware):
    option_name: str = 'directory'
    option_description: str = "Path to local directory"
