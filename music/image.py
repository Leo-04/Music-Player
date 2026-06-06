# https://github.com/beetbox/mediafile/blob/master/mediafile.py#L355
import struct
from mutagen import File
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from PIL import ImageTk


def load(filename: str) -> Image.Image | None:
    """
    Loads common image data from a music file

    Tries to open a music file and find an image, extracting it to a PIL Image.
    If the image cannot be opened, or if there is no image tag, None is returned

    Args:
        filename: str | PathLike
            A string or path like object to the file

    Returns:
        The image data loaded from tags or None
    """

    filename = str(filename)

    # Try to open the file
    try:
        file = File(filename)
    except Exception as err:
        print("Error loading file:", filename, err)
        return None

    # If there are tags
    if not file.tags:
        print("NO TAGS", filename)
        return

    bytesio = None

    # Try to find image tag
    key: str = ""
    for key in file.tags.keys():
        if "APIC" in key.upper():
            bytesio = BytesIO(file.tags.get(key).data)
            break
        elif "cov" in key.lower():
            bytesio = BytesIO(bytes(file.tags[key][0]))
            break
        elif key.lower() == "wm/picture":
            data = bytes(file.tags[key][0])
            _, length = struct.unpack_from('<bi', data)
            pos = 5
            while data[pos:pos + 2] != b"\x00\x00":
                pos += 2
            pos += 2
            while data[pos:pos + 2] != b"\x00\x00":
                pos += 2
            pos += 2
            bytesio = BytesIO(data[pos: pos + length])
            break

    if bytesio is None:
        print("NO IMAGE IN TAGS", filename, file.tags.keys(), type(file))
        return

    # If we have got the image bytes, try to load image
    try:
        return Image.open(bytesio)
    except UnidentifiedImageError:
        print("Cant open tag:", filename, file.tags[key])


def thumbnail(filename: str, size: tuple[int, int] | list[int]) -> Image.Image | None:
    """
    Loads an image from a music file and resizes it

    Tries to open a music file and find an image extracting it to a PIL Image and resizing it.
    If the image cannot be opened, or if there is no image tag, None is returned

    Args:
        filename: str | PathLike
            A string or path like object to the file

        size: tuple[int, int]
            A 2 tuple int that contains the width and height of the image

    Returns:
        The image data loaded from tags or None
    """

    img = load(filename)

    if img is None:
        return


    image = Image.new('RGBA', size, (0, 0, 0, 0))
    img = img.copy()
    img.thumbnail(size, Image.Resampling.LANCZOS)

    img_w, img_h = img.size
    w, h = image.size
    center = ((w - img_w) // 2, (h - img_h) // 2)
    image.paste(img, center)

    return image


def get(filename: str, size: tuple[int, int] | list[int]) -> ImageTk.PhotoImage | None:
    """
    Loads a PhotoImage from a music file and resizes it

    Tries to open a music file and find an image extracting it to a PIL Image and resizing it, then convert it to a PhotoImage.
    If the image cannot be opened, or if there is no image tag, None is returned

    Args:
        filename: str | PathLike
            A string or path like object to the file

        size: tuple[int, int]
            A 2 tuple int that contains the width and height of the image

    Returns:
        The loaded image or None
    """

    img = thumbnail(filename, size)
    if img is not None:
        return ImageTk.PhotoImage(img)
