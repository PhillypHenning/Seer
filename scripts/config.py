import os

from pyconfman2 import Schema

config = Schema.ConfigSchema(filepath="local_config.yml")

required_local_paths = [
    "data",
    "data/vectors",
]