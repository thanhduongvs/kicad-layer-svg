import math
import cairo
from kicad_pcb import KiCadPCB

class PCBSVG:
    def __init__(self, kicad: KiCadPCB, colors: dict):
        self.kicad = kicad
        self.colors = colors
        self.surfaces = []
        self.layer_contexts = []
        
        if not kicad.box or kicad.box.minx == float('inf'):
            print("Lỗi: Không tìm thấy Bounding Box hợp lệ.")
            return

        # Hệ số phóng to và chuyển đổi Nanometer -> Pixel/Millimeter
        zoom_factor = 20
        self.SCALE = 1e-6 * zoom_factor

        # ==========================================
        # TÍNH MARGIN VÀ DỊCH CHUYỂN HỆ TỌA ĐỘ
        # ==========================================
        max_edge_width = 0
        if self.kicad.pcbdata.edge_cuts:
            max_edge_width = max(edge.width for edge in self.kicad.pcbdata.edge_cuts)
        
        if max_edge_width == 0:
            max_edge_width = 100000 # 0.1mm
            
        margin_nm = 2 * max_edge_width

        # 1. Kích thước mặt giấy = Kích thước bo mạch + (2 * lề)
        dx_px = ((kicad.box.maxx - kicad.box.minx) + 2 * margin_nm) * self.SCALE
        dy_px = ((kicad.box.maxy - kicad.box.miny) + 2 * margin_nm) * self.SCALE

        self.layer_id_to_idx = {l.id: i for i, l in enumerate(self.kicad.stackup)}

        # Tính khoảng lề bằng pixel để dịch chuyển
        margin_px = margin_nm * self.SCALE

        for layer_info in self.kicad.stackup:
            filename = f"{layer_info.name}.svg"
            
            surface = cairo.SVGSurface(filename, dx_px, dy_px)
            ctx = cairo.Context(surface)
            
            # 2. Dịch chuyển toàn bộ hệ tọa độ sang phải và xuống dưới một khoảng bằng lề
            ctx.translate(margin_px, margin_px)
            
            self.layer_contexts.append(ctx)
            self.surfaces.append(surface)
        
        #self.draw()

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
            #ctx.set_source_rgb(0.0, 0.0, 0.0) # Màu đen
            ctx.set_source_rgba(*self.colors.get('Track', (0.0, 0.0, 0.0, 1.0)))
            
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
            #ctx.set_source_rgb(0.0, 0.0, 0.0) # Màu đen
            ctx.set_source_rgba(*self.colors.get('Track', (0.0, 0.0, 0.0, 1.0)))
            
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
                #ctx.set_source_rgb(0.8, 0.6, 0.2) # Màu đồng
                # Lấy màu Via (mặc định xanh nếu lỗi)
                ctx.set_source_rgba(*self.colors.get('Via', (0.2, 0.8, 0.2, 1.0)))
                
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
            
            #color = getattr(self, 'net_to_color', {}).get(pad.name, (0.8, 0.2, 0.2))
            #ctx.set_source_rgb(*color) 
            ctx.set_source_rgba(*self.colors.get('Pad', (0.8, 0.6, 0.2, 1.0)))
            
            ctx.translate(px_mm, py_mm)
            if pad.angle != 0:
                ctx.rotate(math.radians(-pad.angle))
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
                w = pad.size.x * self.SCALE
                h = pad.size.y * self.SCALE
                
                # Tính khoảng cách vát góc (dựa trên cạnh ngắn nhất)
                chamfer_d = pad.chamfer_ratio * min(w, h)
                
                # Xác định tọa độ 4 biên so với tâm (0, 0)
                left = -w / 2
                right = w / 2
                top = -h / 2
                bottom = h / 2
                
                ctx.new_path() # Bắt đầu vẽ path mới
                
                # 1. Góc trên-trái (Top-Left)
                if 'top_left' in pad.chamfered_corners:
                    ctx.move_to(left, top + chamfer_d)
                    ctx.line_to(left + chamfer_d, top)
                else:
                    ctx.move_to(left, top)
                    
                # 2. Góc trên-phải (Top-Right)
                if 'top_right' in pad.chamfered_corners:
                    ctx.line_to(right - chamfer_d, top)
                    ctx.line_to(right, top + chamfer_d)
                else:
                    ctx.line_to(right, top)
                    
                # 3. Góc dưới-phải (Bottom-Right)
                if 'bottom_right' in pad.chamfered_corners:
                    ctx.line_to(right, bottom - chamfer_d)
                    ctx.line_to(right - chamfer_d, bottom)
                else:
                    ctx.line_to(right, bottom)
                    
                # 4. Góc dưới-trái (Bottom-Left)
                if 'bottom_left' in pad.chamfered_corners:
                    ctx.line_to(left + chamfer_d, bottom)
                    ctx.line_to(left, bottom - chamfer_d)
                else:
                    ctx.line_to(left, bottom)
                    
                ctx.close_path() # Đóng path (tự động nối về điểm bắt đầu)
                # ctx.fill() # Gọi hàm fill() ở ngoài khối if-elif nếu bạn đang gộp chung
            # rectangle
            else:
                ctx.rectangle(-sx_mm / 2, -sy_mm / 2, sx_mm, sy_mm)

            # --- ĐỤC LỖ KHOAN CHO PAD PTH ---
            if pad.drill_size and (pad.drill_size.x > 0 or pad.drill_size.y > 0):
                # Dịch ngược offset để lỗ khoan nằm đúng tâm thực của Pad
                ctx.translate(-off_x_mm, -off_y_mm)
                
                dx_mm = pad.drill_size.x * self.SCALE
                dy_mm = pad.drill_size.y * self.SCALE
                
                ctx.new_sub_path()
                
                # Bỏ qua biến drill_shape, chỉ cần x khác y là lỗ oval (slotted hole)
                if dx_mm != dy_mm:
                    self._create_oval_path(ctx, dx_mm, dy_mm)
                else:
                    drill_d = max(dx_mm, dy_mm)
                    ctx.arc(0, 0, drill_d / 2, 0, 2*math.pi)
                
            # --- CHỈ GỌI FILL MỘT LẦN DUY NHẤT Ở CUỐI ---
            ctx.fill()
            ctx.restore()

        # ==========================================
        # 5. VẼ EDGE CUTS (Đường viền bo mạch)
        # ==========================================
        for edge in self.kicad.pcbdata.edge_cuts:
            # Quy đổi tọa độ và kích thước sang pixel
            w_mm = edge.width * self.SCALE
            if w_mm == 0:
                w_mm = 0.1 * 1e6 * self.SCALE  # Đề phòng width = 0 thì cho nét vẽ mặc định
                
            sx_mm = (edge.start.x - minx) * self.SCALE
            sy_mm = (edge.start.y - miny) * self.SCALE
            ex_mm = (edge.end.x - minx) * self.SCALE
            ey_mm = (edge.end.y - miny) * self.SCALE

            # Lặp qua tất cả các lớp đồng để vẽ viền bo mạch lên mọi file SVG
            for ctx in self.layer_contexts:
                ctx.save()
                #ctx.set_source_rgb(0.4, 0.4, 0.4) # Màu xám cho viền
                edge_color = self.colors.get('EdgeCuts', (0.4, 0.4, 0.4, 1.0))
                ctx.set_source_rgba(*edge_color)
                ctx.set_line_width(w_mm)
                ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                
                ctx.new_path()
                
                if edge.type == 'segment':
                    ctx.move_to(sx_mm, sy_mm)
                    ctx.line_to(ex_mm, ey_mm)
                    
                elif edge.type == 'rectangle':
                    # Tính chiều rộng và chiều cao của hình chữ nhật
                    rect_w = ex_mm - sx_mm
                    rect_h = ey_mm - sy_mm
                    ctx.rectangle(sx_mm, sy_mm, rect_w, rect_h)
                
                elif edge.type == 'arc':
                    # Tính toán tọa độ tâm, điểm giữa và bán kính ra Pixel
                    cx = (edge.center.x - minx) * self.SCALE
                    cy = (edge.center.y - miny) * self.SCALE
                    mx = (edge.mid.x - minx) * self.SCALE
                    my = (edge.mid.y - miny) * self.SCALE
                    r_mm = edge.radius * self.SCALE
                    
                    # Tính các góc radian
                    start_rad = math.atan2(sy_mm - cy, sx_mm - cx)
                    end_rad = math.atan2(ey_mm - cy, ex_mm - cx)
                    mid_rad = math.atan2(my - cy, mx - cx)

                    # Xác định chiều quay
                    diff1 = (mid_rad - start_rad) % (2 * math.pi)
                    diff2 = (end_rad - mid_rad) % (2 * math.pi)
                    is_clockwise = (diff1 + diff2) < (2 * math.pi + 1e-4)

                    # Vẽ cung tròn
                    if is_clockwise:
                        ctx.arc(cx, cy, r_mm, start_rad, end_rad)
                    else:
                        ctx.arc_negative(cx, cy, r_mm, start_rad, end_rad)
                elif edge.type == 'circle':
                    # Tính toán tọa độ tâm và bán kính ra Pixel
                    cx_mm = (edge.center.x - minx) * self.SCALE
                    cy_mm = (edge.center.y - miny) * self.SCALE
                    r_mm = edge.radius * self.SCALE
                    
                    # ctx.arc(tâm_x, tâm_y, bán_kính, góc_bắt_đầu, góc_kết_thúc)
                    # 2 * math.pi tương đương 360 độ (một vòng tròn khép kín)
                    ctx.arc(cx_mm, cy_mm, r_mm, 0, 2 * math.pi)
                ctx.stroke()
                ctx.restore()
                
        # ==========================================
        # 6. XÓA TRACK ĐI QUA LỖ KHOAN (HOLES)
        # Tối ưu: Gom Path và chỉ fill() 1 lần duy nhất để tránh lỗi lồng mask trên SVG
        # ==========================================
        
        # 6.0. Khởi tạo path trống trên tất cả các layer
        for ctx in self.layer_contexts:
            ctx.new_path()

        # 6.1. Gom lỗ khoan của Vias
        for via in self.kicad.pcbdata.vias:
            vx_mm = (via.pos.x - minx) * self.SCALE
            vy_mm = (via.pos.y - miny) * self.SCALE
            drill_mm = via.drill * self.SCALE

            for layer_id in via.layers:
                idx = self.layer_id_to_idx.get(layer_id, -1)
                if idx == -1: continue
                
                ctx = self.layer_contexts[idx]
                ctx.new_sub_path() # QUAN TRỌNG: Ngắt nét để các lỗ tròn không bị nối dây với nhau
                ctx.arc(vx_mm, vy_mm, drill_mm / 2, 0, 2 * math.pi)

        # 6.2. Gom lỗ khoan của Pads (Chân PTH)
        for pad in self.kicad.pcbdata.pads:
            if not getattr(pad, 'drill_size', None):
                continue
                
            dx_mm = pad.drill_size.x * self.SCALE
            dy_mm = pad.drill_size.y * self.SCALE
            
            if dx_mm > 0 or dy_mm > 0:
                pad_layers = getattr(pad, 'layers', [])
                if not pad_layers:
                    single_layer = getattr(pad, 'layer', None)
                    pad_layers = [single_layer] if single_layer else []

                target_indices = set()
                for layer_id in pad_layers:
                    if layer_id == '*.Cu':
                        target_indices.update(self.layer_id_to_idx.values())
                    else:
                        idx = self.layer_id_to_idx.get(layer_id, -1)
                        if idx != -1:
                            target_indices.add(idx)

                px_mm = (pad.pos.x - minx) * self.SCALE
                py_mm = (pad.pos.y - miny) * self.SCALE

                for idx in target_indices:
                    if idx < 0 or idx >= len(self.layer_contexts): 
                        continue
                        
                    ctx = self.layer_contexts[idx]
                    
                    # Dùng matrix thay vì save()/restore() để KHÔNG LÀM MẤT các path vừa gom ở trên
                    original_matrix = ctx.get_matrix()
                    
                    ctx.translate(px_mm, py_mm)
                    if getattr(pad, 'angle', 0) != 0:
                        ctx.rotate(math.radians(-pad.angle))
                    
                    ctx.new_sub_path() # Ngắt nét
                    if dx_mm != dy_mm: 
                        # Lưu ý: Trong hàm self._create_oval_path của bạn KHÔNG ĐƯỢC có dòng ctx.new_path()
                        self._create_oval_path(ctx, dx_mm, dy_mm)
                    else:              
                        drill_d = max(dx_mm, dy_mm)
                        ctx.arc(0, 0, drill_d / 2, 0, 2 * math.pi)
                    
                    ctx.set_matrix(original_matrix) # Trả lại ma trận tọa độ không gian thực

        # 6.3. THỰC THI "CỤC TẨY" VÀ FILL (Chỉ làm 1 lần cho mỗi context)
        for ctx in self.layer_contexts:
            # Kiểm tra nếu có nét vẽ nào đã được gom thì mới fill
            if ctx.has_current_point():
                ctx.save()
                ctx.set_operator(cairo.OPERATOR_DEST_OUT)
                ctx.fill()
                ctx.restore()

        # ==========================================
        # 7. Lưu File
        # ==========================================
        for surface in self.surfaces:
            surface.finish()
        print("Đã xuất hoàn thiện bản mạch!")

    def _create_oval_path(self, ctx, w, h):
        """Tạo đường dẫn hình bầu dục (Pill shape) chuẩn xác"""
        r = min(w, h) / 2
        if w > h:
            l = (w / 2) - r
            ctx.move_to(-l, -r)         # Điểm bắt đầu: Góc trên-trái
            ctx.line_to(l, -r)          # Kéo đường thẳng qua góc trên-phải
            ctx.arc(l, 0, r, -math.pi/2, math.pi/2)    # Cung bên phải
            ctx.line_to(-l, r)          # Kéo đường thẳng về góc dưới-trái
            ctx.arc(-l, 0, r, math.pi/2, 3*math.pi/2)  # Cung bên trái
        else:
            t = (h / 2) - r
            ctx.move_to(r, -t)          # Điểm bắt đầu: Góc trên-phải
            ctx.line_to(r, t)           # Kéo đường thẳng xuống góc dưới-phải
            ctx.arc(0, t, r, 0, math.pi)               # Cung bên dưới
            ctx.line_to(-r, -t)         # Kéo đường thẳng lên góc trên-trái
            ctx.arc(0, -t, r, math.pi, 2*math.pi)      # Cung bên trên
            
        ctx.close_path()