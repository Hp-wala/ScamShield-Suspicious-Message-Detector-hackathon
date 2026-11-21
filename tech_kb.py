# ==========================================================
# JARVIS AI
# TECHNICAL KNOWLEDGE BASE
# Networking + Computer Science Domain Knowledge
# Python 3.12
# ==========================================================
#
# HOW THIS WORKS
# --------------
# Two dictionaries, same pattern as code_kb.py:
#
# 1. NETWORK_KB -> networking protocols / technologies, each
#                  with a structured set of fields:
#                  purpose, architecture, workflow,
#                  packet_structure, header_fields,
#                  advantages, limitations, use_cases,
#                  performance, security, vulnerabilities,
#                  troubleshooting, best_practices, examples.
#
# 2. CS_KB      -> broader computer science domains (data
#                  structures, OS, databases, distributed
#                  systems, design patterns, system design...)
#                  each with: overview, core_concepts,
#                  common_patterns, tradeoffs, best_practices,
#                  examples.
#
# THIS FILE IS INTENTIONALLY INCOMPLETE ON PURPOSE.
# Topics fully filled in below are meant to be real, usable
# reference depth. Everything else from the full target list
# is present as a PLACEHOLDER entry with the same field
# structure but empty/"not yet documented" values, so the
# module is structurally complete and can be expanded one
# topic at a time without ever changing the shape of the data
# or any code that reads it (project_kb.py, brain.py, etc.
# never need to change when you add a new topic here).
#
# TO ADD/FILL A TOPIC: find its key below and fill in the
# fields. No other file needs to change.
# ==========================================================


# ==========================================================
# EMPTY TEMPLATE (copy this to add a brand new topic)
# ==========================================================

_NETWORK_TEMPLATE = {
    "purpose": None,
    "architecture": None,
    "workflow": None,
    "packet_structure": None,
    "header_fields": None,
    "advantages": None,
    "limitations": None,
    "use_cases": None,
    "performance": None,
    "security": None,
    "vulnerabilities": None,
    "troubleshooting": None,
    "best_practices": None,
    "examples": None,
}

_CS_TEMPLATE = {
    "overview": None,
    "core_concepts": None,
    "common_patterns": None,
    "tradeoffs": None,
    "best_practices": None,
    "examples": None,
}


# ==========================================================
# NETWORKING KNOWLEDGE BASE
# ==========================================================

NETWORK_KB = {

    # ------------------------------------------------------
    "osi_model": {
        "purpose": (
            "A conceptual 7-layer framework for how network "
            "communication is organized, so each layer only "
            "needs to know about the layer directly above/below it."
        ),
        "architecture": (
            "1. Physical - raw bits over a medium (cables, radio).\n"
            "2. Data Link - frames, MAC addressing, error detection "
            "on a local link (Ethernet, Wi-Fi).\n"
            "3. Network - logical addressing and routing (IP, ICMP).\n"
            "4. Transport - end-to-end delivery, reliability "
            "(TCP, UDP).\n"
            "5. Session - manages sessions/connections between apps.\n"
            "6. Presentation - data format/encoding, encryption, "
            "compression (TLS often modeled here).\n"
            "7. Application - the protocols apps actually talk "
            "(HTTP, DNS, SMTP)."
        ),
        "workflow": (
            "Data flows down the stack on the sender (each layer "
            "adds its own header - encapsulation), across the "
            "wire at the physical layer, then up the stack on the "
            "receiver (each layer strips its header - decapsulation)."
        ),
        "packet_structure": "Not a single format - it's the layering model other protocols' packets/frames map onto.",
        "header_fields": "N/A at this level; see individual protocols (Ethernet, IP, TCP).",
        "advantages": "Standard vocabulary for discussing networking; clean separation of concerns; easier troubleshooting (isolate which layer is failing).",
        "limitations": "Real-world stacks (TCP/IP) don't map cleanly onto all 7 layers; mostly a teaching/reference model rather than an implementation spec.",
        "use_cases": "Teaching, troubleshooting methodology ('is this a Layer 2 or Layer 3 problem'), vendor documentation.",
        "performance": "N/A - conceptual model, not a runtime component.",
        "security": "Security controls exist at every layer (MAC filtering at L2, firewalls at L3/L4, TLS at L6, auth at L7).",
        "vulnerabilities": "N/A directly, but attacks are often described by the layer they target (e.g. ARP spoofing = L2, SYN flood = L4).",
        "troubleshooting": "Bottom-up approach: check physical link -> L2 connectivity (ARP/MAC) -> L3 (ping, routing) -> L4 (port reachability) -> L7 (application logs).",
        "best_practices": "Use the model as a mental checklist when diagnosing 'why can't A reach B', not as literal code architecture.",
        "examples": "A browser request: HTTP (L7) -> TLS (L6) -> TCP (L4) -> IP (L3) -> Ethernet (L2) -> electrical signal (L1).",
    },

    # ------------------------------------------------------
    "tcp_ip_model": {
        "purpose": "The practical 4-layer model that the real internet is built on (vs. the theoretical OSI 7-layer model).",
        "architecture": (
            "1. Network Access (Link) - combines OSI L1+L2 "
            "(Ethernet, Wi-Fi, ARP).\n"
            "2. Internet - IP, ICMP, routing (maps to OSI L3).\n"
            "3. Transport - TCP, UDP (maps to OSI L4).\n"
            "4. Application - HTTP, DNS, SMTP, SSH etc. "
            "(combines OSI L5-L7)."
        ),
        "workflow": "Same encapsulation/decapsulation idea as OSI, just fewer layers; this is what's actually implemented in OS network stacks.",
        "packet_structure": "See IP, TCP, UDP entries individually.",
        "header_fields": "See IP, TCP, UDP entries individually.",
        "advantages": "Matches real implementations directly; simpler than OSI for practical engineering work.",
        "limitations": "Less granular than OSI for teaching purposes; blurs session/presentation concerns into 'application'.",
        "use_cases": "This is literally how the internet works - used in every networked application, from a browser to a mobile app to a game server.",
        "performance": "Depends entirely on the layer/protocol in question (TCP vs UDP tradeoffs, routing efficiency, etc.).",
        "security": "Security is bolted on per layer - IPsec at Internet layer, TLS at transport/application boundary, application-layer auth.",
        "vulnerabilities": "IP spoofing, TCP SYN floods, DNS cache poisoning - all describable in TCP/IP model terms.",
        "troubleshooting": "Tools map directly to layers: ping/traceroute (Internet layer), netstat/ss (Transport layer), curl/browser devtools (Application layer).",
        "best_practices": "Design apps to fail gracefully at each layer (timeouts, retries, DNS fallback) rather than assuming the network is always reliable.",
        "examples": "A REST API call: your code (Application) -> TCP handshake (Transport) -> IP routing (Internet) -> your NIC and switch (Network Access).",
    },

    # ------------------------------------------------------
    "ip_addressing": {
        "purpose": "Uniquely identify devices on a network so packets can be routed to the correct destination; covers IPv4, IPv6, subnetting, and CIDR.",
        "architecture": (
            "IPv4: 32-bit address, written as 4 octets "
            "(e.g. 192.168.1.10), ~4.3 billion addresses.\n"
            "IPv6: 128-bit address, written as 8 groups of hex "
            "(e.g. 2001:0db8::1), vastly larger address space, "
            "built-in support for autoconfiguration (SLAAC) and "
            "no need for NAT.\n"
            "Subnetting: splitting a network into smaller sub-"
            "networks using a subnet mask (e.g. 255.255.255.0).\n"
            "CIDR: 'Classless Inter-Domain Routing' notation - "
            "e.g. 192.168.1.0/24 means the first 24 bits are the "
            "network portion, remaining 8 bits are host addresses "
            "(256 addresses, 254 usable)."
        ),
        "workflow": "A device is assigned an address (static or via DHCP), the subnet mask/CIDR determines which addresses are 'local' (same subnet, reachable via ARP/switching) vs 'remote' (needs a router/gateway).",
        "packet_structure": "IP header sits at the front of every IP packet, wrapping the transport-layer segment (TCP/UDP).",
        "header_fields": (
            "IPv4 key fields: Version, Header Length, Total Length, "
            "TTL (Time To Live), Protocol (TCP=6, UDP=17), Source "
            "IP, Destination IP, Checksum.\n"
            "IPv6 key fields: Version, Traffic Class, Flow Label, "
            "Payload Length, Next Header, Hop Limit, Source/"
            "Destination Address."
        ),
        "advantages": "IPv4: simple, ubiquitous, well understood. IPv6: huge address space, simpler headers, no NAT required, built-in security extension support.",
        "limitations": "IPv4: address exhaustion (hence NAT), no built-in security. IPv6: slower global adoption, some legacy tooling/ISP support gaps.",
        "use_cases": "Every networked device needs an IP address - servers, laptops, phones, IoT devices, cloud VMs, containers.",
        "performance": "Subnetting well reduces broadcast domain size and improves LAN performance; oversized subnets increase broadcast traffic and ARP overhead.",
        "security": "Private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) aren't routable on the public internet, forming a natural (not sufficient) security boundary.",
        "vulnerabilities": "IP spoofing (forging source address), scanning of predictable address ranges, misconfigured subnets exposing internal hosts.",
        "troubleshooting": "`ipconfig`/`ip addr` to check assigned address, `ping` to test reachability, verify subnet mask/CIDR matches expected network segmentation.",
        "best_practices": "Plan subnet sizes around actual host counts (don't waste address space); use CIDR consistently in documentation; migrate critical services to dual-stack (IPv4+IPv6) where possible.",
        "examples": "192.168.1.0/24 = 254 usable host addresses on one LAN; a /30 subnet (4 addresses, 2 usable) is common for point-to-point router links.",
    },

    # ------------------------------------------------------
    "dns": {
        "purpose": "Translates human-readable domain names (example.com) into IP addresses computers use to route traffic.",
        "architecture": (
            "Hierarchical, distributed database: Root servers -> "
            "TLD servers (.com, .org) -> Authoritative name "
            "servers for the specific domain. Resolvers (often "
            "your ISP's or a public one like 8.8.8.8) cache "
            "results and query on your behalf."
        ),
        "workflow": (
            "1. App asks OS resolver for example.com.\n"
            "2. Resolver checks its cache; if empty, asks a root "
            "server, which points to the .com TLD server.\n"
            "3. TLD server points to example.com's authoritative "
            "server.\n"
            "4. Authoritative server returns the IP (A/AAAA record).\n"
            "5. Resolver caches it and returns it to the app."
        ),
        "packet_structure": "DNS messages are typically single UDP packets (port 53) containing a header plus question/answer/authority/additional sections.",
        "header_fields": "Transaction ID, flags (query/response, recursion desired), question count, answer count, followed by the actual question and resource records.",
        "advantages": "Decouples human-friendly names from IPs that can change; caching makes it fast; hierarchical design scales globally.",
        "limitations": "Cache poisoning risk; propagation delay when records change (TTL-bound); plaintext by default (mitigated by DNSSEC/DoH/DoT).",
        "use_cases": "Every domain name lookup - visiting a website, connecting to an API, sending email (via MX records), CDN routing (via geo-aware DNS).",
        "performance": "Low latency due to caching at multiple levels (browser, OS, resolver); TTL tuning trades off freshness vs. lookup speed.",
        "security": "DNSSEC adds cryptographic signing to prevent record tampering; DoH/DoT (DNS over HTTPS/TLS) encrypt queries to prevent eavesdropping.",
        "vulnerabilities": "Cache poisoning, DNS spoofing, DDoS against resolvers/authoritative servers, DNS tunneling (used for data exfiltration).",
        "troubleshooting": "`nslookup`/`dig`/`Resolve-DnsName` to query records directly; check TTLs; verify authoritative server delegation with `dig NS domain`.",
        "best_practices": "Set sensible TTLs (short during migrations, longer once stable); enable DNSSEC where supported; use reputable/monitored resolvers.",
        "examples": "An A record maps example.com -> 93.184.216.34; an MX record tells mail servers where to deliver mail for a domain.",
    },

    # ------------------------------------------------------
    "http_https": {
        "purpose": "Application-layer protocol for transferring data on the web - the basis of virtually all browser/API traffic.",
        "architecture": (
            "Request/response model over TCP (HTTP/1.1, HTTP/2) "
            "or UDP-based QUIC (HTTP/3). HTTPS = HTTP wrapped in "
            "TLS for encryption, integrity, and server authenticity."
        ),
        "workflow": (
            "Client sends a request (method, path, headers, "
            "optional body) -> server processes it -> server "
            "returns a response (status code, headers, body). "
            "For HTTPS, a TLS handshake happens first to "
            "establish an encrypted channel."
        ),
        "packet_structure": "Text-based (HTTP/1.1) or binary framed (HTTP/2, HTTP/3) messages carried inside TCP segments (or QUIC/UDP for HTTP/3).",
        "header_fields": "Common headers: Host, Content-Type, Content-Length, Authorization, Cache-Control, Set-Cookie, User-Agent.",
        "advantages": "Simple, human-readable (v1.1), universally supported, stateless (easy to scale horizontally), rich ecosystem of tooling.",
        "limitations": "HTTP/1.1 has head-of-line blocking; stateless nature means session/auth state must be managed separately (cookies, tokens).",
        "use_cases": "Web pages, REST APIs, webhooks, file downloads, virtually all client-server web communication.",
        "performance": "HTTP/2 multiplexes multiple requests over one connection (fixes head-of-line blocking at the app layer); HTTP/3/QUIC further reduces latency by avoiding TCP handshake overhead.",
        "security": "HTTPS (TLS) provides encryption, integrity, and server identity verification via certificates; HSTS forces HTTPS-only connections.",
        "vulnerabilities": "Man-in-the-middle attacks on plain HTTP, cross-site scripting (XSS), cross-site request forgery (CSRF), injection attacks via unvalidated input.",
        "troubleshooting": "Browser DevTools Network tab, `curl -v`, checking status codes (4xx = client error, 5xx = server error), verifying TLS cert validity.",
        "best_practices": "Always use HTTPS in production; set proper cache headers; use meaningful status codes; validate/sanitize all input server-side.",
        "examples": "GET /api/users/42 returns a 200 with a JSON body; POST /login submits credentials in the request body over HTTPS.",
    },

    # ------------------------------------------------------
    "tls_ssl": {
        "purpose": "Provides encryption, data integrity, and authentication for data in transit (SSL is the legacy predecessor to TLS, now considered insecure/deprecated).",
        "architecture": (
            "Uses asymmetric cryptography (public/private key "
            "pairs, certificates) to establish a session, then "
            "switches to fast symmetric encryption for the actual "
            "data transfer. Certificates are issued/verified via "
            "a Public Key Infrastructure (PKI) and Certificate "
            "Authorities (CAs)."
        ),
        "workflow": (
            "1. Client Hello (supported ciphers, TLS version).\n"
            "2. Server Hello + certificate (public key).\n"
            "3. Client verifies certificate against trusted CAs.\n"
            "4. Key exchange establishes a shared symmetric session "
            "key (via Diffie-Hellman in modern TLS).\n"
            "5. Both sides switch to encrypted communication using "
            "the session key."
        ),
        "packet_structure": "TLS records wrap application data; each record has a type (handshake, alert, application data), version, and length.",
        "header_fields": "Not header-based like IP/TCP - structured as a record protocol with handshake sub-messages (ClientHello, ServerHello, Certificate, Finished).",
        "advantages": "Strong confidentiality and integrity guarantees; authenticates the server (and optionally the client); widely supported and standardized.",
        "limitations": "Adds handshake latency (mitigated by TLS 1.3's 1-RTT handshake and session resumption); certificate management overhead.",
        "use_cases": "HTTPS, secure email (SMTPS/IMAPS), VPNs, secure API communication, any sensitive data in transit.",
        "performance": "TLS 1.3 significantly reduced handshake round trips vs 1.2; session resumption/0-RTT further reduces reconnect latency.",
        "security": "Core security building block for the internet; must disable weak ciphers/old versions (SSLv3, TLS 1.0/1.1 are deprecated).",
        "vulnerabilities": "Historical: Heartbleed, POODLE, BEAST - mostly tied to outdated versions/implementations; misconfigured/self-signed certs enabling MITM; expired certificates.",
        "troubleshooting": "`openssl s_client -connect host:443` to inspect the handshake/cert chain; browser padlock/cert details; check expiry and CA trust chain.",
        "best_practices": "Use TLS 1.2 minimum (prefer 1.3), automate certificate renewal (e.g. Let's Encrypt/ACME), disable weak cipher suites, enforce HSTS.",
        "examples": "A browser padlock icon indicates a valid TLS certificate chain back to a trusted root CA for that domain.",
    },

    # ------------------------------------------------------
    "tcp": {
        "purpose": "Connection-oriented, reliable transport protocol that guarantees ordered, error-checked delivery of a byte stream.",
        "architecture": "Uses a 3-way handshake to establish a connection, sequence/acknowledgment numbers to track delivery, and windowing for flow control.",
        "workflow": (
            "1. SYN (client) -> SYN-ACK (server) -> ACK (client) "
            "establishes the connection.\n"
            "2. Data is sent in segments, each acknowledged by the "
            "receiver; lost segments are retransmitted.\n"
            "3. Connection closes via a FIN/ACK exchange (or RST "
            "for abrupt termination)."
        ),
        "packet_structure": "TCP segment = header + data payload, carried inside an IP packet.",
        "header_fields": "Source/Destination port, Sequence Number, Acknowledgment Number, Flags (SYN, ACK, FIN, RST), Window Size, Checksum.",
        "advantages": "Reliable, ordered delivery; built-in flow control and congestion control; widely supported by every OS/network device.",
        "limitations": "More overhead than UDP (handshake, acks, retransmission); head-of-line blocking can add latency for real-time use cases.",
        "use_cases": "Web traffic (HTTP), email, file transfer, anything requiring guaranteed delivery and order.",
        "performance": "Congestion control algorithms (Cubic, BBR) adapt sending rate to network conditions; window scaling improves throughput on high-latency links.",
        "security": "TCP itself has no encryption - relies on TLS on top; vulnerable to SYN flood DoS attacks without protections like SYN cookies.",
        "vulnerabilities": "SYN flood attacks, TCP session hijacking, sequence number prediction attacks (mostly mitigated by modern randomization).",
        "troubleshooting": "`netstat`/`ss` to check connection states, Wireshark to inspect handshakes/retransmissions, checking for excessive retransmits indicating packet loss.",
        "best_practices": "Tune keepalive/timeout settings for long-lived connections; use connection pooling in applications to avoid handshake overhead per request.",
        "examples": "Every HTTP/1.1 and HTTP/2 connection runs over TCP; SSH and most database connections use TCP too.",
    },

    # ------------------------------------------------------
    "udp": {
        "purpose": "Connectionless, lightweight transport protocol - sends datagrams with no delivery guarantee, in exchange for lower latency/overhead.",
        "architecture": "No handshake, no sequencing, no retransmission built in - the application layer must handle reliability if it's needed.",
        "workflow": "Sender simply sends a datagram to a destination IP/port; there's no connection setup or acknowledgment.",
        "packet_structure": "UDP datagram = small header + payload, carried inside an IP packet.",
        "header_fields": "Source Port, Destination Port, Length, Checksum (much simpler than TCP's header).",
        "advantages": "Very low latency and overhead; no connection state to maintain; good for broadcast/multicast.",
        "limitations": "No guarantee of delivery, ordering, or duplicate protection - the app must implement any of that itself if needed.",
        "use_cases": "DNS queries, video/voice streaming, online gaming, DHCP, any case where speed matters more than guaranteed delivery.",
        "performance": "Minimal overhead means very low latency, ideal for real-time media where a late packet is worse than a lost one.",
        "security": "No built-in protections - easily spoofed source addresses; often used in DDoS amplification attacks (e.g. DNS/NTP amplification).",
        "vulnerabilities": "UDP flood attacks, amplification attacks exploiting protocols like DNS/NTP that reply with much larger responses.",
        "troubleshooting": "Harder to debug than TCP since there's no connection state; use packet captures (Wireshark) to confirm datagrams are actually arriving.",
        "best_practices": "Only use UDP when the application layer can tolerate loss or implements its own reliability (e.g. QUIC does this on top of UDP for HTTP/3).",
        "examples": "DNS queries (typically UDP port 53), a video call's audio/video stream, HTTP/3 (built on QUIC, which runs over UDP).",
    },

    # ------------------------------------------------------
    "dhcp": {
        "purpose": "Automatically assigns IP addresses (and related config like gateway, DNS servers) to devices joining a network, avoiding manual configuration.",
        "architecture": "Client-server model; a DHCP server manages a pool ('scope') of addresses and leases them out for a defined time period.",
        "workflow": (
            "DORA process: Discover (client broadcasts for a "
            "server) -> Offer (server offers an address) -> "
            "Request (client requests that address) -> Ack "
            "(server confirms the lease)."
        ),
        "packet_structure": "DHCP messages are UDP-based (client port 68, server port 67), built on the BOOTP message format.",
        "header_fields": "Transaction ID, client MAC address, requested/offered IP, lease time, options (subnet mask, gateway, DNS servers).",
        "advantages": "Eliminates manual IP configuration; centralizes address management; simplifies moving devices between networks.",
        "limitations": "Single point of failure if the DHCP server goes down (mitigated with redundant servers/failover); rogue DHCP servers can hijack clients.",
        "use_cases": "Every typical home/office/enterprise LAN - laptops, phones, IoT devices joining Wi-Fi/Ethernet.",
        "performance": "Lease renewal traffic is minimal; short lease times increase server load slightly but allow faster address reclaiming.",
        "security": "Rogue DHCP server attacks can redirect clients to malicious gateways/DNS; DHCP snooping on switches mitigates this.",
        "vulnerabilities": "DHCP starvation (exhausting the address pool with fake requests), rogue server/man-in-the-middle attacks.",
        "troubleshooting": "`ipconfig /release` + `/renew` (Windows) or `dhclient` (Linux) to force a new lease; check DHCP server logs for scope exhaustion.",
        "best_practices": "Reserve static leases (by MAC) for servers/printers; enable DHCP snooping on managed switches in enterprise networks.",
        "examples": "A laptop joining office Wi-Fi automatically receives an IP, gateway, and DNS servers via DHCP within seconds.",
    },

    # ------------------------------------------------------
    "rest_apis": {
        "purpose": "An architectural style for designing networked APIs around stateless, resource-oriented HTTP interactions.",
        "architecture": (
            "Resources are identified by URLs (e.g. /users/42); "
            "standard HTTP methods express actions (GET read, "
            "POST create, PUT/PATCH update, DELETE remove); "
            "responses typically use JSON."
        ),
        "workflow": "Client sends an HTTP request to a resource URL with the appropriate method and optional body -> server processes and returns a status code + response body.",
        "packet_structure": "Standard HTTP/HTTPS request/response - see http_https entry.",
        "header_fields": "Content-Type (usually application/json), Authorization (bearer tokens/API keys), Accept, standard HTTP headers.",
        "advantages": "Simple, stateless (scales easily), leverages existing HTTP infrastructure (caching, load balancers), widely understood.",
        "limitations": "Can lead to over-fetching/under-fetching data (addressed by GraphQL); versioning and consistency across many endpoints requires discipline.",
        "use_cases": "Public/internal web APIs, mobile app backends, microservice-to-microservice communication.",
        "performance": "Stateless design allows easy horizontal scaling; caching via HTTP semantics (ETags, Cache-Control) reduces load.",
        "security": "Authentication (API keys, OAuth2, JWT), rate limiting, input validation, HTTPS-only in production.",
        "vulnerabilities": "Broken authentication/authorization, injection attacks, excessive data exposure, lack of rate limiting enabling abuse.",
        "troubleshooting": "Inspect status codes and response bodies, use tools like Postman/curl, check server logs for the specific request.",
        "best_practices": "Use proper HTTP status codes, version your API (e.g. /v1/), paginate large collections, validate all input server-side.",
        "examples": "GET /api/v1/orders/123 returns order details; POST /api/v1/orders creates a new order from the request body.",
    },

    # ------------------------------------------------------
    # PLACEHOLDERS - same structure, not yet documented.
    # Fill these in one at a time using the template above.
    # ------------------------------------------------------
    "network_architecture": dict(_NETWORK_TEMPLATE),
    "physical_layer": dict(_NETWORK_TEMPLATE),
    "data_link_layer": dict(_NETWORK_TEMPLATE),
    "mac_addressing": dict(_NETWORK_TEMPLATE),
    "ethernet": dict(_NETWORK_TEMPLATE),
    "arp": dict(_NETWORK_TEMPLATE),
    "routing": dict(_NETWORK_TEMPLATE),
    "switching": dict(_NETWORK_TEMPLATE),
    "vlans": dict(_NETWORK_TEMPLATE),
    "nat": dict(_NETWORK_TEMPLATE),
    "icmp": dict(_NETWORK_TEMPLATE),
    "ftp_sftp": dict(_NETWORK_TEMPLATE),
    "smtp_pop3_imap": dict(_NETWORK_TEMPLATE),
    "ssh": dict(_NETWORK_TEMPLATE),
    "telnet": dict(_NETWORK_TEMPLATE),
    "snmp": dict(_NETWORK_TEMPLATE),
    "ntp": dict(_NETWORK_TEMPLATE),
    "websocket": dict(_NETWORK_TEMPLATE),
    "mqtt": dict(_NETWORK_TEMPLATE),
    "grpc": dict(_NETWORK_TEMPLATE),
    "graphql": dict(_NETWORK_TEMPLATE),
    "load_balancing": dict(_NETWORK_TEMPLATE),
    "reverse_proxies": dict(_NETWORK_TEMPLATE),
    "firewalls": dict(_NETWORK_TEMPLATE),
    "vpn": dict(_NETWORK_TEMPLATE),
    "proxy_servers": dict(_NETWORK_TEMPLATE),
    "network_security_principles": dict(_NETWORK_TEMPLATE),
    "certificates_pki": dict(_NETWORK_TEMPLATE),
    "authentication_authorization": dict(_NETWORK_TEMPLATE),
    "network_monitoring": dict(_NETWORK_TEMPLATE),
    "packet_analysis": dict(_NETWORK_TEMPLATE),
    "traffic_analysis": dict(_NETWORK_TEMPLATE),
    "high_availability": dict(_NETWORK_TEMPLATE),
    "distributed_networking": dict(_NETWORK_TEMPLATE),
    "cloud_networking": dict(_NETWORK_TEMPLATE),
    "container_networking": dict(_NETWORK_TEMPLATE),
    "kubernetes_networking": dict(_NETWORK_TEMPLATE),
    "sdn": dict(_NETWORK_TEMPLATE),
    "network_automation": dict(_NETWORK_TEMPLATE),
}


# ==========================================================
# COMPUTER SCIENCE KNOWLEDGE BASE
# ==========================================================

CS_KB = {

    # ------------------------------------------------------
    "data_structures_algorithms": {
        "overview": "The study of how to organize data (structures) and manipulate it efficiently (algorithms), forming the foundation of almost all software performance characteristics.",
        "core_concepts": (
            "Arrays/lists, linked lists, stacks, queues, hash "
            "maps, trees (binary, BST, AVL, B-trees), graphs, "
            "heaps/priority queues. Algorithm techniques: sorting "
            "(quicksort, mergesort), searching (binary search), "
            "recursion, dynamic programming, greedy algorithms, "
            "graph traversal (BFS/DFS), Big-O time/space complexity."
        ),
        "common_patterns": "Two-pointer technique, sliding window, divide-and-conquer, memoization/tabulation for DP, union-find for connectivity problems.",
        "tradeoffs": "Time vs. space complexity tradeoffs are constant (e.g. hash maps trade memory for O(1) average lookup vs. O(log n) for balanced trees); choice of structure should match the dominant operation (frequent inserts vs. frequent lookups vs. ordered iteration).",
        "best_practices": "Choose the simplest structure that meets requirements; measure before optimizing; know the Big-O of your language's built-in collections.",
        "examples": "Using a hash map for O(1) lookups instead of scanning a list; using a priority queue (heap) for Dijkstra's shortest path algorithm.",
    },

    # ------------------------------------------------------
    "operating_systems": {
        "overview": "The software layer that manages hardware resources (CPU, memory, disk, I/O) and provides the environment in which applications run.",
        "core_concepts": (
            "Processes and threads, scheduling algorithms, "
            "virtual memory and paging, file systems, "
            "inter-process communication (pipes, sockets, "
            "shared memory), system calls, deadlocks and "
            "synchronization primitives (mutexes, semaphores)."
        ),
        "common_patterns": "Producer-consumer with bounded buffers, reader-writer locks, thread pools to bound concurrency.",
        "tradeoffs": "Multi-threading vs. multi-processing (shared memory speed vs. isolation/safety); preemptive vs. cooperative scheduling (fairness vs. simplicity).",
        "best_practices": "Avoid shared mutable state across threads without proper locking; prefer higher-level concurrency primitives (queues, async/await) over raw locks where possible.",
        "examples": "A web server using a thread pool to handle concurrent requests; a database using write-ahead logging to survive crashes.",
    },

    # ------------------------------------------------------
    "databases": {
        "overview": "Systems for storing, querying, and managing structured (or semi-structured) data reliably and efficiently.",
        "core_concepts": (
            "Relational (SQL) vs. NoSQL (document, key-value, "
            "column, graph) models; ACID transactions; indexing; "
            "normalization vs. denormalization; query "
            "optimization; replication and sharding for scale."
        ),
        "common_patterns": "Read replicas for scaling reads, sharding for scaling writes, caching layers (Redis) in front of the primary DB, event sourcing/CQRS for complex domains.",
        "tradeoffs": "Consistency vs. availability (CAP theorem) in distributed databases; normalization (data integrity) vs. denormalization (read performance).",
        "best_practices": "Index columns used in WHERE/JOIN clauses; avoid N+1 query patterns; use transactions for multi-step operations that must be atomic.",
        "examples": "PostgreSQL for transactional relational data; MongoDB for flexible document storage; Redis for caching and fast key-value lookups.",
    },

    # ------------------------------------------------------
    "distributed_systems": {
        "overview": "Systems composed of multiple independent machines that must coordinate to appear as a single coherent system, despite network unreliability.",
        "core_concepts": (
            "CAP theorem, consensus algorithms (Raft, Paxos), "
            "eventual vs. strong consistency, distributed "
            "transactions, message queues, leader election, "
            "idempotency, distributed tracing."
        ),
        "common_patterns": "Load balancing across nodes, circuit breakers to prevent cascading failures, retries with exponential backoff, service discovery.",
        "tradeoffs": "Strong consistency adds latency/reduces availability during partitions; eventual consistency improves availability but requires handling stale reads.",
        "best_practices": "Design for failure (assume any node/network call can fail); make operations idempotent; use timeouts and circuit breakers on every remote call.",
        "examples": "A microservices architecture where each service can fail independently without taking down the whole system; Kafka as a distributed message log.",
    },

    # ------------------------------------------------------
    "design_patterns": {
        "overview": "Reusable, named solutions to common software design problems, providing a shared vocabulary for structuring code.",
        "core_concepts": (
            "Creational (Factory, Singleton, Builder), "
            "Structural (Adapter, Decorator, Facade), "
            "Behavioral (Observer, Strategy, Command) patterns."
        ),
        "common_patterns": "Dependency injection for testability, Observer pattern for event-driven systems, Strategy pattern for interchangeable algorithms.",
        "tradeoffs": "Patterns add indirection/abstraction - useful when genuine variability exists, overkill when applied preemptively to simple problems.",
        "best_practices": "Apply patterns to solve an actual recurring problem you have, not because a pattern exists; prefer composition over inheritance.",
        "examples": "A payment system using Strategy pattern to swap between payment providers (Stripe, PayPal) without changing calling code.",
    },

    # ------------------------------------------------------
    "system_design": {
        "overview": "The practice of architecting software systems to meet functional and non-functional requirements (scalability, reliability, latency) at a given scale.",
        "core_concepts": (
            "Load balancing, caching strategies, database "
            "scaling (replication/sharding), message queues, "
            "CDNs, rate limiting, horizontal vs. vertical "
            "scaling, monolith vs. microservices."
        ),
        "common_patterns": "Cache-aside pattern, write-through/write-back caching, API gateway in front of microservices, event-driven architecture with message queues.",
        "tradeoffs": "Microservices (independent scaling/deployment) vs. monolith (simplicity, easier debugging); strong consistency vs. availability at scale.",
        "best_practices": "Start simple (monolith) and split out services only when there's a proven need; design for observability (logging, metrics, tracing) from day one.",
        "examples": "A URL shortener using a hash-based key generator plus a distributed cache; a social feed system using fan-out-on-write for followers.",
    },

    # ------------------------------------------------------
    # PLACEHOLDERS - same structure, not yet documented.
    # ------------------------------------------------------
    "computer_architecture": dict(_CS_TEMPLATE),
    "compilers": dict(_CS_TEMPLATE),
    "programming_languages": dict(_CS_TEMPLATE),
    "concurrency_parallel_computing": dict(_CS_TEMPLATE),
    "software_engineering": dict(_CS_TEMPLATE),
    "api_design": dict(_CS_TEMPLATE),
    "cloud_computing": dict(_CS_TEMPLATE),
    "devops": dict(_CS_TEMPLATE),
    "version_control": dict(_CS_TEMPLATE),
    "testing_methodologies": dict(_CS_TEMPLATE),
    "software_architecture": dict(_CS_TEMPLATE),
    "performance_engineering": dict(_CS_TEMPLATE),
    "secure_coding_practices": dict(_CS_TEMPLATE),
    "code_quality_maintainability": dict(_CS_TEMPLATE),
}


# ==========================================================
# LOOKUP HELPERS
# ==========================================================

def get_network_topic(key):
    """Return the full structured entry for a networking topic, or None."""
    return NETWORK_KB.get(key.strip().lower().replace(" ", "_"))


def get_cs_topic(key):
    """Return the full structured entry for a CS domain topic, or None."""
    return CS_KB.get(key.strip().lower().replace(" ", "_"))


def list_documented_network_topics():
    """Topics that have real content (not just the empty template)."""
    return [k for k, v in NETWORK_KB.items() if v.get("purpose") is not None]


def list_documented_cs_topics():
    """Topics that have real content (not just the empty template)."""
    return [k for k, v in CS_KB.items() if v.get("overview") is not None]


def list_placeholder_topics():
    """All topic keys still waiting to be filled in, across both KBs."""
    empty_network = [k for k, v in NETWORK_KB.items() if v.get("purpose") is None]
    empty_cs = [k for k, v in CS_KB.items() if v.get("overview") is None]
    return {"network": empty_network, "cs": empty_cs}


def topic_field(topic_key, field_name, kb="network"):
    """Get one specific field (e.g. 'security') from one topic."""
    source = NETWORK_KB if kb == "network" else CS_KB
    entry = source.get(topic_key.strip().lower().replace(" ", "_"))

    if entry is None:
        return None

    return entry.get(field_name)