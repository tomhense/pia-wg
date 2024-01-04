# pia-wg

A WireGuard configuration utility for Private Internet Access

This is a Python utility that generates WireGuard configuration files for the Private Internet Access VPN service. This allows you to take advantage of the WireGuard protocol without relying on PIA's proprietary client.

This was created by reverse engineering the [manual-connections](https://github.com/pia-foss/manual-connections) script released by PIA. At this stage, the tool is a quick and dirty attempt to get things working. It could break at any moment if PIA makes changes to their API.

pia-wg runs on both Windows and Linux.

This is just a cli version of the [original tool](https://github.com/hsand/pia-wg), also I packaged it into a proper python package.

## Install

### Option 1: Build from source

1. Clone the project and cd into it
2. Make sure you have the `build` package installed: `pip install build`
3. Execute `pythom -m build` to build to package
4. Install the wheel in the dist folder with `pip install`

### Option 2: Download a wheel from the releases

1. Download the release wheel
2. Install it with `pip install`

## Usage

```plaintext
usage: pia_wg [-h] [--list] [--region REGION] [--username USERNAME]
              [--password PASSWORD] [--output OUTPUT]

PIA Wireguard

options:
  -h, --help            show this help message and exit
  --list, -l            List available regions
  --region REGION, -r REGION
                        Region to connect to
  --username USERNAME, -u USERNAME
                        PIA username
  --password PASSWORD, -p PASSWORD
                        PIA password
  --output OUTPUT, -o OUTPUT
                        Where to save the config file
```

## Check everything is working

Visit https://dnsleaktest.com/ to see your new IP and check for DNS leaks.
