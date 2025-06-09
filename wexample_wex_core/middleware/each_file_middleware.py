from wexample_wex_core.middleware.abstract_each_path_middleware import AbstractEachPathMiddleware


class EachFileMiddleware(AbstractEachPathMiddleware):
    option_name: str = 'file'
    option_description: str = "Path to local file"
