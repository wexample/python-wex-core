from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware

if TYPE_CHECKING:
    from wexample_helpers.const.types import Kwargs
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
    from wexample_wex_core.common.command_request import CommandRequest
    from wexample_wex_core.context.execution_context import ExecutionContext


class AbstractEachPathMiddleware(AbstractMiddleware):
    expand_glob: bool = False
    recursion_limit: int = 100
    recursive: bool = False
    should_exist: bool = False

    def __attrs_post_init__(self, **kwargs) -> None:
        # Set default option if none provided
        if "option" not in kwargs or not kwargs["option"]:
            kwargs["option"] = self._get_default_option()

        kwargs["options"] = [kwargs["option"]]

    def build_execution_contexts(
        self,
        command_wrapper: CommandMethodWrapper,
        request: CommandRequest,
        function_kwargs: Kwargs,
    ) -> list[ExecutionContext]:
        from wexample_wex_core.context.execution_context import ExecutionContext

        # If glob expansion is enabled and the path is a directory,
        # create an execution for each matching item in that directory
        if self.expand_glob:

            path = self._get_option_file_path(function_kwargs=function_kwargs)

            # If the path is a directory, process it
            if os.path.isdir(path):
                passes = []
                option = self.get_first_option()

                # Process the directory (recursively if enabled)
                path_kwargs_list = self._process_directory_recursively(
                    request=request, directory_path=path, option_name=option.name
                )

                # Create execution passes by combining the original kwargs with each path
                for path_kwargs in path_kwargs_list:
                    kwargs_copy = function_kwargs.copy()
                    kwargs_copy.update(path_kwargs)

                    passes.append(
                        ExecutionContext(
                            middleware=self,
                            command_wrapper=command_wrapper,
                            request=request,
                            function_kwargs=kwargs_copy,
                        )
                    )

                return passes

            # If the path is not a directory, continue normally
            # (validation will happen in validate_options)

        # If expand_glob is not enabled, use default behavior
        return super().build_execution_contexts(
            command_wrapper=command_wrapper,
            request=request,
            function_kwargs=function_kwargs,
        )

    def validate_options(
        self,
        command_wrapper: CommandMethodWrapper,
        request: CommandRequest,
        function_kwargs: Kwargs,
    ) -> bool:
        from wexample_wex_core.exception.path_not_found_command_option_exception import (
            PathNotFoundCommandOptionException,
        )

        if self.should_exist:
            import os.path

            option = self.get_first_option()
            if option and option.name in function_kwargs:
                file_path = function_kwargs[option.name]
                if not os.path.exists(file_path):
                    raise PathNotFoundCommandOptionException(
                        option_name=option.name, file_path=file_path
                    )

        return True

    def _get_default_option(self) -> dict[str, Any]:
        """Get the default path option definition."""
        from wexample_helpers.const.globals import PATH_NAME_PATH

        return {
            "name": PATH_NAME_PATH,
            "type": str,
            "required": True,
            "description": "Path to local file or directory",
        }

    def _get_option_file_path(self, function_kwargs: Kwargs) -> str | None:
        option = self.get_first_option()
        return function_kwargs[option.name]

    def _process_directory_recursively(
        self,
        request: CommandRequest,
        directory_path: str,
        option_name: str,
        current_depth: int = 0,
    ) -> list[dict]:
        """
        Process a directory recursively, collecting paths that match the criteria.

        Args:
            directory_path: Path to the directory to process
            option_name: Name of the option to set in function kwargs
            current_depth: Current recursion depth

        Returns:
            List of function kwargs dictionaries for each matching path
        """
        if current_depth > self.recursion_limit:
            return []  # Stop recursion if max depth is reached

        result = []

        try:
            # Iterate through all directory items
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)

                # Process items that match the subclass criteria
                if self._should_process_item(request=request, item_path=item_path):
                    # Create a copy of arguments for each matching item
                    result.append({option_name: item_path})

                # If recursive is enabled and item is a directory, check if we should explore it
                if self.recursive and os.path.isdir(item_path):
                    # Skip directories that shouldn't be explored
                    if not self._should_explore_directory(
                        request=request, directory_name=item
                    ):
                        request.kernel.io.info(
                            f"Skipping path that does not match middleware policy: {item_path}"
                        )
                        continue

                    subdirectory_results = self._process_directory_recursively(
                        request=request,
                        directory_path=item_path,
                        option_name=option_name,
                        current_depth=current_depth + 1,
                    )
                    result.extend(subdirectory_results)
        except (PermissionError, FileNotFoundError):
            # Skip directories we can't access
            pass

        return result

    def _should_explore_directory(
        self, request: CommandRequest, directory_name: str
    ) -> bool:
        """
        Determine if a directory should be explored during recursive traversal.
        This method can be overridden by subclasses to skip certain directories.

        Args:
            directory_name: Name of the directory to check (not the full path)

        Returns:
            True if the directory should be explored, False otherwise
        """
        # Base implementation explores all directories
        return True

    def _should_process_item(self, request: CommandRequest, item_path: str) -> bool:
        """
        Determine if an item should be processed based on its path.
        This method should be overridden by subclasses to implement specific filtering logic.

        Args:
            item_path: Path to the item to check

        Returns:
            True if the item should be processed, False otherwise
        """
        # Base implementation accepts all items
        return True
