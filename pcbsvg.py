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
            
            # 1. Tính toán tất cả tọa độ ra đơn vị Millimeter trên bản vẽ
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
            
            # 2. Lấy góc tuyệt đối (Radian) dựa trên tọa độ thực
            start_rad = math.atan2(sy - cy, sx - cx)
            end_rad = math.atan2(ey - cy, ex - cx)
            mid_rad = math.atan2(my - cy, mx - cx)

            # 3. Thuật toán kiểm tra hướng quét đi qua điểm Mid
            # Đưa góc chênh lệch về phạm vi [0, 2*PI)
            diff1 = (mid_rad - start_rad) % (2 * math.pi)
            diff2 = (end_rad - mid_rad) % (2 * math.pi)
            
            # Nếu tổng 2 góc chênh lệch < 360 độ -> Quét cùng chiều kim đồng hồ
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

            # Via xuất hiện trên nhiều lớp đồng
            for layer_id in via.layers:
                idx = self.layer_id_to_idx.get(layer_id, -1)
                if idx == -1: continue
                
                ctx = self.layer_contexts[idx]
                ctx.save()
                ctx.set_source_rgb(0.8, 0.6, 0.2) # Màu đồng (vàng ươm)
                
                # Dùng Even-Odd để đục lỗ Via
                ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
                ctx.new_path()
                ctx.arc(vx_mm, vy_mm, diam_mm / 2, 0, 2*math.pi) # Vòng ngoài
                ctx.new_sub_path()
                ctx.arc(vx_mm, vy_mm, drill_mm / 2, 0, 2*math.pi) # Lỗ khoan
                
                ctx.fill()
                ctx.restore()

        # ==========================================
        # 4. VẼ PADS (Chân linh kiện)
        # ==========================================
        """
        for pad in self.kicad.pcbdata.pads:
            idx = self.layer_id_to_idx.get(pad.layer, -1)
            if idx == -1: continue
            
            ctx = self.layer_contexts[idx]
            
            px_mm = (pad.pos.x - minx) * self.SCALE
            py_mm = (pad.pos.y - miny) * self.SCALE
            sx_mm = pad.size.x * self.SCALE
            sy_mm = pad.size.y * self.SCALE

            ctx.save()
            ctx.set_source_rgb(0.7, 0.0, 0.0) # Màu đỏ đậm cho Pad
            
            # Dịch chuyển và xoay hệ tọa độ tại tâm Pad
            ctx.translate(px_mm, py_mm)
            if pad.angle != 0:
                ctx.rotate(math.radians(pad.angle))

            if pad.shape == "circle":
                ctx.new_path()
                ctx.arc(0, 0, sx_mm / 2, 0, 2*math.pi)
                ctx.fill()
                
            elif pad.shape == "rect":
                ctx.new_path()
                # Cairo vẽ rect từ góc trên trái, nên lùi lại nửa chiều dài và rộng
                ctx.rectangle(-sx_mm / 2, -sy_mm / 2, sx_mm, sy_mm)
                ctx.fill()
                
            elif pad.shape == "oval":
                # Oval (oblong) trong KiCad thường là đường thẳng nét cực dày có bo tròn 2 đầu
                width = sy_mm
                length = sx_mm - width
                
                ctx.new_path()
                ctx.set_line_width(width)
                ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                
                if length > 0:
                    ctx.move_to(-length/2, 0)
                    ctx.line_to(length/2, 0)
                else: # Trường hợp pad dựng đứng
                    length = sy_mm - sx_mm
                    ctx.set_line_width(sx_mm)
                    ctx.move_to(0, -length/2)
                    ctx.line_to(0, length/2)
                ctx.stroke()

            ctx.restore()
        """
        # ==========================================
        # 5. Lưu File
        # ==========================================
        for surface in self.surfaces:
            surface.finish()
        print("Đã xuất hoàn thiện bản mạch!")