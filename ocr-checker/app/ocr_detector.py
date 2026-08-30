import cv2
import pytesseract


TARGET_TEXT = "raffz"


def detect_raffz(image_bytes):
    """
    Mendeteksi 'Raffz' pada bagian bawah-tengah gambar.

    image_bytes:
        bytes gambar yang ada di memory.

    return:
        True / False
    """

    # Decode image langsung dari memory
    image_array = bytearray(image_bytes)

    img = cv2.imdecode(
        __import__("numpy").frombuffer(
            image_array,
            dtype=__import__("numpy").uint8
        ),
        cv2.IMREAD_COLOR
    )

    if img is None:
        return False

    height, width = img.shape[:2]

    # --------------------------------------------------------
    # Crop:
    # 25% bagian bawah
    # 30% bagian tengah
    # --------------------------------------------------------

    y_start = int(height * 0.75)
    x_start = int(width * 0.35)
    x_end = int(width * 0.65)

    crop = img[
        y_start:height,
        x_start:x_end
    ]

    # Grayscale
    gray = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2GRAY
    )

    # Upscale
    gray = cv2.resize(
        gray,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )

    # OCR satu kali
    text = pytesseract.image_to_string(
        gray,
        config="--psm 7 -l eng"
    )

    text = text.lower()

    print(f"    OCR: {text.strip()!r}")

    return TARGET_TEXT in text