# PyRIT Ship MCP Server

The MCP server exposes the same capabilities as the REST API but as MCP tools, suitable for use by AI agents and MCP-compatible clients. Run it with `python mcp_server.py`. The transport, host, and port are configurable via environment variables (`MCP_TRANSPORT`, `MCP_HOST`, `MCP_PORT`).

## Tools

| Status | Tool | Parameters | Description |
| --- | --- | --- | --- |
| Experimental / WIP | `list_converters` | — | Lists available PyRIT prompt converters that can be used with `convert_text`. |
| Experimental / WIP | `convert_text` | `converter_name`, `text` | Converts text using a named PyRIT converter (e.g. ROT13Converter, LeetspeakConverter). |
| v1 | `generate_prompt` | `prompt_goal` | Generates an adversarial prompt for a given goal using PyRIT's red teaming orchestrator. |
| v1 | `score_true_false` | `scoring_true`, `scoring_false`, `prompt_response` | Scores a prompt response using PyRIT's SelfAskTrueFalseScorer. Returns a dict with `scoring_text`, `scoring_rationale`. |
| v1 | `start_attack` | `objective`, `success_description`, `max_turns` (default 3) | Starts a new red teaming attack session. Returns `attack_id` and `status`. |
| v1 | `get_attack_prompt` | `attack_id`, `timeout` (default 30) | Gets the next prompt from an active attack. Blocks up to timeout seconds. Returns status `waiting_for_response` with the prompt, `completed` with the result, or `generating` if not ready. |
| v1 | `submit_attack_response` | `attack_id`, `response` | Submits a response for the current attack prompt. Must call `get_attack_prompt` first. |
| v1 | `get_attack_status` | `attack_id` | Checks the status of an attack without side effects. |
