import math
import cairo
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kicad_pcb import KiCadPCB

class PCBSVG:
    def __init__(self, kicad: 'KiCadPCB'):
        self.kicad = kicad
        self.surfaces = []
        self.layer_contexts = []
        
        if not kicad.box or kicad.box.minx == float('inf'):
            print("Lỗi: Không tìm thấy Bounding Box hợp lệ.")
            return

        # Hệ số phóng to và chuyển đổi Nanometer -> Pixel/Millimeter
        zoom_factor = 20
        self.SCALE = 1e-6 * zoom_factor

        # Tính kích thước mặt giấy SVG
        dx_px = (kicad.box.maxx - kicad.box.minx) * self.SCALE
        dy_px = (kicad.box.maxy - kicad.box.miny) * self.SCALE

        self.layer_id_to_idx = {l.id: i for i, l in enumerate(self.kicad.stackup)}

        for layer_info in self.kicad.stackup:
            filename = f"{layer_info.name}.svg"
            
            surface = cairo.SVGSurface(filename, dx_px, dy_px)
            ctx = cairo.Context(surface)
            
            self.layer_contexts.append(ctx)
            self.surfaces.append(surface)
        
        self.draw()

    def draw(self):
        minx = self.kicad.box.minx
        miny = self.kicad.box.miny

        # ==========================================
        # 1. VẼ TRACKS (Đoạn thẳng)
        # ==========================================
        for track in self.kicad.pcbdata.tracks:
            idx = self.layer_id_to_idx.get(track.layer, -1)
            if idx == -1: continue
            
            if track.start.x == track.end.x and track.start.y == track.end.y:
                continue

            ctx = self.layer_contexts[idx]
            ctx.set_source_rgb(0.0, 0.0, 0.0) # Màu đen
            
            w_mm = track.width * self.SCALE
            sx_mm = (track.start.x - minx) * self.SCALE
            sy_mm = (track.start.y - miny) * self.SCALE
            ex_mm = (track.end.x - minx) * self.SCALE
            ey_mm = (track.end.y - miny) * self.SCALE

            ctx.set_line_width(w_mm)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            
            ctx.new_path()
            ctx.move_to(sx_mm, sy_mm)
            ctx.line_to(ex_mm, ey_mm)
            ctx.stroke()

        # ==========================================
        # 2. VẼ ARC TRACKS (Đường cong)
        # ==========================================
        for arc in self.kicad.pcbdata.arc_tracks:
            idx = self.layer_id_to_idx.get(arc.layer, -1)
            if idx == -1: continue

            ctx = self.layer_contexts[idx]
            ctx.set_source_rgb(0.0, 0.0, 0.0) # Màu đen
            
            w_mm = arc.width * self.SCALE
            r_mm = arc.radius * self.SCALE
            cx = (arc.center.x - minx) * self.SCALE
            cy = (arc.center.y - miny) * self.SCALE
            
            sx = (arc.start.x - minx) * self.SCALE
            sy = (arc.start.y - miny) * self.SCALE
            ex = (arc.end.x - minx) * self.SCALE
            ey = (arc.end.y - miny) * self.SCALE
            mx = (arc.mid.x - minx) * self.SCALE
            my = (arc.mid.y - miny) * self.SCALE
            
            start_rad = math.atan2(sy - cy, sx - cx)
            end_rad = math.atan2(ey - cy, ex - cx)
            mid_rad = math.atan2(my - cy, mx - cx)

            diff1 = (mid_rad - start_rad) % (2 * math.pi)
            diff2 = (end_rad - mid_rad) % (2 * math.pi)
            
            is_clockwise = (diff1 + diff2) < (2 * math.pi + 1e-4)

            ctx.set_line_width(w_mm)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            
            ctx.new_path()
            if is_clockwise:
                ctx.arc(cx, cy, r_mm, start_rad, end_rad)
            else:
                ctx.arc_negative(cx, cy, r_mm, start_rad, end_rad)
            ctx.stroke()

        # ==========================================
        # 3. VẼ VIAS (Xuyên lỗ)
        # ==========================================
        for via in self.kicad.pcbdata.vias:
            vx_mm = (via.pos.x - minx) * self.SCALE
            vy_mm = (via.pos.y - miny) * self.SCALE
            diam_mm = via.diameter * self.SCALE
            drill_mm = via.drill * self.SCALE

            for layer_id in via.layers:
                idx = self.layer_id_to_idx.get(layer_id, -1)
                if idx == -1: continue
                
                ctx = self.layer_contexts[idx]
                ctx.save()
                ctx.set_source_rgb(0.8, 0.6, 0.2) # Màu đồng
                
                ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
                ctx.new_path()
                ctx.arc(vx_mm, vy_mm, diam_mm / 2, 0, 2*math.pi) 
                ctx.new_sub_path()
                ctx.arc(vx_mm, vy_mm, drill_mm / 2, 0, 2*math.pi) 
                
                ctx.fill()
                ctx.restore()

        # ==========================================
        # 4. VẼ PADS (Chân linh kiện)
        # ==========================================
        for pad in self.kicad.pcbdata.pads:
            idx = self.layer_id_to_idx.get(pad.layer, -1)
            if idx == -1: continue
            
            ctx = self.layer_contexts[idx]
            
            px_mm = (pad.pos.x - minx) * self.SCALE
            py_mm = (pad.pos.y - miny) * self.SCALE
            sx_mm = pad.size.x * self.SCALE
            sy_mm = pad.size.y * self.SCALE
            
            off_x_mm = pad.offset.x * self.SCALE
            off_y_mm = pad.offset.y * self.SCALE

            ctx.save()
            
            color = getattr(self, 'net_to_color', {}).get(pad.name, (0.8, 0.2, 0.2))
            ctx.set_source_rgb(*color) 
            
            ctx.translate(px_mm, py_mm)
            if pad.angle != 0:
                ctx.rotate(math.radians(pad.angle))
            ctx.translate(off_x_mm, off_y_mm)

            # Thiết lập quy tắc đổ màu đục lỗ chuẩn SVG
            ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
            ctx.new_path()
            shape_type = str(pad.shape).lower()
            
            if "circle" in shape_type:
                ctx.arc(0, 0, sx_mm / 2, 0, 2*math.pi)
                
            elif "oval" in shape_type or "oblong" in shape_type:
                self._create_oval_path(ctx, sx_mm, sy_mm)

            elif "roundrect" in shape_type:
                ratio = pad.rounding_ratio if pad.rounding_ratio > 0 else 0.25
                r = min(sx_mm, sy_mm) * ratio
                w, h = sx_mm, sy_mm
                ctx.arc(w/2 - r, h/2 - r, r, 0, math.pi/2)             
                ctx.arc(-w/2 + r, h/2 - r, r, math.pi/2, math.pi)      
                ctx.arc(-w/2 + r, -h/2 + r, r, math.pi, 3*math.pi/2)   
                ctx.arc(w/2 - r, -h/2 + r, r, 3*math.pi/2, 2*math.pi)  
                ctx.close_path()

            elif "chamferedrect" in shape_type:
                ratio = pad.chamfer_ratio if pad.chamfer_ratio > 0 else 0.20
                chamfer = min(sx_mm, sy_mm) * ratio
                w, h = sx_mm, sy_mm
                ctx.move_to(-w/2, -h/2 + chamfer)     
                ctx.line_to(-w/2 + chamfer, -h/2)     
                ctx.line_to(w/2, -h/2)                
                ctx.line_to(w/2, h/2 - chamfer)       
                ctx.line_to(w/2 - chamfer, h/2)       
                ctx.line_to(-w/2, h/2)                
                ctx.close_path()

            else:
                ctx.rectangle(-sx_mm / 2, -sy_mm / 2, sx_mm, sy_mm)

            # Xử lý đục lỗ khoan cho Pad PTH
            if pad.drill_size and (pad.drill_size.x > 0 or pad.drill_size.y > 0):
                # Dịch ngược offset để lỗ khoan nằm ở tâm thực của footprint
                ctx.translate(-off_x_mm, -off_y_mm)
                
                dx_mm = pad.drill_size.x * self.SCALE
                dy_mm = pad.drill_size.y * self.SCALE
                
                ctx.new_sub_path()
                
                if pad.drill_shape == "oblong" and dx_mm != dy_mm:
                    self._create_oval_path(ctx, dx_mm, dy_mm)
                else:
                    drill_d = max(dx_mm, dy_mm)
                    ctx.arc(0, 0, drill_d / 2, 0, 2*math.pi)
                
            # Đổ màu một lần duy nhất
            ctx.fill()
            ctx.restore()

        # ==========================================
        # 5. Lưu File
        # ==========================================
        for surface in self.surfaces:
            surface.finish()
        print("Đã xuất hoàn thiện bản mạch!")

    def _create_oval_path(self, ctx, w, h):
        """Tạo đường dẫn hình bầu dục (Pill shape)"""
        r = min(w, h) / 2
        if w > h:
            l = (w / 2) - r
            ctx.arc(l, 0, r, -math.pi/2, math.pi/2)    # Cung bên phải
            ctx.arc(-l, 0, r, math.pi/2, 3*math.pi/2)  # Cung bên trái
        else:
            t = (h / 2) - r
            ctx.arc(0, t, r, 0, math.pi)               # Cung bên dưới
            ctx.arc(0, -t, r, math.pi, 2*math.pi)      # Cung bên trên
        ctx.close_path()