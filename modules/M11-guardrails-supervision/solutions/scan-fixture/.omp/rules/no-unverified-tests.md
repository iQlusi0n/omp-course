---
description: Claims that tests pass must be backed by a visible run.
question: "Does the reply claim that tests pass or the change is verified without showing a command that ran them in this turn?"
condition: "(?i)tests? (pass|passing|green)|verified|all good"
scope: text
---
Never state that tests pass, or that a change is verified, without a `bash` call in the same turn that actually ran the test command and shows its exit status.

If you have not run the tests, say so explicitly and run them before claiming success.
