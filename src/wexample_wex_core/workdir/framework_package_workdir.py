from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from wexample_wex_core.workdir.project_workdir import ProjectWorkdir

if TYPE_CHECKING:
    from wexample_prompt.common.progress.progress_handle import ProgressHandle


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

    def publish(self, commit_and_push: bool = False, progress: ProgressHandle | None = None, ) -> None:
        """Push the package to the packages manager service (npm, pipy, packagist, etc.)"""
        from wexample_helpers.helpers.shell import shell_run

        if commit_and_push:
            shell_run([
                'git',
                'commit',
                '-am',
                f'"Publishing version {self.get_project_version()}"',
            ], inherit_stdio=True, cwd=self.get_path())

            shell_run([
                'git',
                'push',
            ], inherit_stdio=True, cwd=self.get_path())

    def bump(self, interactive: bool = False, **kwargs) -> None:
        """Create a version-x.y.z branch, update the version number in config. Don't commit changes."""
        from wexample_helpers.helpers.version import version_increment

        current_version = self.get_project_version()
        new_version = version_increment(version=current_version, **kwargs)
        branch_name = f"version-{new_version}"

        def _bump() -> None:
            from wexample_helpers.helpers.shell import shell_run

            # Create or switch to branch first, so changes are committed on it.
            try:
                # Try to create and switch (git switch -c is safer, fallback to checkout -b)
                try:
                    shell_run(
                        ["git", "switch", "-c", branch_name],
                        inherit_stdio=True,
                        cwd=self.get_path(),
                    )
                except Exception:
                    # If switch -c is unavailable or branch exists, try checkout -b
                    shell_run(
                        ["git", "checkout", "-b", branch_name],
                        inherit_stdio=True,
                        cwd=self.get_path(),
                    )
            except Exception:
                # If branch already exists, just switch to it.
                shell_run(
                    ["git", "switch", branch_name],
                    inherit_stdio=True,
                    cwd=self.get_path(),
                )

            # Change version number on this branch
            self.get_config_file().write_config_value("version", new_version)

            self.success(
                f'Bumped {self.get_package_name()} from "{current_version}" to "{new_version}" and switched to branch "{branch_name}"'
            )

        if interactive:
            confirm = self.confirm(
                f"Do you want to create a new version for package {self.get_package_name()} in {self.get_path()}? "
                f'This will create/switch to branch "{branch_name}".'
            )

            if confirm.get_answer():
                _bump()
        else:
            _bump()
