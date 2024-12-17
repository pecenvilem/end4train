import QtQuick
import QtLocation
import QtPositioning

Map {
    id: map

    property variant position: QtPositioning.coordinate(50.0829886, 14.4369822) // Prague

    anchors.fill: parent
    center: position
    zoomLevel: 10
    plugin: Plugin
        {
            name: "osm"
            PluginParameter {name: "osm.mapping.custom.host"; value: "https://tile.openstreetmap.org/"}
        }
    activeMapType: supportedMapTypes[supportedMapTypes.length - 1]

    MapCircle {
        id: mainCircle
        center: position
        radius: 10
        visible: true
        color: 'blue'
    }

    WheelHandler {
        id: wheel
        rotationScale: 1/15
        property: "zoomLevel"
    }
    DragHandler {
        id: drag
        target: null
        onTranslationChanged: (delta) => map.pan(-delta.x, -delta.y)
    }
    Component.onCompleted: {
        map.addMapItem(mainCircle)
    }
}