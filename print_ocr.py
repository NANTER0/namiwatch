from PIL import Image
import pytesseract


def extract_text(image_file):
    try:
        image = Image.open(image_file)

        text = pytesseract.image_to_string(
            image
        )

        return text.strip()

    except Exception as error:
        return "OCR_ERROR: " + str(error)
