import argparse
import os.path
from getpass import getpass

from pia_wg.piawg import PiaWG


def region_list() -> list[str]:
    pia = PiaWG()
    return sorted(list(pia.server_list.keys()))


def generate_config(region: str, username: str, password: str) -> dict:
    pia = PiaWG()

    # Check region
    if region not in pia.server_list.keys():
        raise Exception("Invalid region")

    # Set region
    pia.set_region(region)

    # Generate public and private key pair
    pia.generate_keys()

    # Get token
    if not pia.get_token(username, password):
        raise Exception("Error logging in, please try again...")

    # Add key
    status, response = pia.addkey()
    if not status:
        raise Exception("Error adding key to server", response)

    return {
        "interface": {
            "address": pia.connection["peer_ip"],
            "private_key": pia.privatekey,
            "dns": [
                pia.connection["dns_servers"][0],
                pia.connection["dns_servers"][1]
            ],
        },
        "peer": {
            "public_key": pia.publickey,
            "endpoint": f"{pia.connection['server_ip']}:1337",
            "allowed_ips": "0.0.0.0/0",
            "persistent_keepalive": 25
        }
    }


def config_to_string(config: dict) -> str:
    interface = config["interface"]
    peer = config["peer"]
    return '[Interface]\n' \
        + f'Address = {interface["address"]}\n' \
        + f'PrivateKey = {interface["private_key"]}\n' \
        + f'DNS = {",".join(interface["dns"])}\n\n' \
        + '[Peer]\n' \
        + f'PublicKey = {peer["public_key"]}\n' \
        + f'Endpoint = {peer["endpoint"]}\n' \
        + f'AllowedIPs = {peer["allowed_ips"]}\n' \
        + f'PersistentKeepalive = {peer["persistent_keepalive"]}\n'


def main() -> None:
    argparser = argparse.ArgumentParser(description='PIA Wireguard')
    argparser.add_argument('--list', '-l', action='store_true', help='List available regions')
    argparser.add_argument('--region', '-r', help='Region to connect to')
    argparser.add_argument('--username', '-u', help='PIA username')
    argparser.add_argument('--password', '-p', help='PIA password')
    argparser.add_argument('--output', '-o', default="wireguard.conf", help='Where to save the config file')

    args = argparser.parse_args()

    if args.list:
        print("Available regions:")
        for region in region_list():
            print(region)
        exit(0)

    if not args.region:
        print("Please specify a region")
        exit(1)

    if os.path.exists(args.output):
        print("Config file already exists, please delete it first")
        exit(1)

    if not args.username:
        args.username = input("Enter PIA username: ")
    if not args.password:
        args.password = getpass("Enter PIA password: ")

    print(f"Saving configuration file {args.output}")
    config = generate_config(args.region, args.username, args.password)
    with open(args.output, 'w') as configFile:
        configFile.write(config_to_string(config))


if __name__ == '__main__':
    main()
