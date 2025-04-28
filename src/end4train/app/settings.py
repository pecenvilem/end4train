from __future__ import annotations

from typing import Callable, Annotated

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStyleFactory
from pydantic import BaseModel, Field, AfterValidator


def validate_style_string(style_string: str, style_factory:Callable[[], list[str]] = QStyleFactory.keys) -> str:
    allowed = style_factory()
    if style_string not in allowed:
        raise ValueError(f"Can't create QStyle for factory string: {style_string}")
    return style_string


class PressureGaugeWidget(BaseModel):
    min_value: Annotated[float, Field(alias="minValue", title="Minimum value")] = 0.0
    max_value: Annotated[float, Field(alias="maxValue", title="Maximum value")] = 12.0
    min_angle: Annotated[float, Field(alias="minAngle", title="Minimum angle")] = 10.0
    max_angle: Annotated[float, Field(alias="maxAngle", title="Maximum angle")] = 350.0
    major_tick_count: Annotated[int, Field(alias="majorTickCount", title="Major ticks over the gauge range", ge=0)] = 6
    minor_tick_count: Annotated[int, Field(alias="minorTickCount", title="Minor ticks between two major ticks")] = 5
    minor_tick_labels: Annotated[bool, Field(alias="minorTickLabels", title="Labels on minor ticks")] = False


def pressure_gauge_widget_factory(
        min_value: float, max_value: float, max_angle: float, min_angle: float,
        major_tick_count: int, minor_tick_count: int, minor_tick_labels: bool
) -> PressureGaugeWidget:
    return PressureGaugeWidget(
        min_value=min_value, max_value=max_value, min_angle=min_angle, max_angle=max_angle,
        major_tick_count=major_tick_count, minor_tick_count=minor_tick_count, minor_tick_labels=minor_tick_labels
    )


class ThemeSection(BaseModel):
    style: Annotated[
        str,
        Field(title="Style", json_schema_extra={"platform_values": {"qt": QStyleFactory.keys()} }),
        AfterValidator(validate_style_string)
    ] = "Windows"
    color_scheme: Annotated[Qt.ColorScheme, Field(alias="colorScheme", title="Color Scheme")] = Qt.ColorScheme.Unknown


class PressureWidgetSection(BaseModel):
    main_reservoir: Annotated[
        PressureGaugeWidget, Field(alias="mainReservoir", title="Main reservoir")
    ] = pressure_gauge_widget_factory(0.0, 12.0, 10, 350, 6, 5, False)


class WidgetSection(BaseModel):
    pressure_widgets: Annotated[
        PressureWidgetSection, Field(alias="pressureWidgets", title="Pressure gauges")
    ] = PressureWidgetSection()


class Settings(BaseModel):
    autostart: Annotated[bool, Field(title="Autostart")] = False
    theme: Annotated[ThemeSection, Field(title="Theme")] = ThemeSection()
    widget: Annotated[WidgetSection, Field(title="Widgets")] = WidgetSection()
