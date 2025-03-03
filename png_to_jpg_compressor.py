from PIL import Image
import sys
import os


def img_scale_down_same_proportion(
    image: Image.Image, target_width: int, target_height: int
) -> Image.Image:

    if (
        not isinstance(image, Image.Image)
        or not isinstance(target_height, int)
        or not isinstance(target_height, int)
    ):
        raise ValueError("\033[31mParameters are invalid\033[0m")

    width, height = image.size

    aspect_ratio = width / height
    if width > height:
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    else:
        new_height = target_height
        new_width = int(target_height * aspect_ratio)

    new_width = min(new_width, target_width)
    new_height = min(new_height, target_height)
    return image.resize((new_width, new_height), Image.LANCZOS)


def convert_and_resize_images(
    dirpath: str,
    target_dirpath: str = "result",
    target_width: int = 1280,
    target_height: int = 960,
) -> None:

    if (
        not isinstance(dirpath, str)
        or not os.path.isdir(dirpath)
        or not isinstance(target_height, int)
        or not isinstance(target_width, int)
    ):
        raise ValueError("\033[31mParameters are invalid\033[0m")

    _result_path: str = os.path.join(dirpath, target_dirpath)

    if not os.path.exists(_result_path):
        os.mkdir(_result_path)

    for fname in os.listdir(dirpath):
        lower_fname = fname.lower()
        if lower_fname.endswith(".png") or lower_fname.endswith(".jpg"):
            fpath = os.path.join(dirpath, fname)
            img = Image.open(fpath)

            img_resized = img_scale_down_same_proportion(
                img, target_width, target_height
            )

            new_fname = os.path.splitext(fname)[0] + ".jpg"
            new_fpath = os.path.join(_result_path, new_fname)

            img_resized.convert("RGB").save(new_fpath, "JPEG", quality=85)

            img.close()
            img_resized.close()
            print(f"Converted and resized {fname} to {new_fname}")


if __name__ == "__main__":
    dirpath = sys.argv[1]
    convert_and_resize_images(dirpath)
