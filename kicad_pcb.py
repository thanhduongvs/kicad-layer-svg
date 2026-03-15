import re
import math
from kipy import KiCad
from kipy.board import Board
from kipy.board_types import Track, ArcTrack, BoardSegment, BoardRectangle, BoardPolygon, BoardArc, BoardCircle
from typing import Set, Optional, List, Tuple, DefaultDict
from collections import defaultdict
from kipy.geometry import Vector2
from dataclasses import dataclass, field
from data import LayerMap, PointData, ViaData, TrackData, ArcTrackData
from kipy.proto.board.board_types_pb2 import BoardLayer

class KiCadPCB:
    def __init__(self):
        self.kicad: Optional[KiCad] = None
        self.board: Optional[Board] = None
        self.connected: bool = False
        self.stackup: List[LayerMap] = []

    def connect_kicad(self) -> Tuple[bool, str]:
        try:
            #nets = KiCad().get_board().get_nets()
            #print(f"nets: {nets}")
            self.footprints = []
            self.kicad = KiCad()
            #self.board = self.kicad.get_board()
            self.connected = True

            self.get_net_classes()
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
        
    def get_edge_cuts(self):
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

                elif isinstance(shape, BoardRectangle):
                    update_bounds(shape.top_left.x, shape.top_left.y, bounds)
                    update_bounds(shape.bottom_right.x, shape.bottom_right.y, bounds)            
                elif isinstance(shape, BoardArc):
                    update_bounds(shape.start.x, shape.start.y, bounds)
                    update_bounds(shape.mid.x, shape.mid.y, bounds)
                    update_bounds(shape.end.x, shape.end.y, bounds)
                    
                elif isinstance(shape, BoardCircle):
                    cx, cy = shape.center.x, shape.center.y
                    rx, ry = shape.radius_point.x, shape.radius_point.y
                    
                    radius = math.hypot(rx - cx, ry - cy)
                    
                    update_bounds(cx - radius, cy - radius, bounds)
                    update_bounds(cx + radius, cy + radius, bounds)
                elif isinstance(shape, BoardPolygon):
                    print(shape.bounding_box())
                    print(shape.polygons)
                """
                elif isinstance(shape, BoardPolygon):
                    for polygon_with_holes in shape.points:
                        for node in polygon_with_holes.outline.nodes:
                            update_bounds(node.point.x, node.point.y, bounds)
                """

        return bounds['minx'], bounds['miny'], bounds['maxx'], bounds['maxy']

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
        
    def get_via(self):
        for via in self.board.get_vias():
            via = ViaData(
                name =via.net.name,
                diameter = via.diameter,
                drill= via.drill_diameter,
                position = PointData(via.position.x, via.position.y),
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

    
    def get_arc_tracks(self):
        arc_tracks = [t for t in self.board.get_tracks() if isinstance(t, ArcTrack)]
        for t in arc_tracks:
            track = ArcTrackData(
                name = t.net.name,
                width = t.width,
                layer = t.layer,
                start = PointData(t.start.x, t.start.y),
                end = PointData(t.end.x, t.end.y),
                mid = PointData(t.mid.x, t.mid.y),
                center = PointData(t.center().x, t.center().y),
                radius = t.radius(),
                start_angle = t.start_angle(),
                end_angle = t.end_angle(),
                angle = t.angle(),
                length = t.length()
            )

def update_bounds(x, y, bounds):
    """
    Cập nhật Bounding Box. 
    'bounds' là một dictionary chứa {'minx':..., 'miny':..., 'maxx':..., 'maxy':...}
    """
    if x < bounds['minx']: bounds['minx'] = x
    if x > bounds['maxx']: bounds['maxx'] = x
    if y < bounds['miny']: bounds['miny'] = y
    if y > bounds['maxy']: bounds['maxy'] = y
