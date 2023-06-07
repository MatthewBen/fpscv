import numpy as np
import cv2 as cv
import sys
import matplotlib.pyplot as plt
import math

plt.ion()
fig, ax = plt.subplots()

x = [ x for x in range(-59, 1) ]
y = [ 0 ] * 60
line, = ax.plot(x, y)
ax.set_ylim([0, 61])
fig.canvas.draw()
fig.canvas.flush_events()

if len(sys.argv) < 2:
  print(f'Error: want 2 argument but {len(sys.argv)} was given.')
  print(sys.argv)
  sys.exit(-1)

video_file = sys.argv[1]

cap = cv.VideoCapture(video_file)

if not cap.isOpened():
  print(f'Cannot open video file. path: {video_file}')
  exit(-1)

fps = cap.get(cv.CAP_PROP_FPS)
if fps < 60.0:
  print(f'Warning: fps = {fps}, video FPS lower than 60.0 may result invalid report.')

good_pixel_fmt = [
  cv.VideoWriter.fourcc('I', '4', '2', '0'),
  cv.VideoWriter.fourcc('4', '2', '0', 'P'),
  cv.VideoWriter.fourcc('4', '2', '2', 'P'),
  cv.VideoWriter.fourcc('4', '4', '4', 'P'),
]
pix_format = cap.get(cv.CAP_PROP_CODEC_PIXEL_FORMAT)
if pix_format not in good_pixel_fmt:
  print(f'Warning: recommend pixel format YUV 420p/422p/444p.')
  
good_fourcc = [
  "ULH0",
  # TODO more
]
fourcc_code = int(cap.get(cv.CAP_PROP_FOURCC))
fourcc = chr(fourcc_code&0xff) + chr((fourcc_code>>8)&0xff) + chr((fourcc_code>>16)&0xff) + chr((fourcc_code>>24)&0xff)
if fourcc not in good_fourcc:
  print(f'Warning: recommend video format is {good_fourcc}, current={fourcc}')

img1 = None
img2 = None

# real_fps = real_frame_count / time = real_frame_count / (frame_count/video_fps)

w, h = None, None
i = -1
real_frames = []
frames = 0
thresholds = 0
while True:
  i += 1
  ret, frame = cap.read()
  if not ret:
    print('Cannot receive frame (stream end?). Exiting...')
    break
  if img1 is None:
    img1 = frame
    real_frames.append(True)
    frames += 1
    continue
  if w is None:
    w = len(img1[0])
    h = len(img1)
  img2 = frame
  diff = cv.absdiff(img1, img2)
  img1 = img2
  diff_norm = np.abs(diff).sum()
  avg_diff_norm = diff_norm/(w*h)
  
  if diff_norm == 0:
    cv.imwrite(f"extract/dup_{i}_1.jpg", img1)
    cv.imwrite(f"extract/dup_{i}_2.jpg", img2)
  
  if avg_diff_norm > thresholds:
    real_frames.append(True)
  else:
    real_frames.append(False)
    
  if len(real_frames) > fps:
    del real_frames[0]
    
  if frames < fps:
    frames += 1
  real_frames.count(True)
  real_fps = real_frames.count(True)
  print(f'frame {i}, real_fps={real_fps}')
  
  del y[0]
  y.append(real_fps)
  del x[0]
  x.append(i)
  line.set_xdata(x)
  line.set_ydata(y)
  ax.set_xlim(x[0], x[-1])
  fig.canvas.draw()
  fig.canvas.flush_events()
  if cv.waitKey(1) == ord('q'):
    break

cap.release()
cv.destroyAllWindows()
  