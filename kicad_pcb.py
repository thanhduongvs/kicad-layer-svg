import re
import math
from kipy import KiCad
from kipy.board import Board, BoardOriginType
from kipy.board_types import Track, ArcTrack, BoardSegment, BoardRectangle, BoardPolygon, BoardArc, BoardCircle
from typing import Set, Optional, List, Tuple, DefaultDict
from collections import defaultdict
from kipy.geometry import Vector2
from dataclasses import dataclass, field
from data import LayerMap, PointData, ViaData, TrackData, ArcTrackData, PcbData, PadData, BoxData, EdgeData
from kipy.proto.board.board_types_pb2 import BoardLayer, PadType, PadStackShape, DrillShape

class KiCadPCB:
    def __init__(self):
        self.kicad: Optional[KiCad] = None
        self.board: Optional[Board] = None
        self.connected: bool = False
        self.box: Optional[BoxData] = None
        self.stackup: List[LayerMap] = []
        self.pcbdata: PcbData = PcbData()
        self.layers: List[str] = []

    def connect_kicad(self) -> Tuple[bool, str]:
        try:
            #nets = KiCad().get_board().get_nets()
            #print(f"nets: {nets}")
            self.footprints = []
            self.kicad = KiCad()
            self.board = self.kicad.get_board()
            self.connected = True

            self.get_edge_cuts()
            self.get_stackup()
            self.get_vias()
            self.get_tracks()
            self.get_arc_tracks()
            self.get_pads()
            print("done")
            return True, "Connected to KiCad"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.connected = False
            self.footprints = []
            self.references = []
            self.stackup = []
            self.layers = []
            return False, str(e)
        
    def get_edge_cuts(self) -> BoxData:
        bounds = {
            'minx': float('inf'),
            'miny': float('inf'),
            'maxx': float('-inf'),
            'maxy': float('-inf')
        }
        for shape in self.board.get_shapes():
            #print(shape)
            if shape.layer == BoardLayer.BL_Edge_Cuts:
                if isinstance(shape, BoardSegment):
                    update_bounds(shape.start.x, shape.start.y, bounds)
                    update_bounds(shape.end.x, shape.end.y, bounds)
                    edge =  EdgeData(
                        type = 'segment',
                        width = shape.attributes.stroke.width,
                        start = PointData(shape.start.x, shape.start.y),
                        end = PointData(shape.end.x, shape.end.y),
                        center = PointData(0, 0),
                        mid = PointData(0, 0),
                        radius = 0
                    )
                    self.pcbdata.edge_cuts.append(edge)

                elif isinstance(shape, BoardRectangle):
                    update_bounds(shape.top_left.x, shape.top_left.y, bounds)
                    update_bounds(shape.bottom_right.x, shape.bottom_right.y, bounds) 
                    edge =  EdgeData(
                        type = 'rectangle',
                        width = shape.attributes.stroke.width,
                        start = PointData(shape.top_left.x, shape.top_left.y),
                        end = PointData(shape.bottom_right.x, shape.bottom_right.y),
                        center = PointData(0, 0),
                        mid = PointData(0, 0),
                        radius = 0
                    )
                    self.pcbdata.edge_cuts.append(edge)           
                elif isinstance(shape, BoardArc):
                    update_bounds(shape.start.x, shape.start.y, bounds)
                    update_bounds(shape.mid.x, shape.mid.y, bounds)
                    update_bounds(shape.end.x, shape.end.y, bounds)
                    edge =  EdgeData(
                        type = 'arc',
                        width = shape.attributes.stroke.width,
                        start = PointData(shape.start.x, shape.start.y),
                        end = PointData(shape.end.x, shape.end.y),
                        mid = PointData(shape.mid.x, shape.mid.y),
                        center = PointData(shape.center().x, shape.center().y),
                        radius = shape.radius()
                    )
                    self.pcbdata.edge_cuts.append(edge)
                elif isinstance(shape, BoardCircle):
                    cx, cy = shape.center.x, shape.center.y
                    rx, ry = shape.radius_point.x, shape.radius_point.y
                    
                    radius = math.hypot(rx - cx, ry - cy)
                    
                    update_bounds(cx - radius, cy - radius, bounds)
                    update_bounds(cx + radius, cy + radius, bounds)
                    
                    edge = EdgeData(
                        type = 'circle',
                        width = shape.attributes.stroke.width,
                        start = PointData(cx, cy),  # Bắt buộc của dataclass
                        end = PointData(cx, cy),    # Bắt buộc của dataclass
                        mid = PointData(0, 0),
                        center = PointData(cx, cy), # Dữ liệu thực tế để vẽ
                        radius = radius             # Dữ liệu thực tế để vẽ
                    )
                    self.pcbdata.edge_cuts.append(edge)
                elif isinstance(shape, BoardPolygon):
                    for p in shape.polygons:
                        nodes = p.outline.nodes
                        if not nodes:
                            continue
                            
                        # Cập nhật Bounding Box cho tất cả các đỉnh
                        for node in nodes:
                            update_bounds(node.point.x, node.point.y, bounds)
                            
                        # Tạo các đoạn thẳng (segment) nối các đỉnh với nhau
                        num_nodes = len(nodes)
                        for i in range(num_nodes):
                            start_node = nodes[i]
                            # Lấy đỉnh tiếp theo, nếu là đỉnh cuối thì quay lại đỉnh 0
                            end_node = nodes[(i + 1) % num_nodes]
                            
                            edge = EdgeData(
                                type='segment',
                                width=shape.attributes.stroke.width,
                                start=PointData(start_node.point.x, start_node.point.y),
                                end=PointData(end_node.point.x, end_node.point.y),
                                center = PointData(0, 0),
                                mid = PointData(0, 0),
                                radius = 0
                            )
                            self.pcbdata.edge_cuts.append(edge)

        offset = self.board.get_origin(BoardOriginType.BOT_GRID)
        minx = bounds['minx'] - offset.x
        maxx = bounds['maxx'] - offset.x
        miny = bounds['miny'] - offset.y
        maxy = bounds['maxy'] - offset.y
        print(f"{minx}, {maxx}, {miny}, {maxy}")
        self.box = BoxData(
            minx = bounds['minx'],
            miny = bounds['miny'],
            maxx = bounds['maxx'],
            maxy = bounds['maxy']
        )

    def get_net_classes(self):
        nets = KiCad().get_board().get_nets()
        net_classes = KiCad().get_board().get_netclass_for_nets(nets)
        print(f"nets: {net_classes}")
        #net_classes = KiCad().get_project(KiCad().get_board().document).get_net_classes()
        #names = [t.name for t in net_classes if t.name != 'Default']
        #print(names)
        #for name in names:
            #print(name)
            #nets = KiCad().get_board().get_nets(netclass_filter=name)
            #nets = self.board.get_nets(netclass_filter=name)
            #print(f"nets: {nets}")
        
    def get_stackup(self):
        stackup = self.board.get_stackup()
        for l in stackup.layers:
            if BoardLayer.BL_F_Cu <= l.layer <= BoardLayer.BL_B_Cu:
                l_name = l.user_name if l.user_name else f"Layer {l.layer}"
                self.stackup.append(LayerMap(l_name, l.layer))
        
        self.stackup.sort(key=lambda x: x.id)
        self.layers = [layer.name for layer in self.stackup]
        
    def get_vias(self):
        for via in self.board.get_vias():
            via = ViaData(
                name =via.net.name,
                diameter = via.diameter,
                drill= via.drill_diameter,
                pos = PointData(via.position.x, via.position.y),
                layers = via.padstack.layers
            )
            self.pcbdata.vias.append(via)

    def get_tracks(self):
        tracks = [t for t in self.board.get_tracks() if isinstance(t, Track)]
        for t in tracks:
            track = TrackData(
                name = t.net.name,
                width = t.width,
                layer = t.layer,
                start = PointData(t.start.x, t.start.y),
                end = PointData(t.end.x, t.end.y)
            )
            self.pcbdata.tracks.append(track)

    
    def get_arc_tracks(self):
        arc_tracks = [t for t in self.board.get_tracks() if isinstance(t, ArcTrack)]
        for t in arc_tracks:
            if t.center() is None:
                track_fallback = TrackData(
                    name = t.net.name,
                    width = t.width,
                    layer = t.layer,
                    start = PointData(t.start.x, t.start.y),
                    end = PointData(t.end.x, t.end.y)
                )
                self.pcbdata.tracks.append(track_fallback)
                continue
            track = ArcTrackData(
                name = t.net.name,
                width = t.width,
                layer = t.layer,
                start = PointData(t.start.x, t.start.y),
                end = PointData(t.end.x, t.end.y),
                mid = PointData(t.mid.x, t.mid.y),
                center = PointData(t.center().x, t.center().y),
                radius = t.radius()
            )
            self.pcbdata.arc_tracks.append(track)
    
    def get_pads(self):
        for p in self.board.get_pads():
            pad_type = 'unknown'
            match p.pad_type:
                case PadType.PT_PTH:
                    pad_type = 'pth'
                case PadType.PT_SMD:
                    pad_type = 'smd'
                case PadType.PT_EDGE_CONNECTOR:
                    pad_type = 'edge'

            copper_layers = p.padstack.copper_layers
            copper = copper_layers[0]
            shape = 'unknown'
            drill_shape = 'unknown'
            match p.padstack.drill.shape:
                case DrillShape.DS_CIRCLE:
                    drill_shape = 'circle'
                case DrillShape.DS_OBLONG:
                    shape = 'oblong'
    
            match copper.shape:
                case PadStackShape.PSS_CIRCLE:
                    shape = 'circle'
                case PadStackShape.PSS_RECTANGLE:
                    shape = 'rectangle'
                case PadStackShape.PSS_OVAL:
                    shape = 'oval'
                case PadStackShape.PSS_TRAPEZOID:
                    shape = 'trapezoid'
                case PadStackShape.PSS_ROUNDRECT:
                    shape = 'roundrect'
                case PadStackShape.PSS_CHAMFEREDRECT:
                    shape = 'chamferedrect'
            for l in p.padstack.layers:
                if BoardLayer.BL_F_Cu <= l <= BoardLayer.BL_B_Cu:
                    pad = PadData(
                        name = p.net.name,
                        type = pad_type,
                        layer = l,
                        pos = PointData(p.position.x, p.position.y),
                        size = PointData(copper.size.x, copper.size.y),
                        offset = PointData(copper.offset.x, copper.offset.y),
                        angle = p.padstack.angle.degrees,
                        shape = shape,
                        rounding_ratio = copper.corner_rounding_ratio,
                        chamfer_ratio = copper.chamfer_ratio,
                        drill_size = PointData(p.padstack.drill.diameter.x, p.padstack.drill.diameter.y),
                        drill_shape = drill_shape
                    )
                    self.pcbdata.pads.append(pad)


def update_bounds(x, y, bounds):
    """
    Cập nhật Bounding Box. 
    'bounds' là một dictionary chứa {'minx':..., 'miny':..., 'maxx':..., 'maxy':...}
    """
    if x < bounds['minx']: bounds['minx'] = x
    if x > bounds['maxx']: bounds['maxx'] = x
    if y < bounds['miny']: bounds['miny'] = y
    if y > bounds['maxy']: bounds['maxy'] = y
