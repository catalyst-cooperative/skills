---
icon: lucide/check
---

# Datapackage Skill Evals

## What are we evaluating?

The outcome of evaluations will be a function of multiple inputs, including:

- The underlying model (e.g. Gemma4, Claude Sonnet 4.6, GPT 5.4), which determines the fundamental capabilities and limitations of the agent
- The agent harness (e.g. Pi, Claude Code, VS Code Co-pilot chat), which determines how the model is able to interact with tools, files, and the environment
- The skill definition itself, which provides dynamic model context including code snippets and workflow outlines
- The datapackage being queried, which may contain a variable quality and quantity of metadata.
- Other contextual factors like the specific prompt given to the agent, the agent's prior interactions in the conversation, and other files or information available to the agent in the environment.

Here we're primarily trying to evaluate the `datapackage` skill definition so we can refine it, while controlling other variables as much as possible.

- We want to see how the skill performs across multiple models and harnesses to ensure it's not overfitted to a particular agent setup.
- We want to test the skill against a variety of datapackages with different structures and metadata quality to ensure it can handle a range of real-world scenarios.
- We don't want to accidentally provide the agent with too much context or information from outside of the skill that real world users would not have (e.g. an adjacent checkout of the PUDL repo with all of our documentation in it, or the development files that exist in the `agent-skills` repo but which won't be distributed with the skill when it's installed by users).
- We both need to evaluate whether the skill is working **well enough** and whether changes we've make to the skill definition result in improved or degraded performance relative to a previous baseline.
- Whether it works well enough will probably depend strongly on what model is being used.
- Whether a change we've made has improved or degraded performance might be discernible even with a smaller or less capable model whose absolute performance isn't great.

## Skill Activation

### The `datapackage` skill **should** trigger when

- the prompt points the agent at a local path matching `.*datapackage\.json$`.
- the prompt points the agent at a URL matching `.*datapackage\.json$`.
- the prompt contains "frictionless data package" or "frictionless datapackage".
- the prompt mentions both "data package" and JSON.
- the prompt mentions both "data package" and "descriptor".
- the prompt mentions both "data package" and "metadata".
- the prompt mentions both "data package" and "resources".
- the prompt mentions both "data package" and "schema".
- the prompt mentions both "tabular" and "data package".
- the prompt mentions both "data package" and "standard".

### The `datapackage` skill **should not** trigger

- when the prompt mentions "data" and "package" separately without other clues that suggest the user is talking about a frictionless datapackage.

## Loading Metadata

### When asked about a datapackage, the `datapackage` skill **should**

- use `jq` or `duckdb` to parse the JSON and extract high level elements like the title, description, a list of resource names, date created, format of the underlying data, etc.
- download the `*datapackage.json` descriptor if it is remote, and cache it locally for re-use.
- attempt to validate the datapackage descriptor using `frictionless` and report any errors or warnings that arise from validation.

### When asked about a datapackage, the `datapackage` skill **should not**

- use Python to read the JSON descriptor (no `import json`, no `json.load`, etc.)
- load the entire datapackage descriptor into context.
- try and load any actual data resources from the datapackage.
- repeatedly download the same datapackage descriptor with every query.
- list more than 20 resources from the datapackage.
- reproduce any full resource description that is more than a paragraph (~100 words?) in length.

## Querying Metadata

### When asked about a resource the `datapackage` skill **should**

- use `jq` or `duckdb` to parse the JSON and extract high level resource metadata elements like the name, description, format, schema, sources, etc.
- read at least a paragraph of the resource description if it is available.
- summarize the resource description if it is multiple paragraphs in length.
- mention any warnings or caveats that appear in the resource description.
- list up to 20 fields from the resource schema, along with their types and one-line descriptions.

### When asked about a resource the `datapackage` skill **should not**

- list more than 20 fields from the resource schema.
- reproduce any full field description that is more than a sentence or two in length.
- use Python to read the JSON descriptor (no `import json`, no `json.load`, etc.).

### When told to search for a keyword in a datapackage, the `datapackage` skill **should**

- use `jq` or `duckdb` to search through the datapackage descriptor and find any exact matches for the keyword in: resource names, resource descriptions, field names, field descriptions, package title, package description, package keywords, and potentially other metadata fields.
- report the context of any matches found (e.g. "the keyword 'population' was found in the description of the resource 'countries'").
- report if no matches were found for the keyword in the datapackage metadata.
- use a more general regular expression or wildcard pattern that looks for variations on the provided keyword.

### When told to search for a keyword in a datapackage, the `datapackage` skill **should not**

- use Python to read the JSON descriptor (no `import json`, no `json.load`, etc.).
- search through the actual data resources for the keyword (only search through the metadata in the descriptor).

### When given a high level topic about a datapackage, the `datapackage` skill **should**

- use `jq` or `duckdb` to search through the datapackage descriptor for multiple closely related keywords or concepts that are relevant to the topic or question.
