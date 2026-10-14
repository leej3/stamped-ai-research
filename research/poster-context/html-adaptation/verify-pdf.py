# SPDX-FileCopyrightText: 2026 Center for Open Neuroscience
# SPDX-License-Identifier: Apache-2.0
# /// script
# requires-python = ">=3.11"
# dependencies = ["pypdf==6.0.0", "Pillow==11.3.0", "zxing-cpp==2.3.0"]
# ///
"""Verify the exported page, PDF links, and every QR from the actual PDF raster.

uv run verify-pdf.py --review-dir /absolute/review-directory
Requires pdftoppm. The report does not replace human visual review.
"""
import argparse
import hashlib
import json
from math import hypot
from pathlib import Path
import subprocess

from PIL import Image
from pypdf import PdfReader
import zxingcpp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-dir", required=True, type=Path)
    args = parser.parse_args()
    root = args.review_dir.resolve()
    pdf = root / "stamped-ai-poster.pdf"
    audit = json.loads((root / "html-audit.json").read_text())
    reader = PdfReader(pdf)
    assert len(reader.pages) == 1, f"Expected one page, got {len(reader.pages)}"
    page = reader.pages[0]
    width, height = float(page.mediabox.width), float(page.mediabox.height)
    assert abs(width - 3168) < 0.1 and abs(height - 3168) < 0.1, (width, height)
    uris = []
    for ref in page.get("/Annots", []):
        ann = ref.get_object()
        action = ann.get("/A", {})
        if action.get("/S") == "/URI":
            uris.append(str(action.get("/URI")))
    missing = sorted(set(audit["links"]) - set(uris))
    assert not missing, f"Missing clickable PDF links: {missing}"
    assert audit["minimum_text_px"] >= 32
    font_sizes = []

    def inspect_text(text, current_matrix, text_matrix, font, font_size):
        if not text.strip():
            return
        # Transform the text-space vertical unit vector into page points.
        # Chromium records CSS font sizes with a 0.75 page scale. Include both
        # matrices so a transformed text node cannot evade the 24-point floor.
        cm, tm = current_matrix, text_matrix
        scale = hypot(tm[2] * cm[0] + tm[3] * cm[2],
                      tm[2] * cm[1] + tm[3] * cm[3])
        font_sizes.append({"text": text.strip()[:100], "points": font_size * scale})

    page.extract_text(visitor_text=inspect_text)
    assert font_sizes, "No inspectable PDF text; cannot establish font sizes"
    small_pdf_text = [row for row in font_sizes if row["points"] < 24 - 0.001]
    assert not small_pdf_text, f"PDF text smaller than 24 pt: {small_pdf_text}"
    # The full page is also the visual-review image. Actual PDF pixels are the
    # source for QR checks, not the original SVG or a browser screenshot.
    dpi = 150
    subprocess.run(["pdftoppm", "-f", "1", "-singlefile", "-r", str(dpi),
                    "-png", str(pdf), str(root / "pdf-fullsize")], check=True)
    Image.MAX_IMAGE_PIXELS = 100_000_000
    raster = Image.open(root / "pdf-fullsize.png").convert("RGB")
    sx, sy = raster.width / 4224, raster.height / 4224
    qrs = []
    for qr in audit["qrs"]:
        r = qr["rect"]
        # White quiet zone is already in the SVG; add only a two-pixel margin.
        crop = raster.crop((int(r["x"] * sx) - 2, int(r["y"] * sy) - 2,
                            round((r["x"] + r["width"]) * sx) + 2,
                            round((r["y"] + r["height"]) * sy) + 2))
        crop.save(root / f"pdf-qr-{qr['name']}.png")
        decoded = [b.text for b in zxingcpp.read_barcodes(crop)]
        rotated = [b.text for b in zxingcpp.read_barcodes(crop.transpose(Image.Transpose.ROTATE_90))]
        qrs.append({"name": qr["name"], "expected": qr["url"], "decoded": decoded,
                    "decoded_rotated": rotated, "passed": decoded == [qr["url"]] and rotated == [qr["url"]]})
    preview = raster.copy()
    preview.thumbnail((1600, 1600))
    preview.save(root / "pdf-preview.png")
    report = {"pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
              "page_count": len(reader.pages), "page_points": [width, height],
              "minimum_html_text_px": audit["minimum_text_px"], "minimum_html_text_pt": audit["minimum_text_px"] * 72 / 96,
              "minimum_pdf_text_pt": round(min(row["points"] for row in font_sizes), 4),
              "inspected_pdf_text_runs": len(font_sizes),
              "link_annotation_count": len(uris), "unique_expected_links": len(audit["links"]),
              "missing_links": missing, "raster_dpi": dpi, "qr_results": qrs,
              "visual_review": "Required separately; not established by this script."}
    (root / "pdf-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    assert qrs and all(q["passed"] for q in qrs), "A PDF QR failed; inspect pdf-audit.json"
    print(json.dumps({"page_inches": [width / 72, height / 72], "qrs_passed": len(qrs), "links_present": len(set(uris)), "report": str(root / "pdf-audit.json")}))


if __name__ == "__main__":
    main()
