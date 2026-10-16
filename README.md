# EIP-7702 Delegation Checker (CLI)

Read-only command-line tool that answers one question: **does this wallet
carry an active EIP-7702 delegation, and to which contract?**

Since Pectra, a phished 7702 authorization lets drainers attach a permanent
sweeper to an EOA — every future deposit can be swept without any further
signature. Checking takes seconds and costs nothing.

**No wallet connection. No keys. No sign-in.** The tool sends a single
read-only `eth_getCode` call to a public RPC endpoint of your choice.

## Why this matters

October 2026 saw a $1.54M delegation-drainer wave tied to a single sweeper
contract. Victims who checked their delegation state early lost nothing;
victims who topped up a delegated address lost the top-up within minutes.

## Usage

```bash
git clone https://github.com/sreyleak-security/eip7702-check.git
cd eip7702-check
python3 eip7702_check.py --address 0xYourAddress

# any chain — point at its public RPC:
python3 eip7702_check.py --address 0xYourAddress --rpc https://polygon-rpc.com
```

Exit codes: `0` clean · `1` delegation found · `2` network error.
Scriptable — drop it into cron to monitor cold wallets.

## Sample output

Clean:

```
[OK] 0xabc...: no active EIP-7702 delegation (code is empty).
     Delegated Address on explorers should read: Null
```

Delegated:

```
[!] 0xabc... HAS an active EIP-7702 delegation.
    Delegated to : 0xdead...
    Action       : verify this contract on a block explorer.
                   Unknown contract → revoke via a type-0x04 tx
                   (fund the address with ONLY the gas needed —
                   sweepers may be watching).
```

## How it works

Under EIP-7702, a delegated EOA carries a 3-byte designator prefix
(`0xef0100`) followed by the delegate contract's 20-byte address in its
code. The tool reads `eth_getCode`, parses the designator, and extracts the
delegate — no explorer scraping, no API keys.

Full walkthrough (including the revoke procedure and the funding-order
trap):
**[Check your wallet for an EIP-7702 delegation — BrainResearchHub](https://brainresearchhub.net/research/security/check-eip-7702-delegation-revoke)**

Related from the same author:
- [Wallet drained? The first 24 hours](https://brainresearchhub.net/research/security/wallet-drained-first-24-hours)
- [EIP-7702 delegation attacks: how wallets get taken](https://brainresearchhub.net/research/security/eip-7702-delegation-attacks-check-wallet)
- [Web version (browser, read-only)](https://brainresearchhub.net/tools/eip-7702-delegation-checker)

## License

MIT — use it, fork it, ship it to your community group chats.

*Educational tool. Verify everything on a block explorer. I will never DM
you or ask for your keys.*
