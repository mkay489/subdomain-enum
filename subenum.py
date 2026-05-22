#!/usr/bin/env python3
"""
subenum.py  Asynchronous Subdomain Enumerator
Author: github.com/mkayx
Educational purposes only. Only scan domains you own or have permission to test.
"""

import asyncio
import argparse
import sys
import json
import time
from datetime import datetime
from pathlib import Path

try:
    import aiohttp
    import aiodns
except ImportError:
    print("[!] Missing dependencies. Run: pip install aiohttp aiodns")
    sys.exit(1)

BANNER = r"""
 ____        _     _____
/ ___| _   _| |__ | ____|_ __  _   _ _ __ ___
\___ \| | | | '_ \|  _| | '_ \| | | | '_ ` _ \
 ___) | |_| | |_) | |___| | | | |_| | | | | | |
|____/ \__,_|_.__/|_____|_| |_|\__,_|_| |_| |_|

  Async Subdomain Enumerator v1.0  @yourusername
  For authorized testing only.
"""

DEFAULT_WORDLIST = [
    "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1", "ns2",
    "vpn", "m", "mobile", "api", "dev", "staging", "test", "beta", "admin",
    "portal", "remote", "blog", "shop", "static", "cdn", "media", "img",
    "assets", "help", "support", "docs", "wiki", "git", "jenkins", "jira",
    "confluence", "gitlab", "grafana", "kibana", "monitor", "dashboard",
    "db", "mysql", "postgres", "redis", "elastic", "auth", "sso", "login",
    "app", "apps", "backend", "internal", "intranet", "extranet", "proxy",
    "gateway", "router", "firewall", "vpn2", "vpn1", "remote2", "office",
    "cloud", "web", "web1", "web2", "server", "host", "ns3", "ns4",
    "mx", "mx1", "mx2", "smtp2", "imap", "pop3", "exchange", "autodiscover",
    "corp", "dev2", "stage", "prod", "production", "demo", "sandbox"
]


class SubdomainEnumerator:
    def __init__(self, domain: str, wordlist: list, concurrency: int = 100,
                 timeout: int = 3, output: str = None, use_crtsh: bool = True):
        self.domain = domain
        self.wordlist = wordlist
        self.concurrency = concurrency
        self.timeout = timeout
        self.output = output
        self.use_crtsh = use_crtsh
        self.found = []
        self.semaphore = asyncio.Semaphore(concurrency)
        self.stats = {"checked": 0, "found": 0, "errors": 0}

    async def resolve_subdomain(self, resolver: aiodns.DNSResolver, subdomain: str):
        full = f"{subdomain}.{self.domain}"
        async with self.semaphore:
            try:
                result = await resolver.query(full, "A")
                ips = [r.host for r in result]
                self.stats["found"] += 1
                return {"subdomain": full, "ips": ips, "source": "dns-brute"}
            except aiodns.error.DNSError:
                self.stats["errors"] += 1
                return None
            finally:
                self.stats["checked"] += 1

    async def query_crtsh(self, session: aiohttp.ClientSession) -> list:
        """Query crt.sh certificate transparency logs."""
        url = f"https://crt.sh/?q=%.{self.domain}&output=json"
        found = set()
        try:
            print(f"[*] Querying crt.sh for {self.domain}...")
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    for entry in data:
                        name = entry.get("name_value", "")
                        for sub in name.splitlines():
                            sub = sub.strip().lstrip("*.")
                            if sub.endswith(self.domain) and sub != self.domain:
                                found.add(sub)
            print(f"[+] crt.sh returned {len(found)} unique entries")
        except Exception as e:
            print(f"[!] crt.sh query failed: {e}")
        return list(found)

    async def run(self):
        start = time.time()
        print(BANNER)
        print(f"[*] Target      : {self.domain}")
        print(f"[*] Wordlist    : {len(self.wordlist)} words")
        print(f"[*] Concurrency : {self.concurrency}")
        print(f"[*] Started     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 55)

        resolver = aiodns.DNSResolver()
        connector = aiohttp.TCPConnector(ssl=False)

        async with aiohttp.ClientSession(connector=connector) as session:
            crtsh_found = []
            if self.use_crtsh:
                crtsh_results = await self.query_crtsh(session)
                for sub in crtsh_results:
                    try:
                        result = await resolver.query(sub, "A")
                        ips = [r.host for r in result]
                        entry = {"subdomain": sub, "ips": ips, "source": "crt.sh"}
                        crtsh_found.append(entry)
                        print(f"  [CERT]  {sub:45s} {', '.join(ips)}")
                    except:
                        pass

            print(f"\n[*] Starting DNS brute force ({len(self.wordlist)} subdomains)...")
            tasks = [self.resolve_subdomain(resolver, w) for w in self.wordlist]

            for coro in asyncio.as_completed(tasks):
                result = await coro
                if result:
                    self.found.append(result)
                    ips_str = ", ".join(result["ips"])
                    print(f"  [FOUND] {result['subdomain']:42s} {ips_str}")

        all_results = crtsh_found + self.found
        seen = set()
        unique = []
        for r in all_results:
            if r["subdomain"] not in seen:
                seen.add(r["subdomain"])
                unique.append(r)

        elapsed = time.time() - start
        print("\n" + "=" * 55)
        print(f"[+] Scan complete in {elapsed:.2f}s")
        print(f"[+] Checked     : {self.stats['checked']} (brute force)")
        print(f"[+] Found       : {len(unique)} total unique subdomains")
        print("=" * 55)

        if unique:
            print("\n[*] Results:")
            for r in sorted(unique, key=lambda x: x["subdomain"]):
                print(f"    {r['subdomain']:45s} [{r['source']}]")

        if self.output:
            out = {
                "target": self.domain,
                "timestamp": datetime.now().isoformat(),
                "stats": self.stats,
                "results": unique
            }
            Path(self.output).write_text(json.dumps(out, indent=2))
            print(f"\n[+] Saved to {self.output}")

        return unique


def load_wordlist(path: str) -> list:
    try:
        words = Path(path).read_text().splitlines()
        return [w.strip() for w in words if w.strip() and not w.startswith("#")]
    except FileNotFoundError:
        print(f"[!] Wordlist not found: {path}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Async Subdomain Enumerator",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("domain", help="Target domain (e.g. example.com)")
    parser.add_argument("-w", "--wordlist", help="Path to wordlist file (uses built-in if omitted)")
    parser.add_argument("-c", "--concurrency", type=int, default=100,
                        help="Concurrent DNS queries (default: 100)")
    parser.add_argument("-t", "--timeout", type=int, default=3,
                        help="DNS timeout in seconds (default: 3)")
    parser.add_argument("-o", "--output", help="Save results to JSON file")
    parser.add_argument("--no-crtsh", action="store_true",
                        help="Skip crt.sh certificate transparency lookup")
    args = parser.parse_args()

    wordlist = load_wordlist(args.wordlist) if args.wordlist else DEFAULT_WORDLIST

    enumerator = SubdomainEnumerator(
        domain=args.domain,
        wordlist=wordlist,
        concurrency=args.concurrency,
        timeout=args.timeout,
        output=args.output,
        use_crtsh=not args.no_crtsh
    )

    asyncio.run(enumerator.run())


if __name__ == "__main__":
    main()
