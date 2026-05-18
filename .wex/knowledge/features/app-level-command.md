# App-level commands

App-level commands are YAML or Python files stored inside a project's `.wex/commands/` directory. They are invoked with the `.` prefix from anywhere inside the project tree.

## Naming convention

| Context        | Format       | Example                          |
|----------------|--------------|----------------------------------|
| Directory name | `snake_case` | `install/`                       |
| File name      | `snake_case` | `local.yml`                      |
| CLI invocation | `kebab-case` | `wex .install/local`             |

The resolver converts kebab-case to snake_case internally, so `wex .my-group/my-command` maps to `.wex/commands/my_group/my_command.yml` (or `.py`).

## Invocation

```bash
wex .my-group/my-command
wex .my-group/my-command --option value
```

The resolver walks up from the current working directory to find the nearest `.wex/` directory.

## File location

```
<project-root>/
  .wex/
    commands/
      my_group/
        my_command.yml   # or my_command.py
```

---

## YAML commands

Use YAML for simple scripts or to orchestrate multiple runners/steps.

```yaml
description: "What this command does"
options:
  - name: my_option
    short: o
    type: str          # str | int | bool
    default: "value"
    help: "Option description"
scripts:
  - runner: bash
    script: echo "hello ${MY_OPTION}"
  - runner: python
    script: |
      print("hello")
  - runner: docker
    service: my_service
    script: echo "inside container"
```

### Runners

| Runner   | Executes on       | Working directory          |
|----------|-------------------|----------------------------|
| `bash`   | host              | project root               |
| `python` | host              | project root               |
| `docker` | container service | container app dir (`/app`) |

For `docker`, set `service` to the service name from your `docker-compose.yml` (e.g. `vite`, `main`).

### Variable substitution

Variables from `.wex/.env` are substituted in YAML scripts **before execution** using `${VAR_NAME}` syntax. This applies to all runners.

```yaml
# .wex/.env
MY_TOKEN=abc123
```

```yaml
scripts:
  - runner: bash
    script: echo "token is ${MY_TOKEN}"

  - runner: python
    script: |
      token = "${MY_TOKEN}"
      # do NOT use os.environ.get("MY_TOKEN") — not injected into the process
```

Option values are also available as `${MY_OPTION}` (uppercased option name).

### Calling another wex command from a step

YAML steps can delegate to another command. This is useful to keep complex logic in a `.py` file and orchestrate it from YAML alongside other steps (e.g. a docker step).

```yaml
# .wex/commands/install/local.yml
description: "Switch to local mount and reinstall"
scripts:
  - command: .install/update-package-json
    args:
      mode: local
  - runner: docker
    service: vite
    script: npm install
```

---

## Python commands

Use Python for commands with non-trivial logic. The function must be named `app__{group}__{name}` and decorated with `@command(type=COMMAND_TYPE_APP)`.

```python
# .wex/commands/install/update_package_json.py
from __future__ import annotations
from typing import TYPE_CHECKING
from wexample_wex_core.const.globals import COMMAND_TYPE_APP
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@command(
    type=COMMAND_TYPE_APP,
    description="Update package.json dependency mode",
)
def app__install__update_package_json(context: ExecutionContext) -> None:
    import json
    kernel = context.kernel
    io = context.io

    with open("package.json") as f:
        pkg = json.load(f)
    # ... logic here
    with open("package.json", "w") as f:
        json.dump(pkg, f, indent=2)
        f.write("\n")
    io.success(message="package.json updated")
```

### When to use Python vs YAML

| Use YAML when...                              | Use Python when...                        |
|-----------------------------------------------|-------------------------------------------|
| Script is simple (a few lines)                | Logic is complex or requires imports      |
| You need multiple runners in sequence         | You want type hints, error handling, etc. |
| You want to call other commands + run docker  | No docker step needed                     |

The recommended pattern for commands that need both logic **and** a docker step: put the logic in a `.py` command and call it from a `.yml` orchestrator alongside the docker step.
