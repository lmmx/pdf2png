from pathlib import Path
from tqdm import tqdm
from sys import stderr
from argparse import ArgumentParser
from subprocess import call
from pdf2image import convert_from_path
from more_itertools import ichunked
from PIL import Image

parser = ArgumentParser()
parser.add_argument("input")

pdf_crop_margins = "pdf-crop-margins"

arg_l = parser.parse_args()

input_pdf = Path(arg_l.input).absolute()
if not input_pdf.suffix == ".pdf":
    raise ValueError(f"'{input_pdf}' does not have a PDF suffix")
crop_suffix = "_cropped"
crop_pdf_dest = input_pdf.parent / f"{input_pdf.stem}{crop_suffix}.pdf"

call([
    pdf_crop_margins,
    "-s",
    "-u",
    str(input_pdf),
    "-o",
    str(crop_pdf_dest)
    ]
)

page_limit = 8
pdf_pages = convert_from_path(crop_pdf_dest)
i = 0
pdf_pages_lim = pdf_pages[:page_limit]
for page_pair in tqdm(ichunked(pdf_pages_lim, 2), total=len(pdf_pages_lim) // 2):
    iter_size = len(pdf_pages_lim[(i * 2) : (i + 1) * 2])
    if iter_size == 1:
        print(f"Stopped ahead of iteration {i+1} to avoid unpaired page", file=stderr)
        continue
    p1, p2 = page_pair
    if not p1.height == p2.height:
        raise NotImplementedError("Images aren't same size, can't stack 2-up")
    combined_shape = (p1.width + p2.width, p1.height)
    two_up = Image.new('RGB', combined_shape)
    two_up.paste(p1, (0,0))
    two_up.paste(p2, (p1.width, 0))
    out_png = input_pdf.parent / f"{input_pdf.stem}_{i}.png"
    two_up.save(out_png)
    i += 1
