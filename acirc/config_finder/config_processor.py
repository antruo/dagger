import logging
from acirc.pipeline.pipeline import Pipeline
from acirc.config_finder.config_finder import ConfigFinder
from acirc.pipeline.task_factory import TaskFactory
# import acirc.conf as conf

from os.path import join, splitext, relpath
from os import environ
import yaml

_logger = logging.getLogger('configFinder')
DAG_DIR = join(environ['AIRFLOW_HOME'], 'dags')


class ConfigProcessor:
    def __init__(self, config_finder: ConfigFinder):
        self._config_finder = config_finder
        self._task_factory = TaskFactory()

    @staticmethod
    def _load_yaml(yaml_path):
        with open(yaml_path, 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                _logger.exception("Couldn't read config file {}", yaml_path, exc)
                exit(1)
        return config

    def process_pipeline_configs(self):
        configs = self._config_finder.find_configs()
        pipelines = []

        for pipeline_config in configs:
            pipeline_name = relpath(pipeline_config.directory, DAG_DIR).replace('/', '-')
            config_path = join(pipeline_config.directory, pipeline_config.config)

            _logger.info("Processing config: %s", config_path)
            pipeline = Pipeline(pipeline_config.directory, self._load_yaml(config_path))

            for task_config in pipeline_config.job_configs:
                task_name = splitext(task_config.config)[0]
                task_config_path = join(pipeline_config.directory, task_config.config)

                _logger.info("Processing task config: %s", task_config_path)
                task_config = self._load_yaml(task_config_path)
                task_type = task_config['type']
                pipeline.add_task(
                    self._task_factory.create_task(
                        task_type,
                        task_name,
                        pipeline_name,
                        pipeline,
                        task_config
                    )
                )

            pipelines.append(pipeline)

        return pipelines