import logging
import threading
from collections import deque
import zmq
logger = logging.getLogger(__name__)
import cv2
import numpy as np
class CameraSocket(threading.Thread):

    def __init__(self, addr):
        super(CameraSocket, self).__init__(daemon=True)
        logger.info(f"connecting to {addr}")
        context = zmq.Context()
        self._socket = context.socket(zmq.SUB)
        self._socket.setsockopt_string(zmq.SUBSCRIBE, '')
        self._socket.bind(addr)
        self._frames = deque(maxlen=10)
        self._lock = threading.Lock()
        self.start()

    def run(self):
        while True:
            buffer = self._socket.recv()
            # self._socket.send_string('ok')
            logger.debug("frame received")
            bytes_img = buffer
            # # use numpy to construct an array from the bytes
            # png_img = np.frombuffer(bytes_img, dtype='uint8')
            # cv2.imwrite('test.png',png_img)
            # # decode the array into an image
            # numpy_img = cv2.imdecode(png_img, cv2.IMREAD_COLOR)
            # cv2.imwrite('test.png',numpy_img)
            # # base 64 encode string
            # base64_img_str = base64.b64encode(png_img).decode()
            # save img in queue
            
 
            with self._lock:
                self._frames.append(bytes_img)


    def get_frame(self):
        ''' Get frame in bytes if available '''
        with self._lock:
            if not self._frames:
                return
            # frame in bytes
            return self._frames.popleft()
