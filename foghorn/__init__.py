import gevent
from gevent import monkey

monkey.patch_all()
gevent.config.loop = "libuv"
