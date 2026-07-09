# Proxy Learner

Python sidecar for [Karing](https://karing.app) that learns which domains are reachable via **direct** connection in Iran, and maintains a `learned-direct` rule-provider so Karing can route them without VPN.

## Phase 1 setup

1. **Karing**
   - TUN mode: off (phase 1)
   - Mixed port: `3067` (Settings → Port → Rule Based)
   - Windows system proxy: point at Karing
   - Merge `config/karing-snippet.yaml` into your Karing routing rules
   - **Control and Sync** port `3057` is the external controller API (Settings → Port)

   `proxy-learner` auto-discovers API URL and secret from:

   `%APPDATA%\karing\karing\service.json`

   **Important:** Add the `learned-direct` rule-provider to Karing routing rules
   (see `config/karing-snippet.yaml`). Until then, rules are written to
   `learned-direct.yaml` but Karing won't apply them.

2. **Install**

   ```bash
   pip install -e ".[dev]"
   ```

3. **Run the learner**

   ```bash
   proxy-learner
   ```

   Or with env overrides:

   ```bash
   set KARING_API_URL=http://127.0.0.1:3057
   set RULES_PATH=learned-direct.yaml
   set SIGHTING_THRESHOLD=3
   proxy-learner
   ```

## How it works

| Step | Behavior |
|------|----------|
| Observe | Polls Karing `GET /connections` for proxied traffic |
| Count | Records sightings per host; probes after threshold (default 3) |
| Promote | TLS probe 2/3 success → adds `DOMAIN-SUFFIX,... ,DIRECT` to `learned-direct.yaml` |
| Reload | `PUT /providers/rules/learned-direct` |
| Revoke | Watches warning logs; on DIRECT failure → re-probe 2/3 fail → remove rule |

Unknown domains keep Karing's default **PROXY** behavior. The learner only grows the DIRECT list.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `KARING_API_URL` | `http://127.0.0.1:3057` (auto from `service.json`) | Clash external controller |
| `KARING_SECRET` | auto from `service.json` | Bearer token |
| `RULES_PATH` | `learned-direct.yaml` | Rule-provider file path |
| `STATE_PATH` | `state.json` | Sighting counts |
| `RULE_PROVIDER_NAME` | `learned-direct` | Provider name in Karing config |
| `SIGHTING_THRESHOLD` | `3` | Sightings before probe |
| `POLL_INTERVAL_SECONDS` | `5` | Connection poll interval |
| `PROBE_ATTEMPTS` | `3` | Probes per decision |
| `PROBE_REQUIRED_SUCCESSES` | `2` | Required matching outcomes |
| `PROBE_TIMEOUT_SECONDS` | `5` | Per-probe timeout |

## Tests

```bash
pytest
```

## Later phases

- **Phase 2**: Custom forward proxy before Karing
- **Phase 3**: TUN mode owned by this service
- **Later**: Import nekoray/nekobox seed lists as a separate rule-provider
