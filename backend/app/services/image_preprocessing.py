import os
import cv2
import numpy as np
from typing import Dict, Any, Tuple
from pathlib import Path

def preprocess_document_image(image_path: str) -> Dict[str, Any]:
    """
    Applies computer vision preprocessing techniques to optimize document images for OCR:
    - Resize normalization (maintaining aspect ratio)
    - Grayscale conversion
    - Contrast Enhancement (CLAHE: Contrast Limited Adaptive Histogram Equalization)
    - Denoising & Sharpening (Unsharp masking)
    - Adaptive Thresholding (Otsu / Sauvola proxy for high-contrast binarization)
    - Deskew / orientation detection where applicable
    
    Saves preprocessed intermediate variants for OCR while preserving the pristine
    original for forensic analysis.
    """
    if not os.path.exists(image_path):
        return {
            "success": False,
            "error": "Image file not found",
            "best_image_path": image_path,
            "original_image_path": image_path
        }

    try:
        orig_img = cv2.imread(image_path)
        if orig_img is None:
            return {
                "success": False,
                "error": "Could not decode image with OpenCV",
                "best_image_path": image_path,
                "original_image_path": image_path
            }

        h, w = orig_img.shape[:2]
        
        # 1. Resize normalization (if image is tiny or excessively huge)
        target_max_dim = 2000
        target_min_dim = 800
        scale = 1.0
        if max(h, w) > target_max_dim:
            scale = target_max_dim / max(h, w)
        elif min(h, w) < target_min_dim:
            scale = target_min_dim / min(h, w)

        if scale != 1.0:
            resized = cv2.resize(orig_img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LANCZOS4)
        else:
            resized = orig_img.copy()

        # 2. Grayscale conversion
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        # 3. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        contrast_enhanced = clahe.apply(gray)

        # 4. Denoising
        denoised = cv2.fastNlMeansDenoising(contrast_enhanced, h=7, templateWindowSize=7, searchWindowSize=21)

        # 5. Unsharp Masking for Edge Sharpening
        gaussian_blur = cv2.GaussianBlur(denoised, (0, 0), 2.0)
        sharpened = cv2.addWeighted(denoised, 1.5, gaussian_blur, -0.5, 0)

        # 6. Adaptive Thresholding / Binarization (Otsu)
        _, binarized = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 7. Detect skew angle using Hough lines or minAreaRect on contours
        skew_angle = 0.0
        try:
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=120)
            if lines is not None:
                angles = []
                for rho, theta in lines[:15]:
                    angle_deg = (theta * 180 / np.pi) - 90
                    if -45 < angle_deg < 45:
                        angles.append(angle_deg)
                if angles:
                    skew_angle = float(np.median(angles))
        except Exception:
            skew_angle = 0.0

        # Save preprocessed variant next to original in preprocessed directory
        path_obj = Path(image_path)
        prep_dir = path_obj.parent.parent / "preprocessed"
        prep_dir.mkdir(parents=True, exist_ok=True)
        
        prep_filename = f"prep_{path_obj.stem}.png"
        prep_filepath = str(prep_dir / prep_filename)
        
        # We save the enhanced contrast & sharpened image (best for modern Deep Learning OCR)
        cv2.imwrite(prep_filepath, sharpened)

        return {
            "success": True,
            "original_dimensions": [w, h],
            "processed_dimensions": [resized.shape[1], resized.shape[0]],
            "skew_angle_deg": round(skew_angle, 2),
            "original_image_path": image_path,
            "best_image_path": prep_filepath,
            "techniques_applied": [
                "Resolution normalization",
                "CLAHE adaptive contrast enhancement",
                "Non-local means denoising",
                "Unsharp mask edge sharpening",
                f"Orientation skew detection ({round(skew_angle, 2)}°)"
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "best_image_path": image_path,
            "original_image_path": image_path
        }
