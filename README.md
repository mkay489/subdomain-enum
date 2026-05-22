# subenum  Async Subdomain Enumerator

![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/status-active-brightgreen?style=flat-square)

Fast, async subdomain enumeration via DNS brute-force and certificate transparency logs (crt.sh).

```
 ____        _     _____
/ ___| _   _| |__ | ____|_ __  _   _ _ __ ___
\___ \| | | | '_ \|  _| | '_ \| | | | '_ ` _ \
 ___) | |_| | |_) | |___| | | | |_| | | | | | |
|____/ \__,_|_.__/|_____|_| |_|\__,_|_| |_| |_|
```

## Disclaimer

This tool is intended for educational purposes and authorized security testing only.
Only run this against domains you own or have explicit written permission to test.
Unauthorized use may violate laws such as the CFAA, Computer Misuse Act, or GDPR.

## Features

Async DNS brute-force via aiodns, hundreds of queries per second.
crt.sh integration for certificate transparency log lookups.
Custom wordlists or built-in 80-word list.
JSON output for easy post-processing.

## Installation

```bash
git clone https://github.com/yourusername/subenum.git
cd subenum
pip install -r requirements.txt
```

## Usage

```bash
# Basic scan (built-in wordlist + crt.sh)
python subenum.py example.com

# Custom wordlist
python subenum.py example.com -w wordlists/subdomains-top1000.txt

# High concurrency + save results
python subenum.py example.com -c 200 -o results.json

# Skip crt.sh (DNS brute only)
python subenum.py example.com --no-crtsh

# All options
python subenum.py example.com -w wordlist.txt -c 150 -t 5 -o out.json
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| domain | Target domain | required |
| -w / --wordlist | Path to wordlist | built-in |
| -c / --concurrency | Concurrent DNS queries | 100 |
| -t / --timeout | DNS timeout in seconds | 3 |
| -o / --output | JSON output file | none |
| --no-crtsh | Skip crt.sh lookup | false |

## Example Output

```
[*] Target      : example.com
[*] Wordlist    : 1000 words
[*] Concurrency : 100
[*] Started     : 2025-01-15 14:32:01
=======================================================
[*] Querying crt.sh for example.com...
[+] crt.sh returned 23 unique entries

  [CERT]  api.example.com                          93.184.216.34
  [CERT]  dev.example.com                          93.184.216.35

[*] Starting DNS brute force (1000 subdomains)...
  [FOUND] www.example.com                          93.184.216.34
  [FOUND] admin.example.com                        93.184.216.50

=======================================================
[+] Scan complete in 4.83s
[+] Checked     : 1000 (brute force)
[+] Found       : 25 total unique subdomains
=======================================================
```

## Project Structure

```
subenum/
    subenum.py          Main script
    requirements.txt    Dependencies
    wordlists/
        README.md       Where to get wordlists
    README.md
```

## Recommended Wordlists

SecLists DNS: https://github.com/danielmiessler/SecLists/tree/master/Discovery/DNS
Assetnote:    https://wordlists.assetnote.io/

## License

MIT
