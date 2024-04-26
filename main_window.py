import os
from converter import Converter
import subprocess
import os.path
import sys
import zipfile
import webbrowser
from PyQt5.QtWidgets import QMessageBox, QApplication, QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QFileDialog, QMenu, QAction, QDialog, QFrame, QSplitter, QToolBar, QToolButton, QAbstractItemView, QScrollArea
from PyQt5.QtGui import QFontDatabase, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QEvent, QUrl, QRect, QPropertyAnimation
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
from PyPDF2 import PdfFileReader, PdfMerger, PdfReader, PdfFileWriter
from docx import Document
from docx.shared import Inches
from pdf2docx import Converter as PDF2DocxConverter
import fitz
from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PyQt5.QtCore import QSize
# Importaciones específicas de PDFViewerWindow y PDorganizar (¿Módulos propios?)
from PDFViewerWindow import PDFViewerWindow
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Ajusta este valor entre 0 (completamente transparente) y 1 (opaco)
        self.setWindowOpacity(0.9)

        self.archivos_seleccionados = []

        self.layout = QVBoxLayout()
        self.dragged_file_path = None  # Ruta del archivo arrastrado

        self.label_drag = QLabel(
            "Mover archivos PDF para ordenarlos")
        self.label_drag.setAlignment(Qt.AlignCenter)
        self.label_drag.setStyleSheet(
            "color: #B22222; font-size: 22px; margin: 20px;")
        self.layout.addWidget(self.label_drag)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.list_widget.setStyleSheet(
            "QListWidget { background-color: #333333; color: #CCCCCC; border: 2px solid #666666; border-radius: 10px; padding: 20px; }"
            "QListWidget::item { border-bottom: 1px solid #666666; }"
            "QListWidget::item:selected { background-color: #B22222; }"
        )
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        self.layout.addWidget(self.list_widget)

        self.boton_combinar = QPushButton("COMBINAR PDF")
        self.boton_combinar.setStyleSheet(
            "QPushButton { background-color: #666666; color: #CCCCCC; border: 2px solid #666666; border-radius: 10px; padding: 10px; }"
            "QPushButton:hover { background-color: #B22222; border: 2px solid #555555; }"
        )
        self.boton_combinar.clicked.connect(self.combinar_archivos)
        self.layout.addWidget(self.boton_combinar)

        self.setLayout(self.layout)

        self.setAcceptDrops(True)

        self.set_estilo_ventana()

        # Instala un filtro de eventos en la lista de archivos
        self.list_widget.installEventFilter(self)

        self.boton_word = QPushButton("CONVERTIR A WORD")
        self.boton_word.setStyleSheet(
            "QPushButton { background-color: #666666; color: #CCCCCC; border: 2px solid #666666; border-radius: 10px; padding: 10px; }"
            "QPushButton:hover { background-color: #B22222; border: 2px solid #555555; }"
        )
        self.boton_word.clicked.connect(self.convert_to_word)
        self.layout.addWidget(self.boton_word)

        self.label_contador = QLabel("Archivos cargados: 0")
        self.label_contador.setStyleSheet(
            "color: #CCCCCC; font-size: 16px; margin-top: 10px;")
        self.layout.addWidget(self.label_contador)

        # Puedes continuar con el resto de tu código aquí...
        # Establecer el estilo de la ventana
        # Cambiar lightblue al color que desees
        self.setStyleSheet("background-color: lightblue;")

        # Botón de PayPal
        self.boton_paypal = QPushButton(self)
        # Ajusta la ruta si es necesario
        self.boton_paypal.setIcon(QIcon('paypal.ico'))
        # Ajusta el tamaño del ícono
        self.boton_paypal.setIconSize(QSize(64, 64))
        self.boton_paypal.setFixedSize(64, 24)  # Fija el tamaño del botón
        self.boton_paypal.clicked.connect(self.abrir_paypal)

        # Agregar bordes al botón
        self.boton_paypal.setStyleSheet(
            "border: 5px solid black; border-radius: 8px;")

        self.layout.addWidget(self.boton_paypal)

        # Código adicional para la ventana principal
        self.setWindowTitle("PDF Fusion Nexus")
        self.setWindowIcon(QIcon('icono.ico'))
        self.setGeometry(100, 100, 400, 800)

    def set_estilo_ventana(self):
        self.setStyleSheet(
            "QWidget { background-color: #222222; }"
        )

    def set_estilo_ventana(self):
        # Establecer el fondo de la ventana al color #242424
        self.setAutoFillBackground(True)
        palette = self.palette()
        # Aquí se cambian los valores RGB
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)

        # Cambiar el color de las letras a blanco
        self.setStyleSheet("QLabel { color: white; }")

        # Cambiar el color de los bordes a verde
        self.setStyleSheet("QWidget { border: 2px solid #B22222; }")

    def convert_to_word(self):
        if len(self.archivos_seleccionados) == 0:
            print("No hay archivos seleccionados para convertir.")
            return

        try:
            for archivo_pdf in self.archivos_seleccionados:
                # Generar el nombre del archivo de Word de salida
                nombre, _ = os.path.splitext(archivo_pdf)
                nuevo_archivo = nombre + ".docx"

                # Crear un objeto Converter
                convertidor = Converter(archivo_pdf)

                # Convertir el PDF a Word
                convertidor.convert(nuevo_archivo, start=0, end=None)

                # Cerrar el convertidor
                convertidor.close()

                print(
                    f"Archivo '{archivo_pdf}' convertido exitosamente a '{nuevo_archivo}'.")
        except Exception as e:
            print(f"Error al convertir el archivo: {str(e)}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def eventFilter(self, obj, event):
        if obj is self.list_widget:
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
                    self.eliminar_archivos_seleccionados()
                    return True
            elif event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    index = self.list_widget.indexAt(event.pos())
                    if index.isValid():
                        self.list_widget.startDrag(Qt.MoveAction)
                        return True
            elif event.type() == QEvent.DragEnter:
                if event.mimeData().hasUrls():
                    event.acceptProposedAction()
                    return True
            elif event.type() == QEvent.DragMove:
                event.acceptProposedAction()
                return True
            elif event.type() == QEvent.Drop:
                urls = event.mimeData().urls()
                archivos = [url.toLocalFile()
                            for url in urls if url.isLocalFile()]
                self.archivos_seleccionados.extend(archivos)
                self.actualizar_lista_archivos()
                event.acceptProposedAction()
                return True
            elif event.type() == QEvent.Drop:
                mimeData = event.mimeData()
                if mimeData.hasFormat("application/x-qabstractitemmodeldatalist"):
                    data = mimeData.data(
                        "application/x-qabstractitemmodeldatalist")
                    stream = QDataStream(data)
                    while not stream.atEnd():
                        row, col, _ = stream.readInt(), stream.readInt(), stream.readInt()
                        index = self.list_widget.model().index(row, col)
                        archivo = self.list_widget.model().data(index, Qt.DisplayRole)
                        self.archivos_seleccionados.insert(row, archivo)
                    self.actualizar_lista_archivos()
                    event.acceptProposedAction()
                    return True
        return super().eventFilter(obj, event)

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        archivos = [url.toLocalFile() for url in urls if url.isLocalFile()]
        self.archivos_seleccionados.extend(archivos)
        self.actualizar_lista_archivos()

        if archivos:
            archivo_seleccionado = archivos[0]
            self.ver_archivo(archivo_seleccionado)

    def actualizar_lista_archivos(self):
        # Limpiar la lista actual en el widget
        self.list_widget.clear()

        # Agregar elementos a la lista widget
        for archivo in self.archivos_seleccionados:
            # Solo agrega el nombre del archivo
            self.list_widget.addItem(os.path.basename(archivo))

        # Actualizar el contador de archivos cargados
        self.label_contador.setText(
            f"Archivos cargados: {len(self.archivos_seleccionados)}")

    def combinar_archivos(self):
        if len(self.archivos_seleccionados) == 0:
            print("No hay archivos seleccionados para combinar.")
            return

        merger = PdfMerger()

        # Append files to the merger based on the current order in self.archivos_seleccionados
        for url in self.archivos_seleccionados:
            merger.append(url)

        ruta_combinado, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo combinado", "", "Archivos PDF (*.pdf)")

        if ruta_combinado:
            merger.write(ruta_combinado)
            merger.close()
            print("Archivos combinados exitosamente.")

    def limpiar_archivos(self):
        self.archivos_seleccionados = []
        self.actualizar_list_widget()

    def eliminar_archivo(self):
        indices = [index.row() for index in self.list_widget.selectedIndexes()]
        indices.sort(reverse=True)
        for indice in indices:
            del self.archivos_seleccionados[indice]
        self.actualizar_lista_archivos()  # Corregido aquí

    def contextMenuEvent(self, event):
        if len(self.list_widget.selectedItems()) > 0:
            menu = QMenu(self)
            ver_action = QAction("Ver", self)
            eliminar_action = QAction("Eliminar", self)

            # Conectar a la función de la clase
            ver_action.triggered.connect(self.ver_archivo)

            # Conectar a la función de la clase
            eliminar_action.triggered.connect(self.eliminar_archivo)

            menu.addAction(ver_action)

            menu.addAction(eliminar_action)

            style = """
            QMenu {
                background-color: #222222;
                
                border-radius: 40px;
            }

            QMenu::item {
                color: white;
                padding: 10px;
            }

            QMenu::item:selected {
                background-color: #B22222;
                border-radius: 40px;
            }

            QMenu::separator {
                height: 2px;
                background-color: #007F00;
                margin-left: 10px;
                margin-right: 10px;
            }
            """
            menu.setStyleSheet(style)

            menu.exec_(event.globalPos())
        else:
            event.ignore()

    def abrir_pdf(self, item):
        if not self.archivos_seleccionados:
            return

        archivo = self.archivos_seleccionados[self.list_widget.row(item)]
        pdf_viewer = PDFViewerWindow(archivo)
        pdf_viewer.exec_()

    def ver_archivo(self):
        if len(self.list_widget.selectedItems()) == 0:
            return

        indice_seleccionado = self.list_widget.currentRow()
        archivo_seleccionado = self.archivos_seleccionados[indice_seleccionado]

        # Abrir el visor de PDF dentro de la aplicación
        pdf_viewer = PDFViewerWindow(archivo_seleccionado)
        pdf_viewer.exec_()

    def eliminar_archivos_seleccionados(self):
        indices = [index.row() for index in self.list_widget.selectedIndexes()]
        indices.sort(reverse=True)
        for indice in indices:
            del self.archivos_seleccionados[indice]
        self.actualizar_lista_archivos()  # Corregido aquí

    def abrir_paypal(self):
        QDesktopServices.openUrl(QUrl("https://www.paypal.me/luismellizo"))
