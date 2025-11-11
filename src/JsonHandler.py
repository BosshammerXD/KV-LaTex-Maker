import dataclasses
import json
import os
from typing import Any, Protocol, Union, runtime_checkable

@runtime_checkable
class DataclassProtocol(Protocol):
    __dataclass_fields__: dict[str, Any]
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
def __generate_json_data(data: DataclassProtocol) -> __JsonData:
    retval: __JsonData = {}
    for field in dataclasses.fields(data): #type:ignore 
        attr_name = field.name
        attr = getattr(data, attr_name)
        if isinstance(attr, DataclassProtocol):
            retval[attr_name] = __generate_json_data(attr)
        elif isinstance(attr, Union[__PRIMITIVE_TYPES, list, tuple, dict]):
            retval[attr_name] = attr
        else:
            raise ValueError(f"Encountered type that cannot be dumped into json. type:{field.type}")
    return retval

def write_to_json(path: str, data: Any):
    assert isinstance(data, DataclassProtocol), "Provided data was not a dataclass"

    json_data: __JsonData = __generate_json_data(data)

    path_to_file = os.path.join(CONFIGS_PATH, path)
    
    with open(path_to_file, "w+") as f:
        f.write(json.dumps(json_data, indent=2))
#endregion
#
#
#
#region get data from Json
def __fill_data(contents: __JsonData, data: DataclassProtocol):
    for key, value in contents.items():
        if not hasattr(data, key):
            raise ValueError(f"the provided json has the wrong contents. {key} is not a member of the dataclass")
        val = getattr(data, key)
        if isinstance(val, DataclassProtocol) and isinstance(value, dict):
            __fill_data(value, val) #type:ignore
        elif isinstance(value, type(val)):
            setattr(data, key, value)
        else:
            raise ValueError(f"The values of the provided json have the wrong type. {key} has type {type(val)} in dataclass {data.__class__} but type {type(value)} in json")


def read_from_json(path: str, data: Any):
    assert(isinstance(data, DataclassProtocol))
    contents: __JsonData
    try:
        with open(os.path.join(CONFIGS_PATH, path)) as f:
            contents = json.loads(f.read())
    except FileNotFoundError:
        return
    __fill_data(contents, data)
#endregion

@dataclasses.dataclass
class B:
    y: int = 1

@dataclasses.dataclass
class A:
    y: B
    x: int = 1

if __name__ == "__main__":
    write_to_json("config.json", A(x=10, y=B(10)))
    myA = A(y=B(1))
    print(myA.x, myA.y.y, sep=", ")
    read_from_json("config.json", myA)
    print(myA.x, myA.y.y, sep=", ")