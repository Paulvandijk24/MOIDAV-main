# Analysis log

## Stage 1 — question

The student expects the percentage of sad messages to be higher on the fire day
than before and after, and higher after the fire than before it. They also
expect to find multiple other sad days using the same feature.

The notebook points to `message_emotion == "verdrietig"` as the sadness feature,
Amsterdam-local dates as the time unit, and before/on/after-fire phases for the
comparison. A bar plot of percentages with uncertainty bars is the chart family
used by the notebook. The preprocessing implementation should retain the
message-level emotion and date features so daily comparisons remain possible.
