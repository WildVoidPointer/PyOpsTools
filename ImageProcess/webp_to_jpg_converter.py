from PIL import Image
import os

def convert_webp_to_jpg(input_folder, output_folder):
    """
    Convert all WebP images in the input folder to JPG and save them in the output folder.

    :param input_folder: Path to the folder containing WebP images.
    :param output_folder: Path to the folder where converted JPG images will be saved.
    """
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.webp'):
            webp_path = os.path.join(input_folder, filename)
            jpg_path = os.path.join(output_folder, os.path.splitext(filename)[0] + '.jpg')
            
            try:
                with Image.open(webp_path) as img:
                    rgb_img = img.convert('RGB')  # Convert image to RGB format
                    rgb_img.save(jpg_path, 'JPEG')  # Save as JPG
                    print(f"Converted: {webp_path} -> {jpg_path}")
            except Exception as e:
                print(f"Failed to convert {webp_path}: {e}")

if __name__ == "__main__":
    input_folder = r"D:\Downloads\Emojs"
    output_folder = "./output_jpg"  # Replace with your output folder path

    convert_webp_to_jpg(input_folder, output_folder)
