# Demo 12.1 — `/hello` and a `word_count` card (~45 s)

Recorded on omp 18.3.1 with `solutions/hello-extension` in `.omp/extensions/`. The TUI transcript is rendered from the `--mode json` event stream captured during the build (see `BUILD-NOTES.md`); model turns were driven by a scripted provider, so the assistant prose is short.

```
$ omp
  ⓘ hello-extension loaded in /home/user/omp-course-lab

> /hello Ada
  Hello, Ada!                                   (custom message · course.hello.greeting)
  ⓘ Greeted Ada

> Count the words in 'the quick brown fox jumps' using word_count.

  ▸ word_count  Counting three words
      text: "the quick brown fox jumps"
    Counting...
    5
    details: { "count": 5 }

  There are 5 words.
```

What the model received on the next request (from the provider log):

```json
{"role": "tool", "content": "5", "tool_call_id": "call_1"}
```

Same run as raw events (`omp -p --mode json …`):

```
{"type":"tool_execution_start","toolCallId":"call_1","toolName":"word_count","args":{"text":"the quick brown fox jumps"}}
{"type":"tool_execution_update","toolCallId":"call_1","toolName":"word_count","partialResult":{"content":[{"type":"text","text":"Counting..."}]}}
{"type":"tool_execution_end","toolCallId":"call_1","toolName":"word_count","result":{"content":[{"type":"text","text":"5"}],"details":{"count":5}},"isError":false}
```

Failure isolation — a broken sibling module does not stop the good one:

```
$ echo 'export default 42;' > .omp/extensions/broken.ts
$ omp
Failed to load extension /home/user/omp-course-lab/.omp/extensions/broken.ts: Extension does not export a valid factory function: /home/user/omp-course-lab/.omp/extensions/broken.ts
  ⓘ hello-extension loaded in /home/user/omp-course-lab
```
