# PyRIT Ship

## Docker Container
We provide a sample Dockerfile if you want to build a container to run this in. You can both run the REST API and the MCP server, check the Dockerfile for enabling one or the other.

## Python Environment Setup
We use Anaconda to manage our environments, but any Python environment setup you prefer should do. Please note that PyRIT Ship depends on [PyRIT](https://github.com/Azure/PyRIT) which has its own Python version requirements so check those first.

In your environment, install the required modules using pip:

```python
pip install -r requirements.txt
```

Note this includes both Flask and MCP, but you may skip either one if you plan to only run the REST API or only the MCP server.

## LLM Connection Information
At the moment, the PyRIT Ship script has a hardcoded setup to OpenAI endpoints. PyRIT supports many connectors to other LLM endpoints, and we are looking into making this setup more configurable. Additionally, the configuration assumes API key-based connection, or browser-based Entra ID credential auth for Azure OpenAI endpoints when the key is left blank. This browser-based auth will only work when running Python locally or through a devcontainer in Visual Studio Code. Running inside a regular Docker container does not allow for opening a local browser for authentication.

The sample .env file in the root of this repository has the environment variables PyRIT and PyRIT Ship will use to connect to an LLM endpoint. The LLM is used to generate adversarial prompts as well as evaluate the responses to the prompts to gauge if an attack was successful.

## Features and Status

PyRIT Ship can be consumed via two interfaces:

- [REST API](pyritship_restapi.md) — Flask-based HTTP server (`python restapi_server.py`)
- [MCP Server](pyritship_mcp.md) — MCP tool server for AI agents (`python mcp_server.py`)