# API-Openvpn-Proxy-Server
An application to spin up a OpenVPN Server and Proxy Server, then manage, change, restart it from a HTTP API

```
# python app.py --help
usage: app.py [-h] --vpn_configs PATH --openvpn_location FILE

VPN-Rotator, (OpenVPN, HTTP Proxy Server, API Management)

optional arguments:
  -h, --help            show this help message and exit
  --vpn_configs PATH, -vc PATH
                        Configuration Files, or Folder containing Configs
                        (*.ovpn) (Globs allowed)
  --openvpn_location FILE, -ol FILE
                        OpenVPN Binary Location, use this if not in $PATH
                        (default: None)

Contact us on GitHub https://github.com/a904guy/API-Openvpn-Proxy-Server/
```
