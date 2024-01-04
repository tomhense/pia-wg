import argparse
import os.path
from getpass import getpass

from pia_wg.piawg import PiaWG


def main():
    argparser = argparse.ArgumentParser(description='PIA Wireguard')
    argparser.add_argument('--list', '-l', action='store_true', help='List available regions')
    argparser.add_argument('--region', '-r', help='Region to connect to')
    argparser.add_argument('--username', '-u', help='PIA username')
    argparser.add_argument('--password', '-p', help='PIA password')
    argparser.add_argument('--output', '-o', default="wireguard.conf", help='Where to save the config file')

    args = argparser.parse_args()
    pia = PiaWG()

    if args.list:
        print("Available regions:")
        for region in sorted(list(pia.server_list.keys())):
            print(region)
        exit(0)

    if not args.region:
        print("Please specify a region")
        exit(1)

    if os.path.exists(args.output):
        print("Config file already exists, please delete it first")
        exit(1)

    if args.region not in pia.server_list.keys():
        print("Invalid region")
        exit(1)

    # Set region
    print(f"Selected {args.region}")
    pia.set_region(args.region)

    if not args.username:
        args.username = input("Enter PIA username: ")
    if not args.password:
        args.password = getpass("Enter PIA password: ")

    # Generate public and private key pair
    pia.generate_keys()

    # Get token
    if not pia.get_token(args.username, args.password):
        print("Error logging in, please try again...")
        exit(1)

    # Add key
    status, response = pia.addkey()
    if not status:
        print("Error adding key to server")
        print(response)
        exit(1)

    config = '[Interface]\n' \
        + f'Address = {pia.connection["peer_ip"]}\n' \
        + f'PrivateKey = {pia.privatekey}\n' \
        + f'DNS = {pia.connection["dns_servers"][0]},{pia.connection["dns_servers"][1]}\n\n' \
        + '[Peer]\n' \
        + f'PublicKey = {pia.connection["server_key"]}\n' \
        + f'Endpoint = {pia.connection["server_ip"]}:1337\n' \
        + 'AllowedIPs = 0.0.0.0/0\n' \
        + 'PersistentKeepalive = 25\n'

    print(f"Saving configuration file {args.output}")
    with open(args.output, 'w') as configFile:
        configFile.write(config)


if __name__ == '__main__':
    main()
