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
        """Publish workflow for the package (git commit & push)."""
        from wexample_helpers_git.helpers.git import (
            git_commit_all_with_message,
            git_current_branch,
            git_ensure_upstream,
            git_has_index_changes,
            git_has_working_changes,
            git_pull_rebase_autostash,
            git_push_follow_tags,
        )

        if not commit_and_push:
            return

        cwd = self.get_path()
        # Prepare progress handle
        progress = progress or self.io.progress(
            label="Publishing package...", total=4
        ).get_handle()

        git_current_branch(cwd=cwd, inherit_stdio=False)
        git_ensure_upstream(cwd=cwd, default_remote="origin", inherit_stdio=True)
        progress.advance(step=1, label="Ensured upstream")

        git_pull_rebase_autostash(cwd=cwd, inherit_stdio=True)
        progress.advance(step=1, label="Pulled latest (rebase)")

        # Commit only if there are changes (either staged or unstaged tracked files)
        has_working_changes = git_has_working_changes(cwd=cwd)
        has_index_changes = git_has_index_changes(cwd=cwd)

        if has_working_changes or has_index_changes:
            git_commit_all_with_message(
                f"Publishing version {self.get_project_version()}",
                cwd=cwd,
                inherit_stdio=True,
            )
            progress.advance(step=1, label="Committed changes")
        else:
            progress.advance(step=1, label="No changes to commit")

        # Push to upstream, following tags if any were created externally
        git_push_follow_tags(cwd=cwd, inherit_stdio=True)

        progress.finish(label="Pushed")

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
