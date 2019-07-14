import logging
logger = logging.getLogger(__name__)
import threading
from collections import deque
from time import sleep
import zmq
import random

class RadarSocket(threading.Thread):

    def __init__(self, addr):
        super(RadarSocket, self).__init__(daemon=True)
        logger.info(f"connecting to {addr}")
        context = zmq.Context()
        self._values = deque(maxlen=10)
        self._socket = context.socket(zmq.SUB)
        self._socket.setsockopt_string(zmq.SUBSCRIBE, '')
        self._socket.bind(addr)
        self.start()

    def run(self):
        while True:
            buffer = self._socket.recv_string().split()
            radar_id = buffer[0]
            radar_distance = buffer[1]
            logger.debug(f'radar {radar_id} {radar_distance}')
            self._values.append([radar_id, radar_distance])
        # logging.debug('RadarSocket waiting for connection...')
        # connection, address = self._socket.accept()
        # while True:
        #     buffer = connection.recv(self._frame_size)

        #     if len(buffer) > 0:
        #         logging.debug("value received")
        #         bytes_img = buffer
        #         # # use numpy to construct an array from the bytes
        #         # png_img = np.frombuffer(bytes_img, dtype='uint8')
        #         # # decode the array into an image
        #         # numpy_img = cv2.imdecode(png_img, cv2.IMREAD_COLOR)
        #         # # base 64 encode string
        #         # base64_img_str = base64.b64encode(png_img).decode()
        #         # save img in queue
        #         self._values.append(bytes_img)


    def get_value(self):
        ''' Get value if available '''
        if not self._values:
            return

        return self._values.popleft()
