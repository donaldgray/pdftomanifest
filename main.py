import sys
from pathlib import Path

import fitz
from iiif import IIIFStatic
from iiif_prezi.factory import ManifestFactory

extract_path = Path("./output/images")
image_path = Path("./output/iiif/images")
manifest_path = Path("./output/iiif")


def ensure_dirs():
    """Construct output dirs"""
    extract_path.mkdir(parents=True, exist_ok=True)
    image_path.mkdir(parents=True, exist_ok=True)
    manifest_path.mkdir(parents=True, exist_ok=True)


def extract_images_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    image_count = 0

    images = []
    for i in range(len(doc)):
        page = i + 1
        print(f"extracting images from page {page}..")

        count_per_page = 1
        for img in doc.getPageImageList(i):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            target_out = Path(extract_path, f"{image_count:02}.png")

            if pix.n - pix.alpha < 4:  # this is GRAY or RGB
                pix.writePNG(target_out)
            else:  # CMYK: convert to RGB first
                pix = fitz.Pixmap(fitz.csRGB, pix)
                pix.writePNG(target_out)
            pix = None

            images.append(target_out)

            count_per_page = count_per_page + 1
            image_count = image_count + 1

    print(f"finished extracting {image_count} images")
    return images


def generate_iiif(images, pdf):
    """Generate IIIF 2.0 static image-service and manifest"""

    # configure manifest factory
    manifest_factory = ManifestFactory()
    manifest_factory.set_base_prezi_dir(str(manifest_path))
    manifest_factory.set_base_prezi_uri("http://localhost:8000")
    manifest_factory.set_base_image_uri("http://localhost:8000/images")
    manifest_factory.set_iiif_image_info(2.0, 1)

    manifest = manifest_factory.manifest(label="Example Manifest from PDF")
    manifest.description = "Sample P2 manifest with images from PDF"
    manifest.set_metadata({"Generated from": pdf})

    # configure tile generator for static assets
    tile_generator = IIIFStatic(dst=str(image_path),
                                prefix="http://localhost:8000/images",
                                tilesize=512,
                                api_version="2.1",
                                extras=['/full/90,/0/default.jpg',
                                        '/full/200,/0/default.jpg'])  # thumbnail for UV

    seq = manifest.sequence()
    idx = 0
    for i in images:
        print(f"processing image {idx}")
        image_id = i.stem

        # create a canvas with an annotation
        canvas = seq.canvas(ident=image_id, label=f"Canvas {idx}")

        # create an annotation on the Canvas
        annotation = canvas.annotation(ident=f"page-{idx}")

        # add an image to the anno
        img = annotation.image(image_id, iiif=True)
        img.service.profile = 'http://iiif.io/api/image/2/level0.json'

        # set image + canvas hw
        img.set_hw_from_file(str(i))
        canvas.height = img.height
        canvas.width = img.width

        # generate image-pyramid
        tile_generator.generate(src=i, identifier=image_id)

        idx = idx + 1

    manifest.toFile(compact=False)


if __name__ == '__main__':
    if pdf := sys.argv[-1]:
        ensure_dirs()
        images = extract_images_from_pdf(pdf)
        generate_iiif(images, pdf)
        print("finished")
    else:
        print("no arg supplied")
