from box import Box
from flask import Flask, jsonify
import logging
import multiprocessing
import sys

logging.basicConfig()
log = logging.getLogger('App.API')


class apiController:
    args = Box()

    running = multiprocessing.Event()
    change = multiprocessing.Event()
    shutdown = multiprocessing.Event()

    plex = {}

    def __init__(self, args: dict, queues):
        # CLI Variables
        self.args = Box(args)
        self.running = queues['api']['running']
        self.change = queues['api']['change']
        self.shutdown = queues['api']['shutdown']
        self.plex = queues

    # Private method for multiprocessing
    def _process(self):
        log.info("Starting")

        app = Flask(__name__)

        @app.route('/')
        @app.route('/status')
        def status():

            status = {}
            for t in ['api', 'vpn', 'pxy']:
                status[t] = {}
                for tt in ['running', 'change', 'shutdown']:
                    status[t][tt] = self.plex[t][tt].is_set()

            return jsonify(status)

        @app.route('/start')
        def start():
            # TODO: Write startup logic
            return status()

        @app.route('/stop')
        def stop():

            for t in ['api', 'vpn', 'pxy']:
                self.plex[t]['running'].clear()
                self.plex[t]['shutdown'].set()
                self.plex[t]['change'].set()

            return status()

        @app.route('/change')
        def change():
            if self.plex['vpn']['change'].is_set() is False:
                self.plex['vpn']['change'].set()

            return status()

        self.running.set()
        while not self.shutdown.is_set():
            app.run()
        sys.exit()
