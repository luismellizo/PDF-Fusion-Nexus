from pdf2docx import Converter as PDF2DocxConverter
import fitz


class Converter:
    def __init__(self, file_path):
        self.file_path = file_path

    def convert(self, output_file, start=0, end=None):
        try:
            print("Converting PDF to Word...")
            print("Input file:", self.file_path)
            print("Output file:", output_file)

            # Realizar la conversión usando pdf2docx
            cv = PDF2DocxConverter(self.file_path)
            cv.convert(output_file, start=start, end=end)
            cv.close()

            print("Archivo convertido exitosamente.")
        except Exception as e:
            print("Error al convertir el archivo:", str(e))

    def close(self):
        # Perform any necessary cleanup or finalization steps here
        try:
            print("Closing the converter...")
        except Exception as e:
            print("Error al cerrar el convertidor:", str(e))
