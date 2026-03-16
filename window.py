from PySide6.QtWidgets import (QMainWindow, QMessageBox, QColorDialog, 
                               QTableWidgetItem, QPushButton, QHeaderView)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor
from gui import Ui_MainWindow
from kicad_pcb import KiCadPCB
from version import version
from pcbsvg import PCBSVG

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(f"Layer SVG v{version}")
        self.pcb = KiCadPCB()

        # 1. Khởi tạo dữ liệu màu mặc định (RGB dạng float 0.0 - 1.0)
        self.pcb_colors = {
            'Track': (0.8, 0.1, 0.1, 1.0),
            'Pad': (0.8, 0.6, 0.2, 1.0),
            'Via': (0.2, 0.8, 0.2, 1.0)
        }

        # 2. Setup bảng chọn màu
        self.setup_color_table()

        QTimer.singleShot(500, self.connect_kicad)
        self.ui.buttonClose.clicked.connect(self.close)
        self.ui.buttonConnect.clicked.connect(self.connect_kicad)
        self.ui.buttonRun.clicked.connect(self.button_run_clicked)
        #self.ui.buttonColor.clicked.connect(self.button_color_clicked)
    
    def setup_color_table(self):
        # Thiết lập số hàng, cột và tiêu đề
        self.ui.tableWidget.setRowCount(len(self.pcb_colors))
        self.ui.tableWidget.setColumnCount(2)
        self.ui.tableWidget.setHorizontalHeaderLabels(["Item", "Color"])
        
        # Căn chỉnh kích thước cột
        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.tableWidget.verticalHeader().setVisible(False)

        # Đổ dữ liệu vào bảng
        for row, (item_name, color_tuple) in enumerate(self.pcb_colors.items()):
            # Cột 1: Tên thành phần (Khóa không cho chỉnh sửa text)
            name_item = QTableWidgetItem(item_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget.setItem(row, 0, name_item)

            # Cột 2: Nút bấm hiển thị màu
            color_btn = QPushButton()
            self._update_button_style(color_btn, color_tuple)
            
            # Gắn sự kiện click
            color_btn.clicked.connect(lambda checked=False, name=item_name, btn=color_btn: self.pick_color(name, btn))
            
            self.ui.tableWidget.setCellWidget(row, 1, color_btn)

    def pick_color(self, element_name, button):
        current_color = QColor.fromRgbF(*self.pcb_colors[element_name])
        color = QColorDialog.getColor(
            initial=current_color, 
            parent=self, 
            title=f"Chọn màu cho {element_name}"
        )

        if color.isValid():
            r, g, b, a = color.getRgbF()
            self.pcb_colors[element_name] = (r, g, b, a)
            self._update_button_style(button, self.pcb_colors[element_name])
            print(f"Đã cập nhật màu {element_name}: RGB({r:.2f}, {g:.2f}, {b:.2f})")

    def _update_button_style(self, button, rgba_tuple):
        c = QColor.fromRgbF(*rgba_tuple)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {c.name()}; 
                border: 1px solid #555;
                border-radius: 4px;
                margin: 2px;
            }}
        """)

    def connect_kicad(self):
        connected, status = self.pcb.connect_kicad()
        if connected:
            self.ui.statusbar.showMessage(f"Connected to KiCad {self.pcb.kicad.get_version()}")
        else:
            self.ui.statusbar.showMessage(status)
            QMessageBox.information(self, "Message", status)

    def button_run_clicked(self):
        status = self.pcb.get_data()
        if status == False:
            QMessageBox.information(self, "Message", "Please add Edge Cuts")
            return
            
        # TODO: Bạn có thể truyền self.pcb_colors vào PCBSVG tại đây
        PCBSVG(self.pcb)
        print("Done")
    
    def button_color_clicked(self):
        # Nút Color trên giao diện hiện tại có thể dùng để reset màu, 
        # hoặc in ra thông số màu hiện tại để debug
        print("Màu hiện tại đang lưu:", self.pcb_colors)