import sys
import json
import os
import shutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QTextEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QFileDialog, QMessageBox, QHeaderView
)

DATA_FILE = "data.json"
IMAGES_DIR = "images"

class ProductManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🦖 Khủng Long Cười - DIY 3D Tô Màu")
        self.resize(950, 680)
        self.editing_product_id = None 
        self.scanned_images = [] 
        
        self.init_ui()
        self.load_data_to_table()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # --- CỘT TRÁI: FORM NHẬP / SỬA LIỆU ---
        form_layout = QVBoxLayout()
        
        self.form_title = QLabel("<b>Thêm Sản Phẩm Mới (Tự Động Gom Folder)</b>")
        self.form_title.setStyleSheet("font-size: 14px; color: #2C3E2D;")
        form_layout.addWidget(self.form_title)
        
        form_layout.addWidget(QLabel("Tên sản phẩm:"))
        self.name_input = QLineEdit()
        form_layout.addWidget(self.name_input)
        
        form_layout.addWidget(QLabel("Giá sản phẩm (VD: 120.000 đ):"))
        self.price_input = QLineEdit()
        form_layout.addWidget(self.price_input)
        
        folder_layout = QHBoxLayout()
        self.folder_path_input = QLineEdit()
        self.folder_path_input.setPlaceholderText("Chọn thư mục chứa ảnh của mẫu...")
        self.folder_path_input.setReadOnly(True)
        
        btn_browse_folder = QPushButton("Chọn Thư Mục...")
        btn_browse_folder.clicked.connect(self.browse_product_folder)
        folder_layout.addWidget(self.folder_path_input)
        folder_layout.addWidget(btn_browse_folder)
        
        form_layout.addWidget(QLabel("Thư mục tài nguyên (Tự động lọc 1.jpg, 2.jpg...):"))
        form_layout.addLayout(folder_layout)
        
        self.lbl_status_img = QLabel("📸 Chưa chọn thư mục ảnh nào.")
        self.lbl_status_img.setStyleSheet("color: #666; font-style: italic;")
        form_layout.addWidget(self.lbl_status_img)
        
        form_layout.addWidget(QLabel("Mô tả (Mỗi dòng một ý):"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("1 Phối 3D cao 10-12cm\n1 Vỉ màu Acrylic\n2 Cọ vẽ")
        form_layout.addWidget(self.desc_input)
        
        # Nút Hành động chính
        self.btn_save = QPushButton("Thêm Sản Phẩm Mới")
        self.btn_save.setStyleSheet("background-color: #C17F6A; color: white; font-weight: bold; padding: 12px; border-radius: 5px;")
        self.btn_save.clicked.connect(self.save_product)
        form_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("Hủy / Làm mới form")
        self.btn_cancel.clicked.connect(self.clear_form)
        form_layout.addWidget(self.btn_cancel)
        
        # --- THÊM NÚT CẬP NHẬT LÊN WEB Ở DƯỚI CÙNG CỘT TRÁI ---
        form_layout.addSpacing(15)
        btn_deploy_web = QPushButton("🚀 CẬP NHẬT LÊN WEB")
        btn_deploy_web.setStyleSheet("""
            background-color: #2563EB; 
            color: white; 
            font-weight: bold; 
            font-size: 15px;
            padding: 14px; 
            border-radius: 8px;
        """)
        btn_deploy_web.clicked.connect(self.deploy_to_web)
        form_layout.addWidget(btn_deploy_web)

        form_layout.addStretch()
        main_layout.addLayout(form_layout, 1)

        # --- CỘT PHẢI: BẢNG DANH SÁCH ---
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("<b>Danh Sách Sản Phẩm Trong Kho</b>"))
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Tên sản phẩm", "Giá"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.fill_form_for_edit)
        right_layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        btn_delete = QPushButton("Xóa Sản Phẩm Đã Chọn")
        btn_delete.setStyleSheet("background-color: #e63946; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        btn_delete.clicked.connect(self.delete_product)
        
        btn_refresh = QPushButton("Tải lại bảng")
        btn_refresh.clicked.connect(self.load_data_to_table)
        
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_refresh)
        right_layout.addLayout(btn_layout)
        
        main_layout.addLayout(right_layout, 2)

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return []
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_data(self, data):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_data_to_table(self):
        data = self.load_data()
        self.table.setRowCount(len(data))
        for row, item in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(item.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(str(item.get("name", ""))))
            self.table.setItem(row, 2, QTableWidgetItem(str(item.get("price", ""))))

    def browse_product_folder(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Chọn thư mục chứa tài liệu sản phẩm")
        if dir_path:
            self.folder_path_input.setText(dir_path)
            valid_exts = ('.png', '.jpg', '.jpeg', '.webp')
            all_files = os.listdir(dir_path)
            img_files = sorted([f for f in all_files if f.lower().endswith(valid_exts)])
            
            if img_files:
                self.scanned_images = [os.path.join(dir_path, f) for f in img_files]
                self.lbl_status_img.setText(f"✅ Đã nhận diện thấy {len(img_files)} ảnh: {', '.join(img_files)}")
                self.lbl_status_img.setStyleSheet("color: #2a9d8f; font-weight: bold;")
            else:
                self.scanned_images = []
                self.lbl_status_img.setText("⚠️ Không tìm thấy file ảnh nào trong thư mục này!")
                self.lbl_status_img.setStyleSheet("color: #e63946; font-weight: bold;")

    def fill_form_for_edit(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()  # <--- Đã sửa chuẩn xác ở đây
        id_item = self.table.item(row, 0)
        if not id_item:
            return
        
        prod_id = int(id_item.text())
        data = self.load_data()
        product = next((item for item in data if item.get("id") == prod_id), None)
        
        if product:
            self.editing_product_id = prod_id
            self.form_title.setText(f"<b>Đang Sửa Sản Phẩm ID: {prod_id}</b>")
            self.btn_save.setText("Lưu Cập Nhật")
            self.btn_save.setStyleSheet("background-color: #2a9d8f; color: white; font-weight: bold; padding: 12px; border-radius: 5px;")
            
            self.name_input.setText(product.get("name", ""))
            self.price_input.setText(product.get("price", ""))
            self.folder_path_input.clear()
            self.lbl_status_img.setText(f"📂 Ảnh hiện tại: {product.get('img')}")
            
            desc = product.get("desc", [])
            if isinstance(desc, list):
                self.desc_input.setPlainText("\n".join(desc))
            else:
                self.desc_input.setPlainText(str(desc))

    def save_product(self):
        name = self.name_input.text().strip()
        price = self.price_input.text().strip()
        desc_text = self.desc_input.toPlainText().strip()

        if not name or not price:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập Tên và Giá sản phẩm!")
            return

        data = self.load_data()
        
        if self.editing_product_id is not None:
            prod_id = self.editing_product_id
        else:
            prod_id = max([item.get("id", 0) for item in data], default=0) + 1

        images_rel_list = []
        main_img_rel = "images/default.jpg"

        if self.scanned_images:
            target_folder = os.path.join(IMAGES_DIR, f"sp_{prod_id}")
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            
            for src_path in self.scanned_images:
                file_name = os.path.basename(src_path)
                dest_path = os.path.join(target_folder, file_name)
                shutil.copy(src_path, dest_path)
                rel_path = f"images/sp_{prod_id}/{file_name}".replace("\\", "/")
                images_rel_list.append(rel_path)
            
            if images_rel_list:
                main_img_rel = images_rel_list[0] 

        desc_list = [line.strip() for line in desc_text.split("\n") if line.strip()]
        if not desc_list:
            desc_list = ["1 Phối 3D cao 10-12cm", "1 Vỉ màu Acrylic", "2 Cọ vẽ"]

        if self.editing_product_id is not None:
            for item in data:
                if item.get("id") == prod_id:
                    item["name"] = name
                    item["price"] = price
                    if images_rel_list: 
                        item["img"] = main_img_rel
                        item["images"] = images_rel_list
                    item["desc"] = desc_list
                    break
            msg = "Đã cập nhật sản phẩm thành công!"
        else:
            new_product = {
                "id": prod_id,
                "name": name,
                "price": price,
                "img": main_img_rel,
                "images": images_rel_list if images_rel_list else [main_img_rel],
                "desc": desc_list
            }
            data.append(new_product)
            msg = f"Đã thêm sản phẩm mới thành công (ID: {prod_id})!"

        self.save_data(data)
        self.load_data_to_table()
        self.clear_form()
        QMessageBox.information(self, "Thành công", msg)

    def delete_product(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn dòng sản phẩm cần xóa trên bảng!")
            return

        row = selected_rows.row()
        id_item = self.table.item(row, 0)
        if not id_item:
            return
        
        prod_id = int(id_item.text())

        confirm = QMessageBox.question(self, "Xác nhận xóa", f"Bạn có chắc muốn xóa sản phẩm ID: {prod_id} không?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            data = self.load_data()
            new_data = [item for item in data if item.get("id") != prod_id]
            self.save_data(new_data)
            self.load_data_to_table()
            self.clear_form()
            QMessageBox.information(self, "Thành công", "Đã xóa sản phẩm!")

    def deploy_to_web(self):
        # Kiểm tra xem thư mục hiện tại có phải là kho git không
        if not os.path.exists(".git"):
            QMessageBox.warning(
                self, 
                "Lỗi", 
                "Thư mục hiện tại chưa được khởi tạo Git!\nHãy chắc chắn bạn đang chạy ứng dụng trong thư mục mã nguồn web có liên kết với GitHub."
            )
            return

        confirm = QMessageBox.question(
            self, 
            "Xác nhận cập nhật", 
            "Bạn có chắc muốn đẩy toàn bộ thay đổi (sản phẩm mới, ảnh, data.json) lên GitHub không?", 
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                import subprocess
                
                # 1. Chạy lệnh git add .
                subprocess.run(["git", "add", "."], check=True)
                
                # 2. Chạy lệnh git commit
                commit_msg = "Auto update products via PyQt Manager"
                subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                
                # 3. Chạy lệnh git push
                result = subprocess.run(["git", "push"], capture_output=True, text=True, check=True)
                
                QMessageBox.information(
                    self, 
                    "Thành công Rực Rỡ", 
                    "🚀 Đã đẩy dữ liệu và hình ảnh lên GitHub thành công!\n\nWebsite của bạn sẽ tự động cập nhật sau 1-2 phút tới."
                )
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Lỗi Git", 
                    f"Không thể đẩy lên GitHub. Lỗi chi tiết:\n{str(e)}\n\n(Hãy chắc chắn máy tính của bạn đã cấu hình tài khoản Git/Token sẵn)."
                )

    def clear_form(self):
        self.editing_product_id = None
        self.form_title.setText("<b>Thêm Sản Phẩm Mới</b>")
        self.btn_save.setText("Thêm Sản Phẩm Mới")
        self.btn_save.setStyleSheet("background-color: #C17F6A; color: white; font-weight: bold; padding: 12px; border-radius: 5px;")
        self.name_input.clear()
        self.price_input.clear()
        self.folder_path_input.clear()
        self.desc_input.clear()
        self.scanned_images = []
        self.lbl_status_img.setText("📸 Chưa chọn thư mục ảnh nào.")
        self.lbl_status_img.setStyleSheet("color: #666; font-style: italic;")
        self.table.clearSelection()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductManagerApp()
    window.show()
    sys.exit(app.exec_())