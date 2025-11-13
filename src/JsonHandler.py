import dataclasses
import json
import os
from typing import Any, Union

#
#
#
#region move to globals later
base_dir = os.path.dirname(os.path.abspath(__file__))
#endregion
#
#
#
CONFIGS_PATH: str = os.path.join(base_dir, "configs")
if not os.path.exists(CONFIGS_PATH):
    os.makedirs(CONFIGS_PATH, exist_ok=True)

__PRIMITIVE_TYPES = Union[int, float, str, bool]
__JsonData = dict[str, Union[__PRIMITIVE_TYPES, list['__JsonData'], tuple['__JsonData'], dict[str, '__JsonData'], '__JsonData']]
#
#
#
#region json creation
def __generate_json_data(data: type) -> __JsonData:
    retval: __JsonData = {}
    for field in dataclasses.fields(data): #type:ignore 
        attr_name = field.name
        attr = getattr(data, attr_name)
        if isinstance(attr, type):
            retval[attr_name] = __generate_json_data(attr)
        elif isinstance(attr, Union[__PRIMITIVE_TYPES, list, tuple, dict]):
            retval[attr_name] = attr
        else:
            raise ValueError(f"Encountered type that cannot be dumped into json. type:{field.type}")
    return retval

def write_to_json(path: str, data: Any):
    assert isinstance(data, type), "Provided data was not a dataclass"

    json_data: __JsonData = __generate_json_data(data)

    path_to_file = os.path.join(CONFIGS_PATH, path)
    
    with open(path_to_file, "w+") as f:
        f.write(json.dumps(json_data, indent=2))
#endregion
#
#
#
#region get data from Json
def __fill_data(contents: __JsonData, data: type):
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


def read_from_json(path: str, data: Any):
    assert(isinstance(data, type))
    contents: __JsonData
    with open(os.path.join(CONFIGS_PATH, path)) as f:
        contents = json.loads(f.read())
    __fill_data(contents, data)
#endregion

if __name__ == "__main__":
    pass