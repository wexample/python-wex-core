from wexample_app.common.command import Command


class CommandExecutor(Command):
    def execute(self, arguments):
        return self.function(
            kernel=self.kernel,
        )