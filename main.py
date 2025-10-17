import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileSystemModel, QTreeView, QSplitter,
    QScrollArea, QToolBar, QStyle, QLineEdit, QHeaderView
)
from PySide6.QtGui import QIcon, QAction, QPixmap, QImage
from PySide6.QtCore import Qt, QDir, QSize

import fitz
from hzs_utils import HZSFileHelper, hzs_format_path


class HungarianFileSystemModel(QFileSystemModel):
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            headers = ["Név", "Méret", "Típus", "Módosítva"]
            if section < len(headers):
                return headers[section]
        return super().headerData(section, orientation, role)


class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_pdf = None
        self.current_page = 0
        self.zoom_level = 1.0
        self.initUI()

    def initUI(self):
        self.setWindowTitle(' HZS PDF Megjelenítő 1.0')
        self.setWindowIcon(QIcon("ikon.ico"))
        self.setGeometry(100, 100, 1400, 820)
        self.apply_style()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Fájlrendszer modell
        self.file_model = HungarianFileSystemModel()
        self.file_model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
        self.file_model.setNameFilters(["*.pdf"])
        self.file_model.setNameFilterDisables(False)
        self.file_model.setRootPath('')

        # TreeView
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(''))
        self.tree_view.setHeaderHidden(False)
        self.tree_view.setColumnWidth(0, 300)
        self.tree_view.clicked.connect(self.on_tree_clicked)

        # Ez a rész expandálná a meghajtókat automatikusan:
        # import ctypes
        # def list_windows_drives():
        #     drives = []
        #     bitmask = ctypes.cdll.kernel32.GetLogicalDrives()
        #     for i in range(26):
        #         if bitmask & (1 << i):
        #             drives.append(f"{chr(65 + i)}:/")
        #     return drives
        #
        # drives = list_windows_drives()
        # for drive in drives:
        #     idx = self.file_model.setRootPath(drive)
        #     self.tree_view.expand(idx)  # <- Ez nyitja ki
        #     self.tree_view.setExpanded(idx, True)

        # Windows-szerű "Ez a gép" címke
        root_label = QLabel("📁 Ez a gép")
        root_label.setStyleSheet("QLabel { font-weight: bold; padding: 8px; }")

        left_layout.addWidget(root_label)
        left_layout.addWidget(self.tree_view)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(20, 20))
        prev_action = QAction(self.style().standardIcon(QStyle.SP_ArrowBack), 'Előző', self)
        next_action = QAction(self.style().standardIcon(QStyle.SP_ArrowForward), 'Következő', self)
        zoom_in_action = QAction(self.style().standardIcon(QStyle.SP_ArrowUp), 'Nagyít', self)
        zoom_out_action = QAction(self.style().standardIcon(QStyle.SP_ArrowDown), 'Kicsinyít', self)
        reset_action = QAction('100%', self)
        prev_action.triggered.connect(self.prev_page)
        next_action.triggered.connect(self.next_page)
        zoom_in_action.triggered.connect(self.zoom_in)
        zoom_out_action.triggered.connect(self.zoom_out)
        reset_action.triggered.connect(self.zoom_reset)
        toolbar.addAction(prev_action)
        toolbar.addAction(next_action)
        toolbar.addSeparator()
        toolbar.addAction(zoom_out_action)
        toolbar.addAction(reset_action)
        toolbar.addAction(zoom_in_action)
        toolbar.addSeparator()
        search_box = QLineEdit()
        search_box.setPlaceholderText('Keresés fájlnevekben...')
        search_box.textChanged.connect(self.filter_tree)
        toolbar.addWidget(search_box)
        right_layout.addWidget(toolbar)
        control_layout = QHBoxLayout()
        self.page_label = QLabel('Nincs PDF betöltve')
        self.page_label.setAlignment(Qt.AlignCenter)
        control_layout.addStretch()
        control_layout.addWidget(self.page_label)
        control_layout.addStretch()
        right_layout.addLayout(control_layout)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.pdf_label = QLabel('Válassz ki egy PDF fájlt a bal oldalról')
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.pdf_label.setStyleSheet('QLabel { background-color: #fafafa; padding: 18px; border: 1px solid #eee; }')
        self.scroll_area.setWidget(self.pdf_label)
        right_layout.addWidget(self.scroll_area)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([380, 1020])
        main_layout.addWidget(splitter)
        self.prev_btn_action = prev_action
        self.next_btn_action = next_action
        self.zoom_in_action = zoom_in_action
        self.zoom_out_action = zoom_out_action
        self.reset_action = reset_action
        self.set_buttons_enabled(False)

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #f3f6fb; }
            QLabel { font-size: 14px; color: #1b1b1b; }
            QTreeView { background: white; border: 1px solid #e6e6e6; }
            QToolBar { background: transparent; spacing: 6px; }
            QLineEdit { min-width: 200px; padding: 6px; border: 1px solid #e0e0e0; border-radius: 8px; }
            QAction { padding: 6px; }
            QPushButton { border-radius: 8px; padding: 6px 12px; }
        """)

    def set_buttons_enabled(self, enabled):
        self.prev_btn_action.setEnabled(enabled)
        self.next_btn_action.setEnabled(enabled)
        self.zoom_in_action.setEnabled(enabled)
        self.zoom_out_action.setEnabled(enabled)
        self.reset_action.setEnabled(enabled)

    def filter_tree(self, text):
        if text.strip() == '':
            self.file_model.setNameFilters(['*.pdf', '*'])
        else:
            pattern = f'*{text}*'
            self.file_model.setNameFilters([pattern])

    def on_tree_clicked(self, index):
        file_path = self.file_model.filePath(index)
        if os.path.isfile(file_path) and file_path.lower().endswith('.pdf'):
            self.load_pdf(file_path)

    def load_pdf(self, file_path):
        try:
            if self.current_pdf:
                self.current_pdf.close()
            self.current_pdf = fitz.open(file_path)
            self.current_page = 0
            self.zoom_level = 1.0
            self.set_buttons_enabled(True)
            self.display_page()
            display_path = hzs_format_path(file_path)
            self.statusBar().showMessage(display_path)
        except Exception as e:
            self.pdf_label.setText('Hiba a PDF betöltésekor')

    def display_page(self):
        if not self.current_pdf:
            return
        page = self.current_pdf[self.current_page]
        mat = fitz.Matrix(self.zoom_level, self.zoom_level)
        pix = page.get_pixmap(matrix=mat)
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        self.pdf_label.setPixmap(pixmap)
        self.pdf_label.resize(pixmap.size())
        self.page_label.setText(f'Oldal {self.current_page + 1} / {len(self.current_pdf)}')
        self.prev_btn_action.setEnabled(self.current_page > 0)
        self.next_btn_action.setEnabled(self.current_page < len(self.current_pdf) - 1)
        self.reset_action.setText(f'{int(self.zoom_level * 100)}%')

    def prev_page(self):
        if self.current_pdf and self.current_page > 0:
            self.current_page -= 1
            self.display_page()

    def next_page(self):
        if self.current_pdf and self.current_page < len(self.current_pdf) - 1:
            self.current_page += 1
            self.display_page()

    def zoom_in(self):
        if self.zoom_level < 3.0:
            self.zoom_level += 0.25
            self.display_page()

    def zoom_out(self):
        if self.zoom_level > 0.5:
            self.zoom_level -= 0.25
            self.display_page()

    def zoom_reset(self):
        self.zoom_level = 1.0
        self.display_page()

    def closeEvent(self, event):
        if self.current_pdf:
            self.current_pdf.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec())