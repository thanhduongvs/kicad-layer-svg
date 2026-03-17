from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class LayerMap:
    name: str
    id: int

@dataclass
class BoxData:
    minx: int
    miny: int
    maxx: int
    maxy: int

@dataclass
class PointData:
    x: int
    y: int

@dataclass
class ViaData:
    name: str
    diameter: int
    drill: int
    pos: PointData
    layers: List[int]

@dataclass
class TrackData:
    name: str
    width: int
    layer: int
    start: PointData
    end: PointData

@dataclass
class ArcTrackData:
    name: str
    width: int
    layer: int
    start: PointData
    end: PointData
    mid: PointData
    center: PointData
    radius: float

@dataclass
class PadData:
    name: str
    type: str
    layer: int
    pos: PointData
    size: PointData
    offset: PointData
    angle: float
    shape: str
    rounding_ratio: float
    chamfer_ratio: float
    chamfered_corners: List[str]
    trapezoid_delta: PointData
    drill_size: PointData
    drill_shape: str

@dataclass
class EdgeData:
    type: str
    width: int
    start: PointData
    end: PointData
    mid: PointData
    center: PointData
    radius: float

@dataclass
class PolygonData:
    outline: List[PointData]
    holes: List[List[PointData]]

@dataclass
class ZoneData:
    name: str
    layer: int
    polygons: List[PolygonData]

@dataclass
class PcbData:
    box: Optional[BoxData] = None
    vias: List[ViaData] = field(default_factory=list)
    tracks: List[TrackData] = field(default_factory=list)
    arc_tracks: List[ArcTrackData] = field(default_factory=list)
    pads: List[PadData] = field(default_factory=list)
    edge_cuts: List[EdgeData] = field(default_factory=list)
    zones: List[ZoneData] = field(default_factory=list)

@dataclass
class NetClass:
    name: str
    nets: List[PadData] = field(default_factory=list)
