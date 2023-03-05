import gevent
from gevent import monkey

monkey.patch_all()
gevent.config.loop = "libuv"
gevent.config.resolver = ["dnspython", "ares", "thread", "block"]
