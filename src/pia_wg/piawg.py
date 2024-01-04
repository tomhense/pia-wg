import json
import subprocess
import urllib.parse
from importlib.resources import path

import requests
from requests_toolbelt.adapters import host_header_ssl


class PiaWG:
    def __init__(self):
        self.server_list = {}
        self.get_server_list()
        self.region = None
        self.token = None
        self.publickey = None
        self.privatekey = None
        self.connection = None

    def get_server_list(self):
        r = requests.get('https://serverlist.piaservers.net/vpninfo/servers/v4')
        # Only process first line of response, there's some base64 data at the end we're ignoring
        data = json.loads(r.text.splitlines()[0])
        for server in data['regions']:
            self.server_list[server['name']] = server

    def set_region(self, region_name):
        self.region = region_name

    def get_token(self, username, password):
        # Get common name and IP address for metadata endpoint in region
        meta_cn = self.server_list[self.region]['servers']['meta'][0]['cn']
        meta_ip = self.server_list[self.region]['servers']['meta'][0]['ip']

        # Some tricks to verify PIA certificate, even though we're sending requests to an IP and not a proper domain
        # https://toolbelt.readthedocs.io/en/latest/adapters.html#requests_toolbelt.adapters.host_header_ssl.HostHeaderSSLAdapter
        s = requests.Session()
        s.mount('https://', host_header_ssl.HostHeaderSSLAdapter())

        # We use a local certificate file to verify the PIA certificate, this certificate is included in the package
        with path('pia_wg', 'ca.rsa.4096.crt') as ca_file:
            s.verify = ca_file.resolve()

            r = s.get(f"https://{meta_ip}/authv3/generateToken", headers={"Host": meta_cn}, auth=(username, password))
            data = r.json()
            if r.status_code == 200 and data['status'] == 'OK':
                self.token = data['token']
                return True
            else:
                return False

    def generate_keys(self):
        self.privatekey = subprocess.run(['wg', 'genkey'], stdout=subprocess.PIPE, encoding="utf-8").stdout.strip()
        self.publickey = subprocess.run(['wg', 'pubkey'], input=self.privatekey, stdout=subprocess.PIPE,
                                        encoding="utf-8").stdout.strip()

    def addkey(self):
        # Get common name and IP address for wireguard endpoint in region
        cn = self.server_list[self.region]['servers']['wg'][0]['cn']
        ip = self.server_list[self.region]['servers']['wg'][0]['ip']

        s = requests.Session()
        s.mount('https://', host_header_ssl.HostHeaderSSLAdapter())

        with path('pia_wg', 'ca.rsa.4096.crt') as ca_file:
            s.verify = ca_file.resolve()

            r = s.get(f"https://{ip}:1337/addKey?pt={urllib.parse.quote(self.token)}&pubkey={urllib.parse.quote(self.publickey)}", headers={"Host": cn})
            if r.status_code == 200 and r.json()['status'] == 'OK':
                self.connection = r.json()
                return True, r.content
            else:
                return False, r.content
