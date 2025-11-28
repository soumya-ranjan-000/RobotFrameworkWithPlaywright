import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np
import pytesseract
from datetime import datetime
import os
import difflib
from pathlib import Path

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def compare_images(baseline_path, current_path,
                   diff_output="diff.png",
                   highlighted_output="highlighted_diff.png",
                   log_file="debug_log.txt",output_dir: str = None):
    
    # Ensure we have an output directory
    if not output_dir:
        output_dir = os.path.join(str(Path(__file__).resolve().parents[1]), 'output')

    os.makedirs(output_dir, exist_ok=True)

    # Load images
    baseline = cv2.imread(baseline_path)
    current = cv2.imread(current_path)

    # Ensure both images have the same dimensions
    if baseline.shape != current.shape:
        print(f"Resizing current image from {current.shape} to {baseline.shape}")
        current = cv2.resize(current, (baseline.shape[1], baseline.shape[0]))

    # Convert to grayscale
    gray_base = cv2.cvtColor(baseline, cv2.COLOR_BGR2GRAY)
    gray_curr = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)

    # --- Step 1: SSIM Comparison ---
    score, diff = ssim(gray_base, gray_curr, full=True)
    print(f"SSIM Score: {score:.4f}")

    # Save raw diff heatmap
    diff = (diff * 255).astype("uint8")
    cv2.imwrite(os.path.join(output_dir, diff_output), diff)

    # Prepare log entries
    log_entries = []
    log_entries.append(f"Timestamp: {datetime.now()}")
    log_entries.append(f"SSIM Score: {score:.4f}")

    # Initialize results dictionary
    results = {
        "timestamp": str(datetime.now()),
        "ssim_score": float(f'{score:.4f}'),
        "diff_image": diff_output,
        "highlighted_image": None,
        "ocr_differences": {"removed": [], "added": []},  # <-- clean diff format
        "ocr_result": None,
        "final_decision": None
    }

    # --- Step 2: Highlight Differences ---
    if score < 1.0:
        print("⚠️ Differences detected. Highlighting regions...")
        log_entries.append("Differences detected. Highlighting regions...")

        # Threshold the diff image to find contours
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw bounding boxes on the current image
        highlighted = current.copy()
        for c in contours:
            if cv2.contourArea(c) > 50:  # ignore tiny noise
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(highlighted, (x, y), (x+w, y+h), (0, 0, 255), 2)

        cv2.imwrite(os.path.join(output_dir, highlighted_output), highlighted)
        log_entries.append(f"Highlighted differences saved to {highlighted_output}")
        results["highlighted_image"] = highlighted_output

        # --- Step 3: OCR Text Extraction ---
        text_base = extract_clean_text(baseline)
        text_curr = extract_clean_text(current)

        # Compute differences using difflib
        diff = difflib.ndiff(text_base, text_curr)
        removed, added = [], []
        for line in diff:
            if line.startswith("- "):
                removed.append(line[2:])
            elif line.startswith("+ "):
                added.append(line[2:])

        results["ocr_differences"]["removed"] = removed
        results["ocr_differences"]["added"] = added

        if removed or added:
            result_msg = f"""❌ OCR: Text difference detected!
After: {removed}
Before: {added}"""
            results["ocr_result"] = False
        else:
            result_msg = "✅ OCR: No text differences detected."
            results["ocr_result"] = True

        print(result_msg)
        log_entries.append(result_msg)

        # Final decision based on SSIM + OCR
        results["final_decision"] = results["ocr_result"]
    else:
        result_msg = "✅ UI looks identical (SSIM=1.0)."
        print(result_msg)
        log_entries.append(result_msg)
        results["final_decision"] = True

    # --- Step 4: Write logs to file (overwrite each run) ---
    with open(os.path.join(output_dir,log_file), "w", encoding="utf-8") as f:
        f.write("=== Debug Run ===\n")
        for entry in log_entries:
            f.write(entry + "\n")
        f.write("\n")

    # Return dictionary for decision-making
    return results

def extract_clean_text(img):
    text = pytesseract.image_to_string(img)
    # Remove unreadable symbols
    import re
    lines = [re.sub(r'[^A-Za-z0-9\s]', '', line).strip()
             for line in text.splitlines() if line.strip()]
    return lines

def find_project_root(start_path=None, markers=None):
    if start_path is None:
        try:
            start_path = os.path.abspath(os.path.dirname(__file__))
        except NameError:
            start_path = os.path.abspath(os.getcwd())
    if markers is None:
        markers = [
            ".git",
            "pyproject.toml",
            "setup.cfg",
            "requirements.txt",
            "Pipfile",
            ".hg",
            ".svn",
        ]
    cur = start_path
    while True:
        for m in markers:
            if os.path.exists(os.path.join(cur, m)):
                return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return start_path
        cur = parent


current_directory = find_project_root()
baseline_image_path = os.path.join(current_directory, "top_categories_expected.png")
current_image_path = os.path.join(current_directory, "top_categories_actual.png")

# Example usage
print(compare_images(baseline_image_path, current_image_path))



