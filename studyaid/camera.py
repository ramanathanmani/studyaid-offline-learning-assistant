import os
import sys
import shutil
import subprocess

def is_camera_available(device_path="/dev/video0"):
    return os.path.exists(device_path)

def capture_image_ffmpeg(out_path="textbook_capture.jpg", device_path="/dev/video0"):
    """Capture a single frame from webcam using ffmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "v4l2",
        "-video_size", "1280x720",
        "-i", device_path,
        "-vframes", "1",
        out_path
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        return res.returncode == 0 and os.path.exists(out_path)
    except Exception:
        return False

def capture_image_fswebcam(out_path="textbook_capture.jpg", device_path="/dev/video0"):
    """Capture a single frame using fswebcam."""
    cmd = ["fswebcam", "-d", device_path, "-r", "1280x720", "--no-banner", out_path]
    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        return res.returncode == 0 and os.path.exists(out_path)
    except Exception:
        return False

def capture_image_opencv(out_path="textbook_capture.jpg", device_index=0):
    """Capture image with live preview using OpenCV."""
    try:
        import cv2
    except ImportError:
        return False

    cap = cv2.VideoCapture(device_index)
    if not cap.isOpened():
        return False

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("\n[Webcam Scanner] Align textbook paragraph in front of camera.")
    print("                Press SPACE to capture snapshot, or 'q' to cancel.")

    captured = False
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Draw targeting box
            h, w = frame.shape[:2]
            cv2.rectangle(frame, (int(w*0.1), int(h*0.15)), (int(w*0.9), int(h*0.85)), (0, 255, 0), 2)
            cv2.putText(frame, "Align textbook text inside box & press SPACE", 
                        (int(w*0.12), int(h*0.10)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("StudyAid - Textbook Scanner", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # SPACE
                cv2.imwrite(out_path, frame)
                captured = True
                break
            elif key == ord('q') or key == 27:  # 'q' or ESC
                break
    except Exception as e:
        print(f"[Webcam] OpenCV GUI error: {e}", file=sys.stderr)
    finally:
        cap.release()
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

    return captured and os.path.exists(out_path)

def ocr_image(image_path="textbook_capture.jpg"):
    """Extract English textbook text from image using Tesseract OCR."""
    # 1. Try python pytesseract
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(image_path)
        txt = pytesseract.image_to_string(img, lang="eng")
        if txt.strip():
            return txt.strip()
    except Exception:
        pass

    # 2. Try tesseract CLI
    if shutil.which("tesseract"):
        try:
            res = subprocess.run(
                ["tesseract", image_path, "stdout", "-l", "eng", "--oem", "1", "--psm", "6"],
                capture_output=True, text=True, timeout=10
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass

    return ""

def scan_textbook_passage(device_path="/dev/video0", out_img="textbook_capture.jpg"):
    """Full workflow: capture image from webcam, run OCR, and return text."""
    print("\n" + "=" * 64)
    print("   StudyAid: Offline Webcam Textbook Scanner")
    print("=" * 64)

    if not is_camera_available(device_path):
        print(f"[Webcam Error] Camera device not found at {device_path}.")
        print("Please check that the USB webcam is plugged into the Raspberry Pi.")
        return ""

    captured = False
    # Attempt OpenCV first for visual alignment
    captured = capture_image_opencv(out_img, device_index=0)

    # Fallback to fswebcam or ffmpeg if OpenCV window wasn't used or failed
    if not captured:
        print("[Webcam] Capturing snapshot via command-line camera utility...")
        if shutil.which("fswebcam"):
            captured = capture_image_fswebcam(out_img, device_path)
        if not captured and shutil.which("ffmpeg"):
            captured = capture_image_ffmpeg(out_img, device_path)

    if not captured or not os.path.exists(out_img):
        print("[Webcam Error] Failed to capture image from camera.")
        return ""

    print(f"[Webcam] Snapshot captured ({out_img}). Running offline OCR...")
    extracted = ocr_image(out_img)

    if not extracted:
        print("[Webcam OCR] No text could be recognized.")
        print("Tip: Ensure adequate lighting and hold the textbook steady.")
        print("     To install Tesseract on Raspberry Pi: sudo apt install -y tesseract-ocr")
        return ""

    # Clean up broken newlines from OCR
    cleaned_lines = [ln.strip() for ln in extracted.splitlines() if ln.strip()]
    cleaned_text = " ".join(cleaned_lines)

    print("\n" + "-" * 64)
    print("Extracted Textbook Passage from Camera:")
    print("-" * 64)
    print(cleaned_text)
    print("-" * 64 + "\n")
    return cleaned_text
