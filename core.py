import typing
import cv2 as cv
import numpy as np
from cvlog import log

_good_pixel_fmt = [
    cv.VideoWriter.fourcc('I', '4', '2', '0'),
    cv.VideoWriter.fourcc('4', '2', '0', 'P'),
    cv.VideoWriter.fourcc('4', '2', '2', 'P'),
    cv.VideoWriter.fourcc('4', '4', '4', 'P'),
]

_good_fourcc = [
    "ULH0",
    # TODO more
]


class FPSCore(object):

    def __init__(self, video_path: str, cb: typing.Callable[[typing.Any, float], None], dump_dup: str) -> None:
        self.video_path = video_path
        self.cb = cb
        self.dump_dup = dump_dup

    def start_parse(self):
        cap = cv.VideoCapture(self.video_path)

        if not cap.isOpened():
            raise Exception(f'Cannot open video file. path: {self.video_path}')

        fps = cap.get(cv.CAP_PROP_FPS)
        if fps < 60.0:
            log(f'Warning: fps = {fps}, video FPS lower than 60.0 may result invalid report.')

        pix_format = cap.get(cv.CAP_PROP_CODEC_PIXEL_FORMAT)
        if pix_format not in _good_pixel_fmt:
            log(f'Warning: recommend pixel format YUV 420p/422p/444p.')

        fourcc_code = int(cap.get(cv.CAP_PROP_FOURCC))
        fourcc = chr(fourcc_code & 0xff) + chr((fourcc_code >> 8) & 0xff) + \
            chr((fourcc_code >> 16) & 0xff) + chr((fourcc_code >> 24) & 0xff)
        if fourcc not in _good_fourcc:
            log(
                f'Warning: recommend video format is {_good_fourcc}, current={fourcc}')

        img1 = None
        img2 = None
        w, h = None, None
        nframe = 0
        real_frames = []
        thresholds = 0
        while True:
            nframe += 1
            ret, frame = cap.read()
            
            if not ret:
                print('Cannot receive frame (stream end?). Exiting...')
                break
            if img1 is None:
                img1 = frame
                real_frames.append(True)
                log(f'frame {nframe}, real_fps={1}')
                self.cb(np.copy(frame), 1)
                continue
            if w is None:
                w = len(img1[0])
                h = len(img1)
            img2 = frame
            diff = cv.absdiff(img2, img1)
            img1 = img2
            diff_norm = np.abs(diff).sum()
            avg_diff_norm = diff_norm/(w*h)

            if diff_norm == 0 and self.dump_dup:
                cv.imwrite(f"{self.dump_dup}_{nframe}_0.jpg", img1)
                cv.imwrite(f"{self.dump_dup}_{nframe}_1.jpg", img2)

            if avg_diff_norm > thresholds:
                real_frames.append(True)
            else:
                real_frames.append(False)

            if len(real_frames) > fps:
                del real_frames[0]

            real_frame_count = real_frames.count(True)
            log(f'frame {nframe}, real_fps={real_frame_count}')
            self.cb(np.copy(frame), real_frame_count)
