import cv2
import os
import platform
import time
from datetime import datetime

CONFIG = {
    "camera_index": 0,
    "backend": "auto",
    "resolution": (1280, 720),
    "fps_target": 30,
    "exposure": -6,
    "gain_iso": 100,
    "manual_exposure_mode": True,
    "output_dir": "captures",
    "jpeg_quality": 95,
    "burst_hold_timeout": 0.35,
    "resolution_presets": [(640, 480), (1280, 720), (1920, 1080)],
}

WINDOW_MAIN = "Live Preview - Camera Control"
WINDOW_CTRL = "Kontrol Kamera (Exposure / Gain)"

def ensure_output_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def resolve_backend(cfg):
    backend = cfg.get("backend")
    if backend != "auto":
        return backend

    system = platform.system()
    if system == "Windows":
        return cv2.CAP_DSHOW
    elif system == "Linux":
        return cv2.CAP_V4L2
    return None


def open_camera(cfg):
    index = cfg["camera_index"]
    backend = resolve_backend(cfg)

    if backend is not None:
        cap = cv2.VideoCapture(index, backend)
        if cap.isOpened():
            return cap, backend
        cap.release()
        print(f"[INFO] Gagal buka kamera dengan backend {backend}, "
              f"mencoba mode default OpenCV...")

    cap = cv2.VideoCapture(index)
    return cap, None

def apply_camera_properties(cap, cfg):
    width, height = cfg["resolution"]
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, cfg["fps_target"])

    if cfg.get("manual_exposure_mode"):
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)

    if cfg.get("exposure") is not None:
        cap.set(cv2.CAP_PROP_EXPOSURE, cfg["exposure"])

    if cfg.get("gain_iso") is not None:
        cap.set(cv2.CAP_PROP_GAIN, cfg["gain_iso"])


def save_frame(frame, output_dir, prefix="capture", jpeg_quality=95):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    filename = f"{prefix}_{ts}.jpg"
    filepath = os.path.join(output_dir, filename)
    cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
    return filepath


def draw_overlay(frame, fps, burst_active, cam_props):
    h, w = frame.shape[:2]
    lines = [
        f"Resolusi: {w}x{h}  |  FPS: {fps:.1f}",
        f"Exposure: {cam_props.get('exposure', '-')}  |  Gain/ISO: {cam_props.get('gain', '-')}",
        "SPACE/C=Capture | B(tahan)=Burst | R=Ganti Resolusi | Q/ESC=Keluar",
    ]
    if burst_active:
        lines.insert(0, ">>> BURST CAPTURE AKTIF <<<")

    y = 25
    for line in lines:
        cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (0, 255, 0), 1, cv2.LINE_AA)
        y += 24

    if burst_active:
        cv2.circle(frame, (w - 25, 25), 10, (0, 0, 255), -1)

    return frame


def _nop(_val):
    pass

# GitHub: https://github.com/puteriazli

def setup_control_window(cfg):
    cv2.namedWindow(WINDOW_CTRL, cv2.WINDOW_NORMAL)

    init_exp = int(cfg.get("exposure") or 0)
    init_gain = int(cfg.get("gain_iso") or 0)

    cv2.createTrackbar("Exposure", WINDOW_CTRL, 0, 26, _nop)
    try:
        cv2.setTrackbarMin("Exposure", WINDOW_CTRL, -13)
        cv2.setTrackbarMax("Exposure", WINDOW_CTRL, 13)
        cv2.setTrackbarPos("Exposure", WINDOW_CTRL, max(-13, min(13, init_exp)))
        cfg["_exposure_native_range"] = True
    except AttributeError:
        cv2.setTrackbarPos("Exposure", WINDOW_CTRL, max(0, min(26, init_exp + 13)))
        cfg["_exposure_native_range"] = False
        print("[INFO] OpenCV versi ini belum mendukung setTrackbarMin/Max, "
              "trackbar Exposure memakai offset (tampilan 0-26 -> nilai -13..13).")

    cv2.createTrackbar("Gain-ISO (0-255)", WINDOW_CTRL, init_gain, 255, _nop)


def read_control_window(cap, cfg):
    raw_exp = cv2.getTrackbarPos("Exposure", WINDOW_CTRL)
    exp_val = raw_exp if cfg.get("_exposure_native_range") else raw_exp - 13
    gain_val = cv2.getTrackbarPos("Gain-ISO (0-255)", WINDOW_CTRL)
    cap.set(cv2.CAP_PROP_EXPOSURE, exp_val)
    cap.set(cv2.CAP_PROP_GAIN, gain_val)
    return {"exposure": exp_val, "gain": gain_val}

# LinkedIn: https://www.linkedin.com/in/puteriazli

def main():
    cfg = CONFIG
    output_dir = ensure_output_dir(cfg["output_dir"])

    cap, used_backend = open_camera(cfg)

    if not cap.isOpened():
        print("[ERROR] Tidak bisa membuka kamera dengan camera_index="
              f"{cfg['camera_index']}.")
        print("        Coba ganti CONFIG['camera_index'] ke 1, 2, dst., pastikan "
              "kamera tidak dipakai aplikasi lain (Zoom/Teams/OBS),")
        print("        dan cek permission kamera di Windows: Settings > Privacy "
              "> Camera.")
        return
    else:
        print(f"[INFO] Kamera terbuka (backend={used_backend}).")

    apply_camera_properties(cap, cfg)

    cv2.namedWindow(WINDOW_MAIN, cv2.WINDOW_NORMAL)
    setup_control_window(cfg)

    presets = cfg["resolution_presets"]
    preset_idx = presets.index(cfg["resolution"]) if cfg["resolution"] in presets else 0

    burst_key = ord('b')
    last_burst_time = 0.0
    burst_active = False
    burst_session_dir = None
    burst_count = 0

    prev_time = time.time()
    fps = 0.0

    print("=== Camera Control Script ===")
    print("SPACE / C : ambil 1 foto")
    print("B (tahan) : burst capture selama ditahan")
    print("R         : ganti preset resolusi")
    print("Q / ESC   : keluar\n")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[WARNING] Gagal membaca frame dari kamera.")
                break

            now = time.time()
            dt = now - prev_time
            if dt > 0:
                fps = 1.0 / dt
            prev_time = now

            cam_props = read_control_window(cap, cfg)
            key = cv2.waitKey(1) & 0xFF
            
            if key == burst_key:
                if not burst_active:
                    burst_active = True
                    burst_count = 0
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    burst_session_dir = ensure_output_dir(
                        os.path.join(output_dir, f"burst_{ts}"))
                    print(f"[BURST] Mulai burst -> folder: {burst_session_dir}")

                last_burst_time = now
                path = save_frame(frame, burst_session_dir, prefix="burst",
                                   jpeg_quality=cfg["jpeg_quality"])
                burst_count += 1
                print(f"[BURST] Frame #{burst_count} disimpan: {path}")

            elif burst_active and (now - last_burst_time) > cfg["burst_hold_timeout"]:
                burst_active = False
                print(f"[BURST] Selesai. Total {burst_count} frame disimpan.\n")

            if key in (32, ord('c'), ord('C')) and not burst_active:
                path = save_frame(frame, output_dir, prefix="capture",
                                   jpeg_quality=cfg["jpeg_quality"])
                print(f"[CAPTURE] Foto disimpan: {path}")

            if key in (ord('r'), ord('R')):
                preset_idx = (preset_idx + 1) % len(presets)
                new_w, new_h = presets[preset_idx]
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, new_w)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, new_h)
                print(f"[RESOLUSI] Diganti ke {new_w}x{new_h}")

            if key in (27, ord('q'), ord('Q')):
                print("Keluar dari program...")
                break

            display_frame = draw_overlay(frame.copy(), fps, burst_active, cam_props)
            cv2.imshow(WINDOW_MAIN, display_frame)

            if cv2.getWindowProperty(WINDOW_MAIN, cv2.WND_PROP_VISIBLE) < 1:
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

# Kaggle: https://www.kaggle.com/puteriameliaazli

if __name__ == "__main__":
    main()
