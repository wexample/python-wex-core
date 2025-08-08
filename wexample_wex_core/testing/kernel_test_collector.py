from helper.module import module_load_from_file


class KernelTestCollector:
    def __init__(self, config):
        self.config = config
        self.collected_modules = []

    def collect_wex_tests(self, command_data_list):
        """Collect tests from WEX command data."""
        for command_name, command_data in command_data_list:
            if "test" in command_data:
                test_file = command_data["test"]
                module = module_load_from_file(test_file, f"{command_name}_test")
                self.collected_modules.append(module)
