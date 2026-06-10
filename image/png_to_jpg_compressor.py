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
    target_width: int = 1960,
    target_height: int = 1507,
    save_quality: int = 100,
    target_dirpath: str = "result",
) -> None:

    if (
        not isinstance(dirpath, str)
        or not os.path.isdir(dirpath)
        or not isinstance(target_height, int)
        or not isinstance(target_width, int)
    ):
        raise ValueError("\033[31mParameters are invalid\033[0m")

    result_path: str = os.path.join(dirpath, target_dirpath)

    if not os.path.exists(result_path):
        os.mkdir(result_path)

    for fname in os.listdir(dirpath):
        lower_fname = fname.lower()
        if lower_fname.endswith(".png") or lower_fname.endswith(".jpg"):
            fpath = os.path.join(dirpath, fname)
            img = Image.open(fpath)

            img_resized = img_scale_down_same_proportion(
                img, target_width, target_height
            )

            new_fname = os.path.splitext(fname)[0] + ".jpg"
            new_fpath = os.path.join(result_path, new_fname)

            img_resized.convert("RGB").save(new_fpath, "JPEG", quality=save_quality)

            img.close()
            img_resized.close()
            print(f"Converted and resized {fname} to {new_fname}")


if __name__ == "__main__":
    mode = sys.argv[1]
    dirpath = sys.argv[2]

    if (mode == "cover"):
        convert_and_resize_images(dirpath, 1280, 960)
    elif (mode == "show"):
        convert_and_resize_images(dirpath)
    else:
        print("No valid option was specified")
        exit(1)
    print("Complete!")
        
