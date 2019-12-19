from glob import glob
import argparse
import logging
import time
import sys
import os

from lib.api import apiController
from lib.vpn import vpnController
from lib.proxy import proxyController
import multiprocessing

logging.basicConfig()
log = logging.getLogger('App.CLI')


def begin(args):

    queues = {}
    for t in ['api', 'vpn', 'pxy']:
        queues[t] = {
            'running': multiprocessing.Event(),
            'change': multiprocessing.Event(),
            'shutdown': multiprocessing.Event(),
        }

    # Activate All Services
    api = apiController(args, queues)
    vpn = vpnController(args, queues)
    pxy = proxyController(args, queues)

    # Launch Services Seperately from Main Process
    processes = []
    processes.append(multiprocessing.Process(target=api._process))
    processes.append(multiprocessing.Process(target=vpn._process))
    processes.append(multiprocessing.Process(target=pxy._process))

    # Should we shutdown?
    def should_shutdown():
        for t in ['api', 'vpn', 'pxy']:
            if queues[t]['shutdown'].is_set() is False:
                return False
        return True

    # Main Application Loop Logic
    log.info("Starting Launching Services")
    for p in processes:
        p.start()

    # Listen to Events for shutdown (Mostly API Call)
    while should_shutdown() is False:
        time.sleep(1)

    log.info("Shutting Down Services")
    # Allow time for the processes to end
    time.sleep(30)

    # Force Shutdown if Processes can't gracefully.
    log.info("Forcing Down Any Services Not Gracefully Exiting")
    for p in processes:
        if p.is_alive():
            p.terminate()

    sys.exit()


def is_valid_configs(par, arg):
    return list(f for f in glob(arg, recursive=True) if os.access(f, os.R_OK))


def is_valid_executable(parser, arg):
    if not os.path.exists(arg):
        par.error("`openvpn_location` = `%s` does not exist!" % arg)
    else:
        if os.access(arg, os.R_OK + os.X_OK):
            return arg
        else:
            par.error(
                "Application cannot read, or execute the `openvpn_location` = `%s`"
                % arg)


def need_help(args):
    par.print_help()
    sys.exit()


par = argparse.ArgumentParser(description="VPN-Rotator, (OpenVPN)",
                              epilog="Contact us on GitHub if Broken")

par.add_argument('-vpn_configs', '-vc', required=True,
                 help="Configuration Files, or Folder containing Configs (*.ovpn)",
                 metavar="FILE", type=lambda x: is_valid_configs(par, x))

par.add_argument('-openvpn_location', '-ol', required=True,
                 help="OpenVPN Binary Location, use this if not in $PATH",
                 metavar="FILE", type=lambda x: is_valid_executable(par, x))

par.add_argument('-api_host', '-ah', default='0.0.0.0', type=str, nargs='?',
                 help="""Set api listening host (default: %(default)s)""")

par.add_argument('-api_port', '-ap', default=7777, type=int, nargs='?',
                 help="""Set api listening port (default: %(default)s)""")

par.add_argument('-proxy_host', '-ph', default='0.0.0.0', type=str, nargs='?',
                 help="""Set proxy listening host (default: %(default)s)""")

par.add_argument('-proxy_port', '-pp', default=9999, type=int, nargs='?',
                 help="""Set proxy listening port (default: %(default)s)""")

par.set_defaults(func=begin)

args = None

if __name__ == '__main__':
    # Parse Args from CLI
    args = par.parse_args().__dict__

    args['base_path'] = os.path.dirname(os.path.realpath(__file__))

    args['func'](args)