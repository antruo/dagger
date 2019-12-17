from acirc.utilities.config_validator import Attribute
from acirc.pipeline.io import IO

import json


class DbIO(IO):
    ref_name = "database"

    @classmethod
    def init_attributes(cls, orig_cls):
        cls.add_config_attributes([
            Attribute(attribute_name='database_type', comment="mysql, postgresql, etc"),
            Attribute(attribute_name='conn_id'),
            Attribute(attribute_name='table'),
        ])

    def __init__(self, io_config, task):
        super().__init__(io_config, task)

        self._database_type = self.parse_attribute('database_type')
        self._conn_id = self.parse_attribute('conn_id')
        self._table = self.parse_attribute('table')

    def alias(self):
        return "{type}://{conn_id}/{table}".format(
            type=self._database_type,
            conn_id=self._conn_id,
            table=self._table,
        )

    @property
    def rendered_name(self):
        return json.dumps({
            'database_type': self._database_type,
            'conn_id': self._conn_id,
            'table': self._table,
        })

    @property
    def airflow_name(self):
        return "{conn_id}-{table}".format(
            conn_id=self._conn_id,
            table=self._table,
        )

    @property
    def conn_id(self):
        return self._conn_id

    @property
    def table(self):
        return self._table