# %%
from PIL import Image
from surya.ocr import run_ocr
from surya.model.detection.model import load_model as load_det_model, load_processor as load_det_processor
from surya.model.recognition.model import load_model as load_rec_model
from surya.model.recognition.processor import load_processor as load_rec_processor


pdf_file = "/home/alex/KED2025/ked2024/materials/data/scanned_pdf_sample/fdp_scan_party_programme_1947.pdf"
from pdf2image import convert_from_path


# convert PDF to images (one image per page)
pages = convert_from_path(pdf_file, fmt="png")


image = pages[0] # Image.open("IMAGE_PATH")

# import requests
# url = "https://fki.tic.heia-fr.ch/static/img/a01-122-02.jpg"
# image = Image.open(requests.get(url, stream=True).raw).convert("RGB")

langs = ["de"] # Replace with your languages - optional but recommended
det_processor, det_model = load_det_processor(), load_det_model()
rec_model, rec_processor = load_rec_model(), load_rec_processor()

predictions = run_ocr([image], [langs], det_model, det_processor, rec_model, rec_processor)

for idx_box in range(len(predictions)):
    print([line.text for line in predictions[idx_box].text_lines])
# %%
