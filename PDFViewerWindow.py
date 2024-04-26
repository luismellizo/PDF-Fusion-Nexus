from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QPushButton, QFileDialog, QMenu, QAction, QWidget, QMainWindow, QScrollArea
)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QSize, QPoint, QPointF

import fitz
import cv2
import numpy as np
from PIL import Image


class PDFViewerWindow(QDialog):
    def __init__(self, archivo=None):
        super().__init__()
        self.setWindowTitle("Visor de PDF")

        # Establecer tamaño fijo de la ventana
        self.resize(1000, 835)

        # Establecer color de fondo de la ventana
        self.setStyleSheet("""
            background-color: #222222;
            border: 0px;
            border-radius: 10px;
        """)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        self.label = QLabel(self)
        self.scroll_area.setWidget(self.label)

        self.current_page = 0
        self.doc = None
        self.original_pixmap = None
        self.zoom_factor = 1.0
        self.ctrl_pressed = False
        self.alt_pressed = False

        self.page_counter_label = QLabel("Página 1 de 1", self)
        self.page_counter_label.setAlignment(Qt.AlignCenter)
        self.page_counter_label.setStyleSheet("color: white; font-size: 15px;")

        self.layout.addWidget(self.page_counter_label)

        if archivo:
            self.load_pdf(archivo)

        # Agregar botones "Siguiente" y "Anterior" al visor
        button_layout = QHBoxLayout()
        self.layout.addLayout(button_layout)

        boton_anterior = QPushButton("Anterior", self)
        boton_anterior.setStyleSheet("""
            background-color: #666666;
            color: #CCCCCC;
            border: 2px solid #666666;
            border-radius: 10px;
            padding: 10px;
        """)
        boton_anterior.setCursor(
            Qt.PointingHandCursor)  # Cambiar el cursor al pasar sobre el botón
        boton_anterior.clicked.connect(self.pagina_anterior)
        button_layout.addWidget(boton_anterior)

        boton_siguiente = QPushButton("Siguiente", self)
        boton_siguiente.setStyleSheet("""
            background-color: #666666;
            color: #CCCCCC;
            border: 2px solid #666666;
            border-radius: 10px;
            padding: 10px;
        """)
        boton_siguiente.setCursor(
            Qt.PointingHandCursor)  # Cambiar el cursor al pasar sobre el botón
        boton_siguiente.clicked.connect(self.pagina_siguiente)
        button_layout.addWidget(boton_siguiente)

    def load_pdf(self, archivo):
        self.doc = fitz.open(archivo)
        self.show_page(0)  # Mostrar la primera página por defecto
        self.original_pixmap = self.label.pixmap().copy()  # Guardar la imagen original
        self.update_page_counter()  # Actualizar el contador de páginas

    def show_page(self, page_index):
        if 0 <= page_index < len(self.doc):
            self.current_page = page_index
            page = self.doc[self.current_page]

            # Ajustar el zoom para una mayor resolución (por ejemplo, 3x)
            zoom_matrix = fitz.Matrix(3, 3)

            # Obtener la imagen de alta resolución
            # No aplicar escala de grises
            pix = page.get_pixmap(matrix=zoom_matrix, alpha=False)

            # Convertir la superficie a QImage y luego a QPixmap con formato RGB888
            image = QImage(pix.samples, pix.width, pix.height,
                           pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)

            # Escalar el pixmap al tamaño deseado
            desired_width = 3048
            desired_height = 1250
            scaled_pixmap = pixmap.scaled(
                desired_width, desired_height, aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)

            self.label.setPixmap(scaled_pixmap)
            # Actualizar la imagen original al cambiar de página
            self.original_pixmap = scaled_pixmap.copy()
            self.update_page_counter()  # Actualizar el contador de páginas al cambiar de página

    def pagina_anterior(self):
        self.show_page(self.current_page - 1)

    def pagina_siguiente(self):
        self.show_page(self.current_page + 1)

    def update_page_counter(self):
        if self.doc:
            total_pages = len(self.doc)
            current_page_number = self.current_page + 1
            self.page_counter_label.setText(
                f"Página {current_page_number} de {total_pages}")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = PDFViewerWindow("ruta_al_archivo.pdf")
    window.show()
    sys.exit(app.exec_())
