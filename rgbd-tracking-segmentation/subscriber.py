import zmq
import pickle as pkl
from redis_queue import RedisQueue

class ZeroMQSubscriber(object):
    def __init__(self, host, port):
        self.s = zmq.Context().socket(zmq.SUB)
        self.s.bind("tcp://%s:%d" % (host, port))
        self.s.setsockopt_string(zmq.SUBSCRIBE, str(''))

    def zmq_recv_pyobj(self):
        return self.s.recv_pyobj()

    def zmq_recv(self):
        return self.s.recv()

class RedisSubscriber(object):
    def __init__(self, topic, host='localhost', port=6379, db=0):
        self.rqueue = RedisQueue(topic, 1, host=host, port=port, db=db)

    def redis_recv_pyobj(self, blocking=True):
        item = self.rqueue.get(isBlocking=blocking)
        if item is None:
            return None
        return pkl.loads(item)

    def redis_recv(self, blocking=True):
        return self.rqueue.get(isBlocking=blocking)

class DetectionSubscriber(ZeroMQSubscriber):

    def __init__(self, port, host="127.0.0.1"):
        super(DetectionSubscriber, self).__init__(host, port)

    def recv_pyobj(self):
        return self.zmq_recv_pyobj()

    def recv(self):
        return self.zmq_recv()
