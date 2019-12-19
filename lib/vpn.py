import logging
from box import Box
import multiprocessing
import subprocess
from subprocess import PIPE, Popen
import random
import time
import os
import sys

logging.basicConfig()
log = logging.getLogger('App.VPN')


class vpnController:
    args = Box()

    running = multiprocessing.Event()
    change = multiprocessing.Event()
    shutdown = multiprocessing.Event()

    plex = {}

    def __init__(self, args: dict, queues):
        # CLI Variables
        self.args = Box(args)
        self.running = queues['vpn']['running']
        self.change = queues['vpn']['change']
        self.shutdown = queues['vpn']['shutdown']
        self.plex = queues

    # Internal method to be launched in multiprocessing.
    def _process(self):
        log.info("Starting")
        self.running.set()

        while not self.shutdown.is_set():
            self.launch_openvpn()

        log.info("Shutting Down")
        sys.exit()

    def launch_openvpn(self):
        log.info('Launching OpenVPN')
        config = random.choice(self.args['vpn_configs'])
        log.info('Config: %s' % config)
        with Popen('%s --config %s' % (self.args['openvpn_location'], config),
                   cwd=os.path.dirname(config)
                   ) as process:
            log.info("Process Started")
            self.change.clear()
            self.running.set()
            while not self.restart():
                time.sleep(0.3)
            process.terminate()
        self.running.clear()

    def restart(self):
        if self.change.is_set():
            return True
        return False
