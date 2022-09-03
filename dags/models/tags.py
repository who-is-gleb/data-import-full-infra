from enum import Enum


class Tag(str, Enum):
    github = 'github'
    daily = 'daily'
    with_catchup = 'with_catchup'
