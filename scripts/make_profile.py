#!/usr/bin/env python3
"""Generate a private runtime profile for local TV filtering."""
import argparse
import os
from pathlib import Path
import re
import secrets


def load_domains(path):
    domains = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        name = line.strip()
        if not name or name.startswith("#"):
            continue
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", name):
            raise ValueError(f"Invalid domain: {name!r}")
        if any(not label or len(label) > 63 for label in name.split(".")):
            raise ValueError(f"Invalid domain labels: {name!r}")
        if name not in domains:
            domains.append(name)
    if not domains:
        raise ValueError("No domains supplied")
    return domains


def make_profile(domains, secret):
    return '''mixed-port: 7890
allow-lan: false
mode: rule
log-level: info
ipv6: true
external-controller: 127.0.0.1:9090
secret: "''' + secret + '''"
dns:
  enable: true
  listen: 127.0.0.1:1053
  ipv6: true
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  nameserver:
    - 223.5.5.5
    - 119.29.29.29
sniffer:
  enable: true
  parse-pure-ip: true
  force-dns-mapping: true
  override-destination: true
  sniff:
    HTTP:
      ports: [80, 8080]
      override-destination: true
    TLS:
      ports: [443, 8443]
    QUIC:
      ports: [443, 8443]
proxies:
  - name: Local-Direct
    type: direct
    udp: true
proxy-groups: []
rules:
  - IP-CIDR,192.168.0.0/16,DIRECT,no-resolve
  - IP-CIDR,127.0.0.0/8,DIRECT,no-resolve
''' + "".join(f"  - DOMAIN-SUFFIX,{d},REJECT\n" for d in domains) + "  - MATCH,DIRECT\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--domains", type=Path,
                        default=Path(__file__).resolve().parents[1] / "assets/ad-domains.txt")
    args = parser.parse_args()
    domains = load_domains(args.domains)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as file:
        file.write(make_profile(domains, secrets.token_hex(24)))
    print(f"Created {args.output} with {len(domains)} domain rules.")
    print("Contains a generated secret; keep the runtime file private.")


if __name__ == "__main__":
    main()
