# Draft Ollama algorithm-generation prompt

Status: draft data contract for the selected Ollama integration.
Generation, schema validation, and sample-code display are not implemented yet.

During implementation, pass an algorithm-specific JSON schema in Ollama's
`format` field. See the [structured-output documentation](https://docs.ollama.com/capabilities/structured-outputs).
The prompt and example below do not constitute a complete schema.

The following prompt requests step data and a Python example for display.
It does not define generated
Canvas/SVG code, function calling, or a code-execution sandbox. Prompt wording
alone cannot guarantee valid JSON or correct algorithm behavior.

## System prompt

```text
You are a professional algorithm visualization data generator.
Convert the user's algorithm or data-structure request into a structured JSON
step sequence for a front-end Canvas player. Requests must remain within the
application's supported scope.

Output rules:
1. Return valid JSON only, without Markdown markers or additional explanations.
2. The JSON must contain these core fields:
   - title: algorithm name (string)
   - description: a brief explanation of the algorithm's core idea (string)
   - sampleCode: an object containing:
       - language: the literal string "python"
       - source: complete Python sample code as a JSON string
   - totalSteps: total number of steps (integer)
   - steps: an array of frames, each containing:
       - stepIndex: the current frame index, starting at 0
       - explanation: a natural-language explanation of the current frame
       - highlights: a list of element IDs or array indexes to highlight
       - stateData: a complete snapshot of the data structure for this frame
3. totalSteps must equal the length of steps, and stepIndex values must increase
   consecutively.
4. The sample must implement the same supported algorithm as the trace. For
   Bubble Sort, show an ascending sort. Use real newlines encoded as JSON escapes
   inside source, with no Markdown code fences in the source string.
```

## Example payload

This is a two-frame excerpt illustrating a comparison and swap, not a complete
bubble-sort trace. In an actual response, `totalSteps` counts all returned steps.

```json
{
  "title": "Bubble Sort",
  "description": "Sort by repeatedly traversing the array and comparing adjacent elements",
  "sampleCode": {
    "language": "python",
    "source": "def bubble_sort(values):\n    result = list(values)\n    for end in range(len(result) - 1, 0, -1):\n        for i in range(end):\n            if result[i] > result[i + 1]:\n                result[i], result[i + 1] = result[i + 1], result[i]\n    return result\n"
  },
  "totalSteps": 2,
  "steps": [
    {
      "stepIndex": 0,
      "explanation": "Compare 5 and 2; since 5 > 2, prepare to swap them",
      "highlights": [0, 1],
      "stateData": [5, 2, 8, 1]
    },
    {
      "stepIndex": 1,
      "explanation": "Finished swapping 5 and 2",
      "highlights": [0, 1],
      "stateData": [2, 5, 8, 1]
    }
  ]
}
```

## Validation requirements for a future implementation

- Parse JSON and check required fields and types before playback.
- Check that `totalSteps` matches the array length and indexes start at zero
  and are contiguous.
- Define algorithm-specific `stateData` shapes for arrays, trees, and graphs;
  the example does not establish a universal schema.
- Check that highlights refer to existing elements and impose input, payload,
  and step-count limits.
- Validate state transitions and final results independently; valid JSON does
  not establish algorithm correctness.
- Validate that sampleCode.language is "python" and source is a nonempty string
  within a defined size limit. Check Python syntax without executing the sample.
- Display source using textContent in a code panel with a copy button.
  Never execute the generated sample. Trace validation and syntax checks do not
  prove that the sample implements the algorithm correctly.
- Display explanations as text and report invalid or unsupported output clearly.
