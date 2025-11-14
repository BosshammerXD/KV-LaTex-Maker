import json
import os
from typing import Union
from types import ModuleType
from Globals.STATIC import PATHS

if not os.path.exists(PATHS.CONFIG_FOLDER):
    os.makedirs(PATHS.CONFIG_FOLDER, exist_ok=True)

__PRIMITIVE_TYPES = Union[int, float, str, bool]
__JsonData = dict[str, Union[__PRIMITIVE_TYPES, list['__JsonData'], tuple['__JsonData'], dict[str, '__JsonData'], '__JsonData']]
#
#
#
#region json creation
def __generate_json_data(data: ModuleType) -> __JsonData:
    retval: __JsonData = {}
    for attr_name, attr in data.__dict__.items():
        if attr_name.startswith("__"):
            continue
        if isinstance(attr, ModuleType):
            retval[attr_name] = __generate_json_data(attr)
        elif isinstance(attr, Union[__PRIMITIVE_TYPES, list, tuple, dict]):
            retval[attr_name] = attr
        else:
            raise ValueError(f"Encountered type that cannot be dumped into json. {attr_name}:{type(attr)}")
    return retval

def write_to_json(path: str, data: ModuleType):
    json_data: __JsonData = __generate_json_data(data)

    path_to_file = os.path.join(PATHS.CONFIG_FOLDER, path)
    
    with open(path_to_file, "w+") as f:
        f.write(json.dumps(json_data, indent=2))
#endregion
#
#
#
#region get data from Json
def __fill_data(contents: __JsonData, data: ModuleType | type):
    for key, value in contents.items():
        if not hasattr(data, key):
            raise ValueError(f"the provided json has the wrong contents. {key} is not a member of the dataclass")
        val = getattr(data, key)
        if isinstance(val, type) and isinstance(value, dict):
            __fill_data(value, val) #type:ignore
        elif isinstance(value, type(val)):
            setattr(data, key, value)
        else:
            raise ValueError(f"The values of the provided json have the wrong type. {key} has type {type(val)} in dataclass {data.__name__} but type {type(value)} in json")


def read_from_json(path: str, data: ModuleType):
    contents: __JsonData
    with open(os.path.join(PATHS.CONFIG_FOLDER, path)) as f:
        contents = json.loads(f.read())
    __fill_data(contents, data)
#endregion

if __name__ == "__main__":
    pass