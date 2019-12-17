from os import path
import logging
import yaml

_logger = logging.getLogger('root')


class Module:
    def __init__(self, directory, path_to_config):
        self._directory = directory
        config = self.read_yaml(self.read_task_config(path_to_config))

        self._tasks = {}
        for task in config['tasks']:
            self._tasks[task] = self.read_task_config(task)

        self._branches_to_generate = config['branches_to_generate']
        self._override_parameters = config.get('override_parameters', {})

    @staticmethod
    def read_yaml(yaml_str):
        try:
            yaml_obj = yaml.safe_load(yaml_str)
        except yaml.YAMLError as exc:
            _logger.error(f"Couldn't read config file {yaml_str}")
            exit(1)
        return yaml_obj

    def read_task_config(self, task):
        try:
            task_file = path.join(self._directory, task)  + ".yaml"
            with open(task_file, "r") as myfile:
                content = myfile.read()
        except:
            _logger.error(f"Couldn't load task file: {task_file}")
            exit(1)
        return content

    @staticmethod
    def replace_template_parameters(_task_str, _template_parameters):
        for _key, _value in _template_parameters.items():
            locals()[_key] = _value

        return _task_str.format(**locals()).replace("{", "{{").replace("}", "}}")

    @staticmethod
    def dump_yaml(yaml_str, yaml_path):
        with open(yaml_path, "w") as stream:
            yaml.safe_dump(yaml_str, stream=stream, default_flow_style=False, sort_keys=False)

    def generate_task_configs(self):
        for branch_name, attrs in self._branches_to_generate.items():
            _logger.info(f"Generating tasks for branch {branch_name}")

            for task, task_yaml in self._tasks.items():
                task_name = f"{task}_{branch_name}"
                _logger.info(f"Generating task {task_name}")
                task_str = self.replace_template_parameters(task_yaml, attrs)
                task_dict = yaml.safe_load(task_str)

                for override_parameter in self._override_parameters.get(branch_name, {}).get(task, []):
                    to_exec = "task_dict" + override_parameter
                    exec(to_exec)

                self.dump_yaml(task_dict, f"{task_name}.yaml")

    @staticmethod
    def module_config_template():
        return """
tasks:
  - task1 # Name of the template task file in module directory
  - task2
branches_to_generate:
  branch_name1: # Name of the branch (tasks are going to be named as <task-name>_<branch-name>)
    template_parameter_name1: template_parameter_value1
    template_parameter_name2: template_parameter_value2
  branch_name2:
    template_parameter_name1: template_parameter_value1
    template_parameter_name2: template_parameter_value2

#override_parameters:
#  branch_name1:
#    task1:
#      - "['task_parameters']['delete_target_dir'] = False"        
        """
