from __future__ import annotations

from typing import Type, Any

import numpy as np
import pandas as pd
from numpy.dtypes import StringDType

from end4train.communication.constants import SIZE_INCREMENT


class RecordDataStore:
    def __init__(self):
        self.arrays: dict[Type, dict[str, np.typing.NDArray]] = {}
        self.indices: dict[Type, int] = {}

    def create_arrays_for_type(self, type_key: Type) -> None:
        self.indices[type_key] = 0
        self.arrays[type_key] = {}
        self.arrays[type_key]["second"] = np.zeros(SIZE_INCREMENT, dtype=int)
        self.arrays[type_key]["millisecond"] = np.zeros(SIZE_INCREMENT, dtype=int)
        self.arrays[type_key]["data_object_type"] = np.empty(SIZE_INCREMENT, dtype=int)
        self.arrays[type_key]["variable"] = np.empty(SIZE_INCREMENT, dtype=StringDType())
        self.arrays[type_key]["value"] = np.empty(SIZE_INCREMENT, dtype=type_key)

    def enlarge_arrays_for_type(self, type_key: Type) -> None:
        self.arrays[type_key]["second"] = np.append(
            self.arrays[type_key]["second"], np.zeros(SIZE_INCREMENT, dtype=int)
        )
        self.arrays[type_key]["millisecond"] = np.append(
            self.arrays[type_key]["millisecond"], np.zeros(SIZE_INCREMENT, dtype=int)
        )
        self.arrays[type_key]["data_object_type"] = np.append(
            self.arrays[type_key]["data_object_type"], np.empty(SIZE_INCREMENT, dtype=int)
        )
        self.arrays[type_key]["variable"] = np.append(
            self.arrays[type_key]["variable"], np.empty(SIZE_INCREMENT, dtype=StringDType())
        )
        self.arrays[type_key]["value"] = np.append(
            self.arrays[type_key]["value"], np.empty(SIZE_INCREMENT, dtype=type_key)
        )

    def store_value(
            self, value: Any, object_type: int, variable_name: str, second: int, millisecond: int = 0
    ) -> None:
        value_type = type(value)
        if value_type not in self.arrays:
            self.create_arrays_for_type(value_type)
        type_arrays = self.arrays[value_type]
        index = self.indices[value_type]
        if index >= len(type_arrays["second"]):
            self.enlarge_arrays_for_type(value_type)
        type_arrays["second"][index] = second
        type_arrays["millisecond"][index] = millisecond
        type_arrays["data_object_type"][index] = object_type
        type_arrays["variable"][index] = variable_name
        type_arrays["value"][index] = value
        self.indices[value_type] += 1

    def get_data_types(self) -> list[Type]:
        return list(self.arrays.keys())

    def get_data(self, data_type: Type) -> pd.DataFrame:
        type_arrays = self.arrays[data_type]
        return pd.DataFrame(type_arrays).iloc[0:self.indices[data_type]]

    def get_all_data(self) -> dict[Type, pd.DataFrame]:
        return {data_type: self.get_data(data_type) for data_type in self.get_data_types()}
