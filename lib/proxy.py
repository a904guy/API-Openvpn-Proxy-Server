from box import Box
import logging
import multiprocessing
import sys

logging.basicConfig()
log = logging.getLogger('App.PROXY')


class proxyController:
    args = Box()

    running = multiprocessing.Event()
    change = multiprocessing.Event()
    shutdown = multiprocessing.Event()

    plex = {}

    def __init__(self, args: dict, queues):
        # CLI Variables
        self.args = Box(args)
        self.running = queues['pxy']['running']
        self.change = queues['pxy']['change']
        self.shutdown = queues['pxy']['shutdown']
        self.plex = queues

    def _process(self):
        log.info("Starting")

        self.running.set()
        while not self.shutdown.is_set():
            import proxy
            proxy.main(input_args=[])
        sys.exit()
