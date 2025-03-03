import os
import glob
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from pathlib import Path
import shutil

# 删除文件的EXIF数据（图片格式为JPEG、PNG、GIF等）
def remove_exif(image_path):
    try:
        # 打开图片
        image = Image.open(image_path)
        # 如果图片格式是JPEG，删除EXIF数据
        if image.format == "JPEG":
            image_data = image.getdata()
            clean_image = Image.new(image.mode, image.size)
            clean_image.putdata(image_data)
            clean_image.save(image_path, "JPEG")
        elif image.format == "PNG":
            # PNG文件不包含EXIF数据，但可能有其他元数据
            if isinstance(image, PngImageFile):
                image.save(image_path, "PNG")
    except Exception as e:
        print(f"无法处理文件 {image_path}: {e}")

# 删除Word、PDF等文件的作者、创建日期等元数据
def remove_file_metadata(file_path):
    try:
        # 对于PDF文件
        if file_path.lower().endswith(".pdf"):
            from PyPDF2 import PdfFileReader, PdfFileWriter

            pdf_reader = PdfFileReader(file_path)
            pdf_writer = PdfFileWriter()

            # 将所有页面复制到新的PDF中（不包括元数据）
            for page_num in range(pdf_reader.getNumPages()):
                page = pdf_reader.getPage(page_num)
                pdf_writer.addPage(page)

            # 保存没有元数据的新PDF
            with open(file_path, "wb") as output_pdf:
                pdf_writer.write(output_pdf)

        # 对于Word文件（docx）
        elif file_path.lower().endswith(".docx"):
            from zipfile import ZipFile

            with ZipFile(file_path, 'r') as docx:
                # 临时解压docx文件
                docx.extractall("temp_docx")
                # 删除包含元数据的XML文件
                xml_files = ["temp_docx/docProps/app.xml", "temp_docx/docProps/core.xml"]
                for xml_file in xml_files:
                    if os.path.exists(xml_file):
                        os.remove(xml_file)
                # 压缩回去生成无元数据的docx
                with ZipFile(file_path, 'w') as output_docx:
                    for folder_name, subfolders, filenames in os.walk("temp_docx"):
                        for filename in filenames:
                            output_docx.write(os.path.join(folder_name, filename),
                                              os.path.relpath(os.path.join(folder_name, filename),
                                                             "temp_docx"))

            # 删除临时目录
            shutil.rmtree("temp_docx")
    except Exception as e:
        print(f"无法处理文件 {file_path}: {e}")

# 递归处理目录中的所有文件
def process_directory(target_directory):
    for file_path in glob.glob(os.path.join(target_directory, '**', '*'), recursive=True):
        if os.path.isfile(file_path):
            # 如果是图片文件，移除EXIF数据
            if file_path.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'bmp')):
                print(f"正在处理图片文件: {file_path}")
                remove_exif(file_path)
            # 对其他文件格式处理元数据
            else:
                print(f"正在处理文件: {file_path}")
                remove_file_metadata(file_path)

if __name__ == "__main__":
    # 设置目标目录
    target_directory = r""
    process_directory(target_directory)
