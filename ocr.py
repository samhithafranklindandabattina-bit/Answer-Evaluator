from pdf2image import convert_from_bytes
import requests
import os
import tempfile
import streamlit as st

# ✅ Use correct and consistent poppler path
POPPLER_PATH = r"C:\poppler-25.12.0\Library\bin"


def convert_pdf(pdf_bytes):
    images = convert_from_bytes(
        pdf_bytes,
        dpi=300,
        poppler_path=POPPLER_PATH
    )
    return images


def pdf_to_text_with_ocr(pdf_path, api_key, output_folder="output", dpi=200, delete_after_use=False):
    os.makedirs(output_folder, exist_ok=True)

    # ✅ Read file as bytes (fix)
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    images = convert_from_bytes(
        pdf_bytes,
        dpi=dpi,
        poppler_path=POPPLER_PATH
    )

    extracted_text = ""
    image_paths = []

    for i, img in enumerate(images):
        image_path = os.path.join(output_folder, f"page_{i+1}.jpg")
        img.save(image_path, "JPEG", quality=95)
        image_paths.append(image_path)

        file_size = os.path.getsize(image_path)
        if file_size > 1024 * 1024:
            print(f"Image too large: {image_path}")
            return ""

        with open(image_path, 'rb') as image_file:
            response = requests.post(
                "https://api.ocr.space/parse/image",
                files={"image": image_file},
                data={"apikey": api_key, "OCREngine": 2, "isTable": True},
            )

        result = response.json()

        if "ParsedResults" in result:
            extracted_text += result["ParsedResults"][0]["ParsedText"] + "\n"
        else:
            extracted_text += f"\n[OCR failed page {i+1}]\n"

    if delete_after_use:
        for img_path in image_paths:
            os.remove(img_path)

    return extracted_text


def pdf_obj_to_text_with_ocr(pdf_file, api_key, dpi=100, delete_after_use=False):
    # ✅ CRITICAL FIX — reset pointer
    pdf_file.seek(0)

    pdf_bytes = pdf_file.read()

    images = convert_from_bytes(
        pdf_bytes,
        dpi=dpi,
        poppler_path=POPPLER_PATH
    )

    extracted_text = ""
    temp_files = []

    for i, img in enumerate(images):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_image:
            img.save(temp_image.name, "JPEG", quality=95)
            temp_files.append(temp_image.name)

        with open(temp_image.name, 'rb') as image_file:
            try:
                response = requests.post(
                    "https://api.ocr.space/parse/image",
                    files={"image": image_file},
                    data={"apikey": api_key, "OCREngine": 2, "isTable": True},
                )
                response.raise_for_status()
                result = response.json()

                if "ParsedResults" in result and result["ParsedResults"]:
                    extracted_text += result["ParsedResults"][0]["ParsedText"] + "\n"
                else:
                    extracted_text += f"\n[OCR failed page {i+1}]\n"

            except requests.exceptions.RequestException as e:
                st.write(f"OCR API failed page {i+1}: {str(e)}")
                extracted_text += f"\n[OCR API error page {i+1}]\n"

    if delete_after_use:
        for temp_file in temp_files:
            os.remove(temp_file)

    return extracted_text