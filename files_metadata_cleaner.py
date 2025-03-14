import os
import glob
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from pathlib import Path
import shutil


def picture_exif_data_handle(image_path):
    try:
        image = Image.open(image_path)

        if image.format == "JPEG":
            image_data = image.getdata()
            clean_image = Image.new(image.mode, image.size)
            clean_image.putdata(image_data)
            clean_image.save(image_path, "JPEG")
        elif image.format == "PNG":
            if isinstance(image, PngImageFile):
                image.save(image_path, "PNG")
    except Exception as e:
        print(f"无法处理文件 {image_path}: {e}")


def document_metadata_handle(file_path):
    try:
        if file_path.lower().endswith(".pdf"):
            from PyPDF2 import PdfFileReader, PdfFileWriter

            pdf_reader = PdfFileReader(file_path)
            pdf_writer = PdfFileWriter()


            for page_num in range(pdf_reader.getNumPages()):
                page = pdf_reader.getPage(page_num)
                pdf_writer.addPage(page)

            with open(file_path, "wb") as output_pdf:
                pdf_writer.write(output_pdf)


        elif file_path.lower().endswith(".docx"):
            from zipfile import ZipFile

            with ZipFile(file_path, 'r') as docx:

                docx.extractall("temp_docx")
                xml_files = ["temp_docx/docProps/app.xml", "temp_docx/docProps/core.xml"]
                for xml_file in xml_files:
                    if os.path.exists(xml_file):
                        os.remove(xml_file)
                with ZipFile(file_path, 'w') as output_docx:
                    for folder_name, subfolders, filenames in os.walk("temp_docx"):
                        for filename in filenames:
                            output_docx.write(os.path.join(folder_name, filename),
                                              os.path.relpath(os.path.join(folder_name, filename),
                                                             "temp_docx"))

            shutil.rmtree("temp_docx")
    except Exception as e:
        print(f"无法处理文件 {file_path}: {e}")


def process_directory(target_directory):
    for file_path in glob.glob(os.path.join(target_directory, '**', '*'), recursive=True):
        if os.path.isfile(file_path):
            if file_path.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'bmp')):
                print(f"正在处理图片文件: {file_path}")
                picture_exif_data_handle(file_path)

            else:
                print(f"正在处理文件: {file_path}")
                document_metadata_handle(file_path)

if __name__ == "__main__":

    target_directory = r""
    process_directory(target_directory)
