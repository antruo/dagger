from acirc.pipeline.io import IO
from acirc.pipeline.ios import (
    s3_io,
    redshift_io
)


class IOFactory:
    def __init__(self):
        self.factory = dict()

        for cls in IO.__subclasses__():
            self.factory[cls.ref_name] = cls

    def create_io(self, ref_name, io_config, task):
        return self.factory[ref_name](io_config=io_config, task=task)