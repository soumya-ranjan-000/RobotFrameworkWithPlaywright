import os
import sys
import cv2
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from skimage.metrics import structural_similarity as ssim_metric
    HAVE_SKIMAGE = True
except Exception:
    HAVE_SKIMAGE = False

@dataclass
class DiffResult:
    changed_percent: float
    regions_count: int
    ssim_score: Optional[float]
    output_paths: dict


def load_image(path: str):
    """Load image with fallbacks. Tries the given path as-is, then looks
    relative to this module's repo root and the current working directory.
    Returns the loaded image (BGR) or raises FileNotFoundError with details.
    """
    tried = []

    # 1) If absolute path or exists as given, try it first
    candidate = Path(path)
    tried.append(str(candidate))
    if candidate.exists():
        img = cv2.imread(str(candidate), cv2.IMREAD_COLOR)
        if img is not None:
            return img

    # 2) Try path relative to this module's repository root (two levels up)
    repo_root = Path(__file__).resolve().parents[1]
    candidate = repo_root / path
    tried.append(str(candidate))
    if candidate.exists():
        img = cv2.imread(str(candidate), cv2.IMREAD_COLOR)
        if img is not None:
            return img

    # 3) Try path relative to current working directory
    candidate = Path(os.getcwd()) / path
    tried.append(str(candidate))
    if candidate.exists():
        img = cv2.imread(str(candidate), cv2.IMREAD_COLOR)
        if img is not None:
            return img

    # 4) Try resolving via sys.path entries (helpful if running from tests folder)
    for p in sys.path:
        candidate = Path(p) / path
        tried.append(str(candidate))
        if candidate.exists():
            img = cv2.imread(str(candidate), cv2.IMREAD_COLOR)
            if img is not None:
                return img

    # As a last attempt, try cv2.imread on the original string (useful if path contains special prefixes)
    tried.append(f"cv2.imread('{path}')")
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is not None:
        return img

    # Nothing worked — report the locations we tried to help debugging
    tried_unique = []
    for t in tried:
        if t not in tried_unique:
            tried_unique.append(t)

    tried_text = "\n".join(f" - {t}" for t in tried_unique)
    raise FileNotFoundError(
        f"Image not found or could not be opened: {path}\nTried the following locations:\n{tried_text}\nCurrent working dir: {os.getcwd()}"
    )


def ensure_same_size(imgA, imgB):
    """Resize imgB to match imgA's dimensions if they differ."""
    if imgA.shape[:2] != imgB.shape[:2]:
        imgB = cv2.resize(imgB, (imgA.shape[1], imgA.shape[0]), interpolation=cv2.INTER_AREA)
    return imgB


def align_images(imgA, imgB, max_features = 5000, good_match_ratio=0.75):
    """Align imgB to imgA using ORB feature matching and homography.
    Always returns a tuple (aligned_image, homography_ok: bool).
    """
    grayA = cv2.cvtColor(imgA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imgB, cv2.COLOR_BGR2GRAY)

    orb = cv2.ORB_create(nfeatures = max_features)
    kpA, desA = orb.detectAndCompute(grayA, None)
    kpB, desB = orb.detectAndCompute(grayB, None)

    if desA is None or desB is None or len(kpA) < 10 or len(kpB) < 10:
        return ensure_same_size(imgA, imgB), False

    # ORB produces binary descriptors; use Hamming distance
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    try:
        knn_matches = matcher.knnMatch(desA, desB, 2)
    except Exception:
        return ensure_same_size(imgA, imgB), False

    good = []
    for m_n in knn_matches:
        if len(m_n) < 2:
            continue
        m, n = m_n[0], m_n[1]
        if m.distance < good_match_ratio * n.distance:
            good.append(m)

    if len(good) < 10:
        return ensure_same_size(imgA, imgB), False

    src_pts = np.float32([kpA[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kpB[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    if H is None:
        return ensure_same_size(imgA, imgB), False

    alignedB = cv2.warpPerspective(imgB, H, (imgA.shape[1], imgA.shape[0]), flags=cv2.INTER_LINEAR)
    return alignedB, True


def compute_absdiff_mask(grayA, grayB):
    blurA = cv2.GaussianBlur(grayA, (5, 5), 0)
    blurB = cv2.GaussianBlur(grayB, (5, 5), 0)

    diff = cv2.absdiff(blurA, blurB)
    _,thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    clean = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    clean = cv2.dilate(clean, kernel, iterations=1)
    return diff, clean

def compute_ssim_mask(grayA, grayB):
    if not HAVE_SKIMAGE:
        raise RuntimeError("SSIM method selected but is not installed.")
    score, diff = ssim_metric(grayA, grayB, full=True)
    diff_inv = (1.0-diff)
    diff_uint8 = np.uint8(np.clip(diff_inv*255, 0, 255))

    _,thresh = cv2.threshold(diff_uint8, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    clean = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    clean = cv2.dilate(clean, kernel, iterations=1)
    return score, diff_uint8, clean


def overlay_mask(image, mask, color=(0, 0, 255), alpha=0.4):
    overlay = image.copy()
    color_layer = np.zeros_like(image)
    color_layer[mask==255] = color
    cv2.addWeighted(color_layer, alpha, overlay, 1 - alpha, 0, overlay)
    return overlay


def draw_bboxes(image, mask, min_area=500, color=(0, 255, 0), thickness=2  ):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxed = image.copy()
    regions = 0
    for c in contours:
        if cv2.contourArea(c) < min_area:
            continue
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(boxed, (x, y), (x + w, y + h), color, thickness)
        regions += 1
    
    return boxed, regions


def apply_heatmap(diff_unit8, base_image, alpha=0.5):
    heatmap = cv2.applyColorMap(diff_unit8, cv2.COLORMAP_JET)
    heatmap_overlay = cv2.addWeighted(heatmap, alpha, base_image,1-alpha,0)
    return heatmap_overlay


def save_image(path: str, image):
    ok = cv2.imwrite(path, image)
    if not ok:
        raise IOError(f"Failed to save image to: {path}")
    

def compare_images(pathA: str, pathB: str, output_dir: str = None, method: str = 'absdiff', align: bool = True, min_area = 100) -> DiffResult:
    # Ensure we have an output directory
    if not output_dir:
        output_dir = os.path.join(str(Path(__file__).resolve().parents[1]), 'output')

    os.makedirs(output_dir, exist_ok=True)
    imgA = load_image(pathA)
    imgB = load_image(pathB)

    if align:
        alignedB, homography_ok = align_images(imgA, imgB)
        alignment_status = "homography" if homography_ok else "resize"
    else:
        alignedB = ensure_same_size(imgA, imgB)
        alignment_status = "disabled"
    
    # keep filename consistent with paths below
    save_image(os.path.join(output_dir, 'aligned_B.png'), alignedB)

    grayA = cv2.cvtColor(imgA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(alignedB, cv2.COLOR_BGR2GRAY)

    ssim_score = None
    if method.lower() == 'ssim':
        ssim_score, diff_uint8, mask = compute_ssim_mask(grayA, grayB)
        ssim_score = float(ssim_score)
    else:
        diff_uint8, mask = compute_absdiff_mask(grayA, grayB)

    changed_pixels = int(np.count_nonzero(mask))
    total_pixels = mask.size
    changed_percent = (changed_pixels / total_pixels) * 100.0

    overlay = overlay_mask(imgA, mask, color=(0, 0, 255), alpha=0.4)
    bboxes, regions = draw_bboxes(overlay, mask, min_area=min_area, color=(0, 255, 0), thickness=2)
    heatmap = apply_heatmap(diff_uint8, imgA, alpha=0.6)

    paths = {
        "alignedB": os.path.join(output_dir, 'aligned_B.png'),
        "diff_mask": os.path.join(output_dir, 'diff_mask.png'),
        "overlay": os.path.join(output_dir, 'overlay.png'),
        "bboxes": os.path.join(output_dir, 'bboxes.png'),
        "heatmap": os.path.join(output_dir, 'heatmap.png'),
        "report": os.path.join(output_dir, 'report.txt'),
    }

    save_image(paths["diff_mask"], mask)
    save_image(paths["overlay"], overlay)
    save_image(paths["bboxes"], bboxes)
    save_image(paths["heatmap"], heatmap)

    with open(paths["report"], 'w', encoding="utf-8") as f:
        f.write("Image Comparison Report\n")
        f.write("=======================\n\n")
        f.write(f"Image A: {pathA}\n")
        f.write(f"Image B: {pathB}\n")
        f.write(f"Alignment method: {alignment_status}\n")
        f.write(f"Comparison method: {method}\n")
        f.write(f"Changed pixels: {changed_pixels} / {total_pixels} ({changed_percent:.4f}%)\n")
        f.write(f"Regions detected: {regions}\n")
        if ssim_score is not None:
            f.write(f"SSIM score: {ssim_score:.4f} (1.0 = identical)\n")

    return DiffResult(
        changed_percent=changed_percent,
        regions_count=regions,
        ssim_score=ssim_score,
        output_paths=paths
    )
