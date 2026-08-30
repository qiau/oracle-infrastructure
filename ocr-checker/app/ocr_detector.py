import cv2
import numpy as np
import pytesseract


# ============================================================
# KONFIGURASI
# ============================================================

TARGET_TEXT = "raffz"

# Crop:
# 7% bagian bawah gambar
CROP_HEIGHT_RATIO = 0.07

# 20% bagian tengah gambar
CROP_WIDTH_RATIO = 0.20

# Upscale untuk membantu membaca teks kecil
UPSCALE = 5


# ============================================================
# CROP
# ============================================================

def crop_target_area(img):
    """
    Mengambil area kecil berbentuk persegi/persegi panjang
    di tengah-bawah gambar.

    Vertikal:
        7% bagian paling bawah

    Horizontal:
        20% bagian tengah
    """

    height, width = img.shape[:2]

    # --------------------------------------------------------
    # Tinggi: 7% paling bawah
    # --------------------------------------------------------

    crop_height = int(
        height * CROP_HEIGHT_RATIO
    )

    y_start = height - crop_height

    # --------------------------------------------------------
    # Lebar: 20% bagian tengah
    # --------------------------------------------------------

    crop_width = int(
        width * CROP_WIDTH_RATIO
    )

    x_start = (width - crop_width) // 2
    x_end = x_start + crop_width

    return img[
        y_start:height,
        x_start:x_end
    ]


# ============================================================
# OCR
# ============================================================

def detect_raffz(image_bytes):
    """
    Mendeteksi teks 'Raffz' pada area tengah-bawah gambar.

    Image tidak disimpan ke disk.
    Semua proses dilakukan langsung dari memory.

    Return:
        True  -> Raffz ditemukan
        False -> Raffz tidak ditemukan
    """

    # --------------------------------------------------------
    # Decode image dari bytes
    # --------------------------------------------------------

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    img = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if img is None:
        return False

    # --------------------------------------------------------
    # Crop area target
    # --------------------------------------------------------

    crop = crop_target_area(img)

    # --------------------------------------------------------
    # Grayscale
    # --------------------------------------------------------

    gray = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2GRAY
    )

    # --------------------------------------------------------
    # Upscale
    # --------------------------------------------------------

    gray = cv2.resize(
        gray,
        None,
        fx=UPSCALE,
        fy=UPSCALE,
        interpolation=cv2.INTER_CUBIC
    )

    # --------------------------------------------------------
    # OCR
    #
    # PSM 7 = satu baris teks
    # eng    = karakter Latin/Inggris
    # --------------------------------------------------------

    text = pytesseract.image_to_string(
        gray,
        config="--psm 7 -l eng"
    )

    text = text.lower().strip()

    print(
        f"    OCR: {text!r}"
    )

    # --------------------------------------------------------
    # Deteksi
    # --------------------------------------------------------

    return TARGET_TEXT in text