import cv2
import numpy as np
from PIL import Image
import io

def check_image_quality(image_bytes: bytes) -> dict:
    """
    Performs empirical CV quality checks on uploaded crop image.
    Checks:
    1. Valid format & decodability
    2. Minimum resolution (200x200)
    3. Blur detection via Laplacian variance
    4. Darkness detection via mean grayscale intensity
    5. Overexposure / Brightness detection
    """
    issues = []
    metrics = {}

    try:
        # Decode image using PIL
        pil_img = Image.open(io.BytesIO(image_bytes))
        pil_img.verify()
        
        # Re-open for numpy conversion (verify consumes the stream)
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        width, height = pil_img.size
        metrics["resolution"] = f"{width}x{height}"
        metrics["width"] = width
        metrics["height"] = height

        if width < 200 or height < 200:
            issues.append(f"Too low resolution ({width}x{height} pixels, min 200x200 required)")

        # Convert PIL to OpenCV BGR/Grayscale
        cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

        # 1. Blur Check via Laplacian Variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        metrics["blur_laplacian_var"] = round(float(laplacian_var), 2)
        if laplacian_var < 55.0:
            issues.append(f"Too blurry (blur score: {laplacian_var:.1f}, min threshold: 55.0)")

        # 2. Darkness Check
        mean_brightness = np.mean(gray)
        metrics["mean_brightness"] = round(float(mean_brightness), 2)
        if mean_brightness < 35.0:
            issues.append(f"Too dark (brightness score: {mean_brightness:.1f}, min threshold: 35.0)")

        # 3. Brightness / Overexposure Check
        if mean_brightness > 225.0:
            issues.append(f"Too bright / overexposed (brightness score: {mean_brightness:.1f}, max threshold: 225.0)")
        
        # Also check high intensity pixel ratio (pixels > 245)
        overexposed_ratio = np.sum(gray > 245) / float(gray.size)
        metrics["overexposed_ratio"] = round(float(overexposed_ratio), 4)
        if overexposed_ratio > 0.40 and mean_brightness > 200.0:
            issues.append(f"Excessive overexposure ({overexposed_ratio*100:.1f}% washed out pixels)")

    except Exception as e:
        return {
            "is_acceptable": False,
            "issues": [f"Invalid or corrupted image format: {str(e)}"],
            "message": "Image file could not be processed. Please upload a valid image file (JPEG, PNG, WEBP).",
            "metrics": {}
        }

    is_acceptable = len(issues) == 0

    if not is_acceptable:
        message = "Image quality is insufficient for reliable assessment. Please upload a clearer crop image."
    else:
        message = "Image quality check passed successfully."

    return {
        "is_acceptable": is_acceptable,
        "issues": issues,
        "message": message,
        "metrics": metrics
    }
