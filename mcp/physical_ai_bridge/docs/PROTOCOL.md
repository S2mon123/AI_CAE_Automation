# physical-ai/4.0 RPC

This is a new protocol following the user's v4-only decision. Do not point the
client at a v0.2 server or the RobotStudio Add-In TCP port.

POST `/rpc`, JSON envelope with exactly:

```json
{"protocol":"physical-ai/4.0","payload_b64":"BASE64_UTF8_JSON","signature":"LOWERCASE_SHA256_HMAC_HEX"}
```

HMAC input is the UTF-8 string `physical-ai/4.0\nrequest\n` followed by the exact
base64 payload string; responses use `response` instead. Signing the encoded bytes
avoids cross-language JSON canonicalization ambiguity and prevents response/request
reflection. Key files hold base64-encoded random bytes (minimum 32 bytes).

Request payload fields: `request_id` and `nonce` (independent 32-character lowercase
hex identifiers), integer Unix `issued_at`, `operation`, object `parameters`.
Clock skew window: ±30 seconds. Bridge keeps each accepted nonce through
`issued_at+30` and rejects replay or a full 4096-entry window rather than evicting
live nonces. The window is in memory and resets when the process restarts; this is
acceptable only for this read-only release, not a future physical command ledger.

Allowed operations are exactly `system.capabilities`, `plc.state`,
`plc.read_bool` (one `alias` parameter: configured start/done). The ADS helper exposes
only port lifecycle, declaration query, reads and state reads. It verifies exact
symbol name, BOOL data type and size, and reads the symbol-table version before
and after a value read. There is no variable-value write, Force or COM activation.

Authenticated responses repeat request ID and nonce, include a fresh `issued_at`,
fixed `target` (`bridge_id`, `ams_net_id`, integer `ads_port`), `ok`, `code`, `result`
and `quality`. The client verifies the signature, time, request binding and target
before returning any result. Device errors are not successful zero readings.

Maximum envelope is 1 MiB; requests require bounded Content-Length. The listener
is bound to an explicit private IPv4 interface, checks an explicit client allowlist,
and never changes network policy. The host has one attempt, no redirects, no proxy
inheritance and a finite timeout. This protocol authenticates but does not encrypt.
Same-account key access is not a security boundary against that account.

The read-only listener serializes ADS work and has no Stop channel. It must not be
used as the future motion execution service. That service needs a separate Stop
path, persistent supervisor/ledger and independent authorization at the write boundary.
