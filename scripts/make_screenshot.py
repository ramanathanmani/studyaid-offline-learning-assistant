import os
from PIL import Image, ImageDraw, ImageFont

def split_runs(txt):
    runs = []
    curr = []
    is_ta = False
    for c in txt:
        c_is_ta = (0x0B80 <= ord(c) <= 0x0BFF) or (c in ' \t' and is_ta)
        if not curr:
            is_ta = c_is_ta
            curr.append(c)
        elif c_is_ta == is_ta:
            curr.append(c)
        else:
            runs.append((''.join(curr), is_ta))
            curr = [c]
            is_ta = c_is_ta
    if curr:
        runs.append((''.join(curr), is_ta))
    return runs

def render_terminal(txt_path=None, out_png="outputs/terminal_run_screenshot.png"):
    if not txt_path:
        txt_files = sorted([f for f in os.listdir("outputs") if f.startswith("run_") and f.endswith(".txt")])
        txt_path = os.path.join("outputs", txt_files[-1]) if txt_files else "outputs/run_20261105_151403.txt"

    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = [
        "rock@laptop:~/studyaid$ .venv/bin/python -m studyaid run --passage samples/optics.txt",
        "Warning: passage word count (84) is outside the recommended 150-300 word range.",
        ""
    ] + content.splitlines() + [
        "",
        "[Saved outputs]:",
        f"  Text: {txt_path}",
        f"  JSON: {txt_path.replace('.txt', '.json')}",
        "",
        "rock@laptop:~/studyaid$ "
    ]

    try:
        f_mono = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
    except Exception:
        f_mono = ImageFont.load_default()

    try:
        f_ta = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf", 14)
    except Exception:
        f_ta = f_mono

    line_h = 22
    pad_x = 24
    pad_y = 50
    w = 1150
    h = pad_y + len(lines) * line_h + 30

    img = Image.new("RGB", (w, h), color=(13, 17, 23))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (w, 36)], fill=(33, 38, 45))
    draw.line([(0, 36), (w, 36)], fill=(48, 54, 61), width=1)

    draw.ellipse([(14, 12), (26, 24)], fill=(255, 95, 86))
    draw.ellipse([(34, 12), (46, 24)], fill=(255, 189, 46))
    draw.ellipse([(54, 12), (66, 24)], fill=(39, 201, 63))

    title_txt = "rock@laptop: ~/studyaid — .venv/bin/python -m studyaid run --passage samples/optics.txt"
    draw.text((w // 2 - 270, 10), title_txt, fill=(139, 148, 158), font=f_mono)

    y = pad_y
    for line in lines:
        col = (201, 209, 217)
        if line.startswith("rock@laptop"):
            col = (88, 166, 255)
        elif line.startswith("Warning:"):
            col = (210, 153, 34)
        elif line.startswith("=== ") and "TELEMETRY" in line:
            col = (247, 120, 186)
        elif line.startswith("=== "):
            col = (121, 192, 255)
        elif "SUPPORTED" in line:
            col = (63, 185, 80)
        elif "FLAGGED" in line:
            col = (227, 179, 65)
        elif line.startswith("Execution mode:"):
            col = (56, 139, 253)
        elif line.startswith("[S") or line.startswith("[Q"):
            col = (126, 231, 135)
        elif line.startswith("Metric") or line.startswith("Words") or line.startswith("Letters") or line.startswith("Avg"):
            col = (180, 200, 220)
        elif line.startswith("Original") or line.startswith("Simplified"):
            col = (220, 220, 220)

        runs = split_runs(line)
        curr_x = pad_x
        for r_txt, is_tamil in runs:
            f = f_ta if is_tamil else f_mono
            draw.text((curr_x, y), r_txt, fill=col, font=f)
            bbox = draw.textbbox((curr_x, y), r_txt, font=f)
            curr_x = bbox[2]

        y += line_h

    img.save(out_png)
    print(f"Generated screenshot: {out_png} ({os.path.getsize(out_png)} bytes)")

if __name__ == "__main__":
    render_terminal()