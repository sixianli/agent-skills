# Grok models

Read this file only when a batch runs, or is about to run, on a Grok model.
It adds what differs for Grok; the whole procedure stays in
[SKILL.md](../SKILL.md).

Improve this file during the work: when a Grok batch shows something new,
add it to [Known pitfalls](#known-pitfalls) with its date, opencode version
and evidence, and change the procedure when the pitfall shows it was wrong.
Facts measured once can change with a new opencode or xAI release; re-check
them when the version changes.

## Contents

- [Which models are allowed](#which-models-are-allowed)
- [Login and first check](#login-and-first-check)
- [Model facts](#model-facts)
- [Launching](#launching)
- [Usage limits](#usage-limits)
- [Trial batches and comparison](#trial-batches-and-comparison)
- [Known pitfalls](#known-pitfalls)

## Which models are allowed

Use only models of the `xai/` provider, which opencode reaches through the
user's own subscription login. Grok models resold by other providers (for
example `opencode-go/grok-*` or `opencode/grok-*`) are billed to a different
account; the user may forbid them, and a project's instructions say so when
they do. Never fall back to a resold Grok model when `xai/` fails; stop and
report instead.

Enforce this in two places:

1. Launch and resume only through [scripts/grok-launch.sh](../scripts/grok-launch.sh),
   which refuses every model that does not start with `xai/` before anything
   starts.
2. In the project's `.opencode/opencode.json`, add providers the project
   never uses to `disabled_providers`, so their Grok models disappear from
   `opencode models`. A provider whose other models are still needed cannot
   be disabled; rely on the launcher for it. Check the result with
   `opencode models --standalone | grep -i grok` from the project directory.

## Login and first check

The user logs in; Claude never handles the login. In opencode: `/connect`,
search xAI, choose the subscription option ("SuperGrok Subscription" in
opencode 2.0.27), and approve in the browser with the account that holds the
plan. A store-bought plan (for example through the App Store) works when the
same account approves.

Then Claude checks, outside the Bash sandbox:

```bash
opencode auth list            # a line "xAI ... stored"
opencode models | grep '^xai/'
```

and sends one tiny prompt from an empty scratch directory, with standard
input closed (see the stdin pitfall in [SKILL.md](../SKILL.md#known-pitfalls)):

```bash
opencode run --standalone --format json -m xai/<model> "Reply with: ok" < /dev/null
```

An `error` event with HTTP 403 means xAI refused the plan for API use; tell
the user, do not try another provider.

## Model facts

Measured with opencode 2.0.27 on 2026-10-14:

| Model | Variant suffix | Notes |
| --- | --- | --- |
| `xai/grok-build-0.1` | none; `#high`, `#medium`, `#low` fail at once with `provider.no-route` "Variant unavailable" | xAI's coding-agent model; launch it without a suffix |
| `xai/grok-4.7` | `#high` works | newest general model in the list |

Other models listed then: `grok-4.20-0309-reasoning`,
`grok-4.20-0309-non-reasoning`, `grok-4.20-multi-agent-0309`, `grok-4.3`,
`grok-4.5`, `grok-4.6`. Test a variant with one tiny prompt before a batch
uses it.

## Launching

Use [scripts/grok-launch.sh](../scripts/grok-launch.sh) exactly like
`oc-launch.sh`:

```bash
grok-launch.sh new <brief> <run prefix> xai/grok-build-0.1
grok-launch.sh resume <session id> <reply> <next stop file> <run prefix> xai/grok-build-0.1
```

It checks the model and then runs `oc-launch.sh`, so every startup check and
`oc-wait.sh` behave as with any other model. Write the model into the
brief's header line so the stop file and the review name the same model.

## Usage limits

Subscription calls report no cost or token counts in the JSON events (no
`cost` or `tokens` on the events of a successful run in opencode 2.0.27), so
`oc-events.py` shows zero cost. Usage is visible only on the subscription's
own dashboard; plans share a weekly pool across products.

- Record the batch's start and end time in the stop-file review, so the user
  can match it with the dashboard.
- An error that mentions a limit, quota, rate or HTTP 429 means the pool may
  be exhausted: stop the batch between tool calls, keep the session, report
  to the user with the error text, and add the exact text to
  [Known pitfalls](#known-pitfalls). Do not switch provider or model without
  the user's decision.

## Trial batches and comparison

When the user approves a trial of a Grok model, run one normal batch with
the same brief template, review standard and test rules as the current
model. After the final stop file, fill
[templates/grok-trial-record.md](../templates/grok-trial-record.md) in the project's
handoff directory, comparing with the current model's recent batches of
similar size, and report to the user with a recommendation. The user decides
whether the default model changes; record that decision where the project
records model choices.

Measure only what the review saw:

- wall time to the final stop file, and tool calls (`oc-events.py`);
- rework rounds and review findings, by severity;
- claims in stop files that the review found false (check runs, numbers,
  deletions);
- rule breaks (test host, deny-list hits, commit and push rules);
- usage as read from the dashboard, if the user provides it.

## Known pitfalls

- 2026-10-14, opencode 2.0.27: a per-provider `blacklist` in
  `opencode.json` was dropped silently (`opencode debug config` showed the
  provider as `{}`) and the models stayed listed; `disabled_providers`
  worked.
- 2026-10-14: `grok-build-0.1` accepts no variant suffix (see
  [Model facts](#model-facts)).
