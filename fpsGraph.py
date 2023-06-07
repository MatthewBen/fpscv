import typing
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

matplotlib.use('agg')

class FPSGraph(object):

    def __init__(
        self,
        graphSize: typing.Tuple[int, int],
        video_fps: int,
        window: int
    ) -> None:
        self.graphSize = graphSize
        self.video_fps = video_fps
        self.real_frames = []
        self.n_real_frame = 0
        self.fps_list = []
        self.n_frame = 0
        self.window = window
        
        self.min = 0
        self.max = 0
        self.cur = 0
        
    def on_next_frame(self, fps: float):
      self.n_frame += 1
      cur_fps = fps
      self.fps_list.append(cur_fps)
      if len(self.fps_list) > self.window:
        del self.fps_list[0]
      
      self.max = max(self.max, cur_fps)
      self.min = min(self.min, cur_fps)
      self.cur = cur_fps
      
    def get_graph(self):
      with plt.ion():
        fw = self.graphSize[0]/100.0
        fh = self.graphSize[1]/100.0
        fig = plt.figure(figsize=[fw, fh], dpi=100.0)
        fig.set_facecolor([1, 1, 1, 0.4])
        ax = fig.add_subplot()
        ax.set_facecolor([1, 1, 1, 0.4])
        x = np.arange(self.n_frame-self.window+1, self.n_frame+1)
        y = np.pad(np.array(self.fps_list), [(self.window-len(self.fps_list), 0)], mode='constant', constant_values=0)
        line_30, = ax.plot(x, np.full(self.window, 30), label='30')
        line_30.set_linestyle('dashed')
        ax.plot(x, y, label='fps')
        ax.set_ylim(0, self.video_fps+1)
        ax.set_xlim(x[0], x[-1])
        plt.legend(loc='lower right', bbox_to_anchor=(0,0))
        fig.canvas.draw()
        buf = fig.canvas.tostring_argb()
        plt.close(fig)
        return np.fromstring(buf, dtype=np.uint8, sep='').reshape(fig.canvas.get_width_height()[::-1] + (4,))
      