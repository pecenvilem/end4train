from __future__ import annotations

from end4train.communication.constants import MINIMUM_INTENSITY, MAXIMUM_INTENSITY, DATA_ATTRIBUTE_LABEL


class InvalidDisplayIntensityError(ValueError):
    def __init__(self, requested_intensity):
        super().__init__()
        self.requested_intensity = requested_intensity

    def __str__(self):
        return f"Requested intensity {self.requested_intensity} out of bounds [{MINIMUM_INTENSITY};{MAXIMUM_INTENSITY}]"


class KSYSpecMissingIDError(Exception):
    def __init__(self, type_name: str, attribute_index: int):
        message = (f"Attribute '{attribute_index}' of type '{type_name}' is marked as {DATA_ATTRIBUTE_LABEL}, "
                   f"but has no 'id' specified!")
        super().__init__(message)


class KSYSpecInvalidRepeatConditionError(Exception):
    def __init__(self, type_name: str, attribute_name: str, repeat_condition: str):
        message = (f"Attribute '{attribute_name}' of type '{type_name}' has repeat condition {repeat_condition}, "
                   f"this is not supported!")
        super().__init__(message)


class KSYSpecInvalidRepeatExpressionError(Exception):
    def __init__(self, type_name: str, attribute_name: str, repeat_expression: str):
        message = (f"Attribute '{attribute_name}' of type '{type_name}' has repeat expression '{repeat_expression}', "
                   f"this is not supported! (Must be an integer.)")
        super().__init__(message)


class AmbiguousObjectTypeEnumNameError(Exception):
    def __init__(self, enum_name: str, matched_devices: list):
        message = f"'{enum_name}' matched against {len(matched_devices)} devices:"
        message += ", ".join(str(device) for device in matched_devices)
        super().__init__(message)
