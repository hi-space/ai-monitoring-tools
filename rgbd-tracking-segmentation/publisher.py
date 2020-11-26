import zmq
import pickle as pkl
from redis_queue import RedisQueue

class ZeroMQPublisher(object):
    def __init__(self, host, port):
        self.s = zmq.Context().socket(zmq.PUB)
        self.s.connect("tcp://%s:%d" % (host, port))

    def zmq_send_pyobj(self, obj):
        self.s.send_pyobj(obj)

    def zmq_send(self, msg):
        self.s.send_string(msg)

class RedisPublisher(object):
    def __init__(self, topic, host='localhost', port=6379, db=0):
        self.rqueue = RedisQueue(topic, 1, host=host, port=port, db=db)

    def redis_send_pyobj(self, obj):
        self.rqueue.put_and_trim(pkl.dumps(obj))

    def redis_send(self, msg):
        self.rqueue.put_and_trim(msg) 

class DetectionPublisher(ZeroMQPublisher):

    def __init__(self, port, host="127.0.0.1"):
        super(DetectionPublisher, self).__init__(host, port)

    def send_pyobj(self, obj):
        self.zmq_send_pyobj(obj)

    def send(self, msg):
        self.zmq_send(msg)