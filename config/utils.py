import os
import sys
import ast
import json
import string
from typing import TypeVar, Callable, Iterable, Optional, List


T = TypeVar("T")


def get_env_var(key: str, default: T) -> T:
    value = os.getenv(key)
    if value is None:
        return default
    try:
        value = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        pass
    assert type(value) == type(default), f"invalid value for {key}: {value!r}"
    return value


def alchemize_url(url: str) -> str:
    SCHEMES = (
        ("sqlite", "sqlite+aiosqlite"),
        ("postgres", "postgresql+asyncpg"),
        ("mysql", "mysql+aiomysql"),
    )

    for name, scheme in SCHEMES:
        if url.startswith(name):
            return url.replace(name, scheme, 1)
    return url


class Formatter(string.Template):
    delimiter = ""
    format = string.Template.safe_substitute


def load_configs(
    name: str, object_hook: Optional[Callable[[dict], dict]] = None
) -> List[dict]:
    dirs = [
        os.path.dirname(__file__),
        os.path.dirname(os.path.abspath(sys.argv[0])),
        os.getcwd(),
    ]
    dirs = sorted(set(dirs), key=dirs.index)
    result = []
    for dir_ in dirs:
        file = os.path.join(dir_, name)
        if os.path.isfile(file):
            with open(file) as f:
                result.append(json.load(f, object_hook=object_hook))
        else:
            result.append({})
    return result


def join_dicts(dicts: Iterable[dict]) -> dict:
    result = {}
    for d in dicts:
        result.update(d)
    return result


def subtract_dicts(orig_dict: dict, subtract: dict) -> dict:
    return {k: v for k, v in orig_dict.items() if k not in subtract}
