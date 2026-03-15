from typing import List
from dataclasses import dataclass

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
    position: PointData
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
    start_angle: float
    end_angle: float
    angle: float
    length: float

class PadData:
    type: str
    pos: PointData
    size: PointData
    angle: float
    shape: str
    net: str
    layer: int

class PcbData:
    def __init__(self, box):
        self.box:BoxData = box
        self.vias:List[ViaData] = []
        self.tracks:List[TrackData] = []
        self.pads:List[PadData] = []

class NetClass:
    def __init__(self, name):
        self.name = name
        self.nets = []