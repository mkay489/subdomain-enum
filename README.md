subenum – Async Subdomain Enumerator

Async subdomain enumeration via DNS brute-force and certificate transparency logs.

======================================================================

DESCRIPTION

Fast async subdomain enumeration using:
- DNS brute force
- crt.sh certificate transparency lookups

======================================================================

DISCLAIMER

Educational and authorized security testing only.

Only scan domains you own or have explicit permission to test.

Unauthorized use may violate laws such as:
- CFAA
- Computer Misuse Act
- GDPR

======================================================================

FEATURES

- Async DNS brute-force via aiodns
- Hundreds of queries per second
- crt.sh integration
- Custom wordlists
- Built-in default wordlist
- JSON output support

======================================================================

INSTALLATION

Clone repository:
git clone https://github.com/yourusername/subenum.git

Enter directory:
cd subenum

Install dependencies:
pip install -r requirements.txt

======================================================================

USAGE

Basic scan:
python subenum.py example.com

Custom wordlist:
python subenum.py example.com -w wordlists/subdomains-top1000.txt

High concurrency + save results:
python subenum.py example.com -c 200 -o results.json

Skip crt.sh:
python subenum.py example.com --no-crtsh

All options:
python subenum.py example.com -w wordlist.txt -c 150 -t 5 -o out.json

======================================================================

OPTIONS

domain
Target domain
Required

-w / --wordlist
Path to wordlist
Default: built-in

-c / --concurrency
Concurrent DNS queries
Default: 100

-t / --timeout
DNS timeout in seconds
Default: 3

-o / --output
JSON output file
Default: none

--no-crtsh
Skip crt.sh lookup
Default: false

======================================================================

EXAMPLE OUTPUT

[*] Target      : example.com
[*] Wordlist    : 1000 words
[*] Concurrency : 100
[*] Started     : 2025-01-15 14:32:01

=======================================================

[*] Querying crt.sh for example.com...
[+] crt.sh returned 23 unique entries

[CERT] api.example.com    93.184.216.34
[CERT] dev.example.com    93.184.216.35

[*] Starting DNS brute force (1000 subdomains)...

[FOUND] www.example.com    93.184.216.34
[FOUND] admin.example.com  93.184.216.50

=======================================================

[+] Scan complete in 4.83s
[+] Checked : 1000
[+] Found   : 25 total unique subdomains

=======================================================

PROJECT STRUCTURE

subenum/
│
├── subenum.py
├── requirements.txt
├── README.md
│
└── wordlists/
    └── README.md

======================================================================

RECOMMENDED WORDLISTS

SecLists DNS
https://github.com/danielmiessler/SecLists/tree/master/Discovery/DNS

Assetnote
https://wordlists.assetnote.io/

======================================================================

LICENSE

MIT
