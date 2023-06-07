import core
import sys
import typing
import cv2 as cv
import numpy as np
import fpsGraph

if len(sys.argv) < 2:
  print(f'Error: want 2 argument but {len(sys.argv)} was given.')
  print(sys.argv)
  sys.exit(-1)

csv_file = open("fps.csv", "w")
csv_file.write("frame,fps\n")

n = 1
g = fpsGraph.FPSGraph([1920, 200], 60, 120)

def overlay_image_alpha(img, img_overlay, x, y, alpha_mask):
    """Overlay `img_overlay` onto `img` at (x, y) and blend using `alpha_mask`.

    `alpha_mask` must have same HxW as `img_overlay` and values in range [0, 1].
    """
    # Image ranges
    y1, y2 = max(0, y), min(img.shape[0], y + img_overlay.shape[0])
    x1, x2 = max(0, x), min(img.shape[1], x + img_overlay.shape[1])

    # Overlay ranges
    y1o, y2o = max(0, -y), min(img_overlay.shape[0], img.shape[0] - y)
    x1o, x2o = max(0, -x), min(img_overlay.shape[1], img.shape[1] - x)

    # Exit if nothing to do
    if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
        return

    # Blend overlay within the determined ranges
    img_crop = img[y1:y2, x1:x2]
    img_overlay_crop = img_overlay[y1o:y2o, x1o:x2o]
    alpha = alpha_mask[y1o:y2o, x1o:x2o, np.newaxis]
    alpha_inv = 1.0 - alpha

    img_crop[:] = alpha * img_overlay_crop + alpha_inv * img_crop

def on_fps_receive(frame: typing.Any, fps: float):
  global n
  csv_file.write(f"{n},{fps}\n")
  if fps < 29 and n > 30:
    cv.imwrite(f"extract/frame_{n}.jpg", frame)
  g.on_next_frame(fps)
  img = g.get_graph()
  img = np.roll(img, 3, axis=2)
  alpha = img[:,:,3]/255.0
  img = cv.cvtColor(img, cv.COLOR_RGBA2BGR)
  overlay_image_alpha(frame, img, 0, 1080-200, alpha)
  cv.imwrite(f"img/{n}.jpg", frame)
  n += 1

c = core.FPSCore(sys.argv[1], on_fps_receive, None)
try:
  c.start_parse()
except Exception as e:
  print(e)
  exit(-1)
