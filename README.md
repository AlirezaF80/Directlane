# Proxy Learner

Python sidecar for [Karing](https://karing.app) that learns which domains are reachable via **direct** connection in Iran, and maintains a Karing diversion JSON file so those domains can skip VPN.

## Phase 1 setup

1. **Karing**
   - TUN mode: off (phase 1)
   - Mixed port: `3067` (Settings → Port → Rule Based)
   - Windows system proxy: point at Karing
   - **Control and Sync** port `3057` is the external controller API (Settings → Port)

   `proxy-learner` auto-discovers API URL and secret from:

   `%APPDATA%\karing\karing\service.json`

2. **Install**

   ```bash
   pip install -e ".[dev]"
   ```

3. **Run the learner**

   ```bash
   proxy-learner
   ```

4. **Import rules into Karing**

   When `learned-direct.json` changes, import it in Karing → Diversion Rules, or merge the `learned-direct` group into your `diversion_rules_custom.json` before the final proxy catch-all.

   See `config/karing-learned-direct.example.json` for the format.

## How it works

| Step | Behavior |
|------|----------|
| Observe | Polls Karing `GET /connections` for proxied traffic |
| Probe | TLS probe 2/3 on first unseen hostname |
| Promote | Adds exact hostname to `learned-direct.json` `domain` list |
| Revoke | Watches warning logs; on DIRECT failure → re-probe 2/3 fail → remove host |

Unknown domains keep Karing's default **PROXY** behavior. The learner only grows the DIRECT list.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `KARING_API_URL` | `http://127.0.0.1:3057` (auto from `service.json`) | Clash external controller |
| `KARING_SECRET` | auto from `service.json` | Bearer token |
| `RULES_PATH` | `learned-direct.json` | Karing diversion import file |
| `KARING_GROUP_NAME` | `learned-direct` | Diversion group name in JSON |
| `STATE_PATH` | `state.json` | Hosts already probed |
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
- **Later**: Import nekoray/nekobox seed lists as a separate diversion group
