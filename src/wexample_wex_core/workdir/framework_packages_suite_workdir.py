from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_prompt.common.progress.progress_handle import ProgressHandle
from wexample_wex_core.workdir.project_workdir import ProjectWorkdir

if TYPE_CHECKING:
    from wexample_wex_core.workdir.framework_package_workdir import (
        FrameworkPackageWorkdir,
    )


class FrameworkPackageSuiteWorkdir(ProjectWorkdir):
    def get_local_packages_names(self) -> list[str]:
        return [p.get_package_name() for p in self.get_packages()]

    def build_dependencies_map(self) -> dict[str, list[str]]:
        dependencies = {}
        for package in self.get_packages():
            dependencies[package.get_package_name()] = self.filter_local_packages(
                package.get_dependencies()
            )

        return dependencies

    def get_packages(self) -> list[FrameworkPackageWorkdir]:
        pip_dir = self.find_by_name(item_name="pip")
        if pip_dir:
            return pip_dir.get_children_list()
        return []

    def get_dependents(
        self, package: FrameworkPackageWorkdir
    ) -> list[FrameworkPackageWorkdir]:
        return []

    def get_package(self, package_name: str) -> FrameworkPackageWorkdir | None:
        for package in self.get_packages():
            if package.get_package_name() == package_name:
                return package
        return None

    def filter_local_packages(self, packages: list[str]) -> list[str]:
        """
        Keep only dependencies that are local to this workspace.

        A local dependency is one whose package name matches one of the packages
        discovered by get_packages().
        """
        # Use the dedicated helper to retrieve local package names
        local_names = set(self.get_local_packages_names())
        if not packages:
            return []
        # Return only those present locally, preserve order and remove duplicates
        seen: set[str] = set()
        filtered: list[str] = []
        for name in packages:
            if name in local_names and name not in seen:
                seen.add(name)
                filtered.append(name)
        return filtered

    def build_dependencies_stack(
        self,
        package: FrameworkPackageWorkdir,
        dependency: FrameworkPackageWorkdir,
        dependencies_map: dict[str, list[str]],
    ) -> list[FrameworkPackageWorkdir]:
        """When a package depends on another (uses it in its codebase),
        return the dependency chain to locate the original package that declares the explicit dependency.
        """
        return []

    def get_ordered_packages(self) -> list[FrameworkPackageWorkdir]:
        return self.get_packages()

    def packages_propagate_versions(
        self, progress: ProgressHandle | None = None
    ) -> None:
        ordered_packages = self.get_ordered_packages()

        progress = (
            progress
            or self.io.progress(
                label=f"Starting...", total=len(ordered_packages)
            ).get_handle()
        )

        for package in ordered_packages:
            progress.advance(
                label=f'Propagating package "{package.get_package_name()}" version "{package.get_project_version()}"',
                step=1,
            )
            self.io.indentation_up()
            for dependent in self.get_dependents(package):
                self.io.log(f"Applying to {dependent.get_package_name()}")
                dependent.save_dependency(package)
            self.io.indentation_down()
        progress.finish()

    # Publication planning helpers
    def compute_packages_to_publish(self) -> list[FrameworkPackageWorkdir]:
        """Return packages that changed since their last publication tag.

        If a package has no previous tag, it is considered to be published.
        """
        to_publish: list[FrameworkPackageWorkdir] = []
        for pkg in self.get_packages():
            try:
                if pkg.has_changes_since_last_publication_tag():
                    to_publish.append(pkg)
            except Exception:
                # Be conservative: if detection fails, include the package to avoid missing a needed release
                to_publish.append(pkg)
        return to_publish

    def stabilize_publication_plan(
        self,
        *,
        context,
        yes: bool,
        max_loops: int = 3,
        progress: ProgressHandle | None = None,
    ) -> list[FrameworkPackageWorkdir]:
        """Iteratively run rectify + version propagation until the set of packages to publish stabilizes."""
        from wexample_wex_addon_app.commands.files_state.rectify import (
            app__files_state__rectify,
        )

        progress = (
            progress
            or self.io.progress(
                label="Stabilizing plan...", total=max_loops
            ).get_handle()
        )
        to_publish = self.compute_packages_to_publish()
        loop = 0
        while to_publish and loop < max_loops:
            loop += 1
            # Run rectify (updates pinned deps)
            app__files_state__rectify.function(context=context, yes=yes)

            # Recreate this workdir from context's addon manager
            # NOTE: caller must re-fetch instance if needed; we just recompute on the fly
            progress.advance(step=1, label=f"Iteration {loop}")

            # Re-validate and re-propagate versions
            self.packages_validate_internal_dependencies_declarations()
            self.packages_propagate_versions()

            new_to_publish = self.compute_packages_to_publish()
            if {p.get_package_name() for p in new_to_publish} == {
                p.get_package_name() for p in to_publish
            }:
                break
            to_publish = new_to_publish

        progress.finish()
        return to_publish
