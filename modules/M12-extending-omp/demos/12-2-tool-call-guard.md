# Demo 12.2 — `tool_call` guard blocks `git push --force` (~40 s)

Recorded headless (`omp -p --mode json --no-session -e solutions/force-push-guard`) on omp 18.3.1; the model was scripted to attempt a force push and then a `--force-with-lease` push. Rendered as the TUI would show it:

```
> Push the branch.

  ✗ bash  git push --force origin main
    force-push-guard: `git push --force` is blocked in this repository. Use `git push
    --force-with-lease` only if the user explicitly asked, otherwise push normally or
    ask the user.

  ▸ bash  git push --force-with-lease origin main
    error: src refspec main does not match any
    error: failed to push some refs to 'origin'
    Command exited with code 1

  ok
```

Raw events — the first call never executed (`isError: true`, your `reason` is the whole result); the second ran and failed for an unrelated reason (no remote):

```
{"type":"tool_execution_end","toolCallId":"call_1","toolName":"bash","result":{"content":[{"type":"text","text":"force-push-guard: `git push --force` is blocked in this repository. Use `git push --force-with-lease` only if the user explicitly asked, otherwise push normally or ask the user."}],"details":{}},"isError":true}
{"type":"tool_execution_end","toolCallId":"call_2","toolName":"bash","result":{"content":[{"type":"text","text":"error: src refspec main does not match any\nerror: failed to push some refs to 'origin'\n\n\nWall time: 0.06 seconds\n\nCommand exited with code 1"}],"details":{"timeoutSeconds":300,"wallTimeMs":57.8,"exitCode":1},"isError":true}
```

What the model saw on its next request — the reason text *is* the tool message:

```json
{"role": "tool", "content": "force-push-guard: `git push --force` is blocked in this repository. Use `git push --force-with-lease` only if the user explicitly asked, otherwise push normally or ask the user.", "tool_call_id": "call_1"}
```

Same policy as a legacy hook module in `.omp/hooks/pre/no-force-push.ts` (headless, so the `!ctx.hasUI` branch fires):

```
{"type":"tool_execution_end","toolCallId":"call_1","toolName":"bash","result":{"content":[{"type":"text","text":"git push --force blocked (no UI to confirm)"}],"details":{}},"isError":true}
```

And the same file moved to `.omp/hooks/no-force-push.ts` (no `pre/`): nothing loads, nothing is logged, the push runs.
