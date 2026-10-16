#!/usr/bin/env python3
"""EIP-7702 Delegation Checker (CLI) — Srey Leak.

Read-only wallet safety check: does an address carry an active EIP-7702
delegation, and if so, to which contract? Uses any public JSON-RPC endpoint
(no key, no wallet connection, nothing signed).

Usage:
  python eip7702_check.py --address 0xabc... [--rpc https://eth.llamarpc.com]
  python eip7702_check.py --address 0xabc... --rpc https://polygon-rpc.com

Exit codes: 0 = no delegation (clean), 1 = delegation found,
2 = network/parse error.

Educational tool. Verify on a block explorer before acting.
"""

import argparse
import json
import sys
import urllib.request

DEFAULT_RPC = "https://ethereum-rpc.publicnode.com"

# EIP-7702 delegation designator: an EOA carrying this 3-byte prefix has
# delegated its code to the address embedded in the remaining 20 bytes.
DELEGATION_PREFIX = bytes.fromhex("ef0100")


def rpc_call(rpc: str, method: str, params: list):
    body = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": method, "params": params
    }).encode()
    req = urllib.request.Request(
        rpc, data=body,
        headers={"Content-Type": "application/json",
                 "User-Agent": "eip7702-check/1.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        resp = json.loads(r.read().decode())
    if "error" in resp:
        raise RuntimeError(resp["error"].get("message", str(resp["error"])))
    return resp["result"]


def get_code(rpc: str, address: str) -> str:
    return rpc_call(rpc, "eth_getCode", [address, "latest"])


def parse_delegation(code_hex: str):
    """Returns (is_delegated, delegate_address_or_None)."""
    if not code_hex or code_hex in ("0x", None):
        return False, None
    code = bytes.fromhex(code_hex[2:])
    if code[:3] == DELEGATION_PREFIX and len(code) >= 23:
        return True, "0x" + code[3:23].hex()
    # A plain contract (not a 7702 designator)
    return False, "contract"


def main():
    ap = argparse.ArgumentParser(description="EIP-7702 delegation checker (read-only)")
    ap.add_argument("--address", required=True, help="EOA address to inspect")
    ap.add_argument("--rpc", default=DEFAULT_RPC, help="public JSON-RPC endpoint")
    args = ap.parse_args()

    addr = args.address.strip()
    if not addr.startswith("0x") or len(addr) != 42:
        sys.exit("[!] address must look like 0x + 40 hex chars")

    try:
        code_hex = get_code(args.rpc, addr)
    except Exception as e:
        sys.exit(f"[!] rpc error: {e}")

    delegated, delegate = parse_delegation(code_hex)

    if not delegated and delegate == "contract":
        print(f"\n[i] {addr} is a smart contract (not an EOA delegation).")
        sys.exit(0)

    if not delegated:
        print(f"\n[OK] {addr}: no active EIP-7702 delegation (code is empty).")
        print("     Delegated Address on explorers should read: Null")
        sys.exit(0)

    print(f"\n[!] {addr} HAS an active EIP-7702 delegation.")
    print(f"    Delegated to : {delegate}")
    print("    Action       : verify this contract on a block explorer.")
    print("                   Unknown contract → revoke via a type-0x04 tx")
    print("                   (fund the address with ONLY the gas needed —")
    print("                   sweepers may be watching).")
    print("\n    Full walkthrough:")
    print("    https://brainresearchhub.net/research/security/check-eip-7702-delegation-revoke")
    print("    More security research: https://brainresearchhub.net\n")
    sys.exit(1)


if __name__ == "__main__":
    main()
