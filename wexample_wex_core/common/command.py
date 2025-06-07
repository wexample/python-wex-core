from wexample_app.common.command import Command as BaseCommand


class Command(BaseCommand):
    def execute(self, arguments):
        # TODO convert arguments to splitted arguments.
        return self.function(
            kernel=self.kernel,
        )