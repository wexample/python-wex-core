from __future__ import annotations

from abc import abstractmethod

from wexample_wex_core.workdir.project_workdir import ProjectWorkdir


class FrameworkPackageWorkdir(ProjectWorkdir):
    @abstractmethod
    def get_package_name(self) -> str:
        pass

    @abstractmethod
    def get_dependencies(self) -> list[str]:
        pass

    def imports_package_in_codebase(
            self, searched_package: FrameworkPackageWorkdir
    ) -> bool:
        """Check whether the given package is used in this package's codebase."""
        return False

    def build_dependencies_stack(
            self, package: FrameworkPackageWorkdir, dependency: FrameworkPackageWorkdir
    ) -> list[FrameworkPackageWorkdir]:
        """When package is dependent from another one (is using it in its codebase),
        list the packages inheritance stack to find the original package declaring the explicit dependency
        """
        return []

    def depends_from(self, package: FrameworkPackageWorkdir) -> bool:
        """Check if current package depends on given one."""
        return False

    def save_dependency(self, package: FrameworkPackageWorkdir) -> None:
        """Register a dependency into the configuration file."""

    def publish(self) -> None:
        """Push the package to the packages manager service (npm, pipy, packagist, etc.)"""

    def bump(self, interactive: bool = False, **kwargs) -> None:
        from wexample_helpers.helpers.version import version_increment

        version = self.get_project_version()
        new_version = version_increment(version=self.get_project_version(), **kwargs)
        branch_name = f"version-{new_version}"

        def _bump():
            from wexample_helpers.helpers.shell import shell_run

            # Change version number
            self.get_config_file().write_config_value("version", new_version)

            # Create branch and checkout.
            shell_run([
                "git",
                "branch",
                branch_name
            ],
                inherit_stdio=True,
                cwd=self.get_path()
            )

            shell_run([
                "git",
                "checkout",
                branch_name
            ],
                inherit_stdio=True,
                cwd=self.get_path()
            )

            self.success(
                f'Updated {self.get_package_name()} from version "{version}" to "{new_version}"'
            )

        if interactive:
            confirm = self.confirm(
                f"Do you want to create a new version for package {self.get_package_name()} in  {self.get_path()} ?"
                f"This will create a new branch \"{branch_name}\""
            )

            if confirm.get_answer():
                _bump()
        else:
            _bump()
