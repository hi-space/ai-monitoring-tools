import redis

class RedisQueue(object):
    def __init__(self, name, max_size, **redis_kwargs):
        self.key = name
        self.max_size = max_size
        self.rq       = redis.Redis(**redis_kwargs)

    def size(self):
        return self.rq.llen(self.key)

    def isEmpty(self):
        return self.size() == 0

    def put(self, element):
        self.rq.lpush(self.key, element) # left push 

    def put_and_trim(self, element):
        self.put(element) # left push
        self.rq.ltrim(self.key, 0, self.max_size-1)

    def get(self, isBlocking=False, timeout=None):
        if isBlocking:
            element = self.rq.brpop(self.key, timeout=timeout)
            element = element[1] # key[0], value[1]
        else:
            element = self.rq.rpop(self.key) # right pop

        return element
