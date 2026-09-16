"""Report the non-white content bounding box of a PDF page.

Used to check whether an exported figure wastes page area on empty margin,
which would shrink the figure when it is included at \\columnwidth.
"""
import subprocess
import sys
import tempfile
import os

try:
    from PIL import Image
    import numpy as np
except ImportError:
    sys.exit("needs pillow and numpy")


def bbox(pdf, dpi=60):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            ["pdftoppm", "-png", "-r", str(dpi), "-f", "1", "-l", "1", pdf, os.path.join(tmp, "p")],
            check=True,
        )
        page = [f for f in os.listdir(tmp) if f.endswith(".png")][0]
        img = Image.open(os.path.join(tmp, page)).convert("L")
    a = np.asarray(img)
    mask = a < 245                      # anything that is not near-white
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    if not rows.any():
        return None
    top, bottom = np.where(rows)[0][[0, -1]]
    left, right = np.where(cols)[0][[0, -1]]
    h, w = a.shape
    return {
        "page_px": (w, h),
        "content_px": (int(right - left + 1), int(bottom - top + 1)),
        "margins_pct": {
            "left": round(100 * left / w, 1),
            "right": round(100 * (w - 1 - right) / w, 1),
            "top": round(100 * top / h, 1),
            "bottom": round(100 * (h - 1 - bottom) / h, 1),
        },
        "content_area_pct": round(
            100 * (right - left + 1) * (bottom - top + 1) / (w * h), 1
        ),
    }


if __name__ == "__main__":
    for path in sys.argv[1:]:
        r = bbox(path)
        print(f"{path}")
        if r is None:
            print("   (blank page)")
            continue
        print(f"   page {r['page_px'][0]}x{r['page_px'][1]}  "
              f"content {r['content_px'][0]}x{r['content_px'][1]}")
        print(f"   margins  {r['margins_pct']}")
        print(f"   content fills {r['content_area_pct']}% of the page area")
