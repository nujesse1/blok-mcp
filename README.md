# Blok MCP Server

Model Context Protocol (MCP) server for running Blok experiments from Claude Code or Claude Desktop.

## Features

- **Authentication**: Secure authentication via Supabase
- **Experiment Management**: Create, run, and monitor experiments
- **Persona Selection**: Browse and select from available personas
- **ngrok Integration**: Expose local development servers for testing
- **Real-time Results**: Get experiment results as they complete

## Installation

### From Source

```bash
git clone https://github.com/blok-intelligence/blok-mcp.git
cd blok-mcp
pip install -e .
```

### Using pip (when published)

```bash
pip install blok-mcp
```

## Configuration

The server can be configured via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `BLOK_MCP_BLOK_API_URL` | Blok API base URL | `https://app.joinblok.co` |
| `BLOK_MCP_WEB_URL` | Web dashboard URL | Derived from API URL |
| `BLOK_MCP_DEBUG` | Enable debug logging | `false` |

## Usage

### Running Locally

```bash
python -m blok_mcp
```

### Claude Code Setup

Add the MCP server to Claude Code:

```bash
# Option 1: Authenticate via MCP tool
claude mcp add blok-experiments -- python -m blok_mcp

# Option 2: Pre-authenticate with token
ACCESS_TOKEN=$(curl -s -X POST https://app.joinblok.co/api/v1/auth/signin \
  -H 'Content-Type: application/json' \
  -d '{"email":"your@email.com","password":"your-password"}' | jq -r '.access_token')

claude mcp add blok-experiments -- python -m blok_mcp
```

### Claude Desktop Setup

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "blok-experiments": {
      "command": "python",
      "args": ["-m", "blok_mcp"],
      "env": {
        "BLOK_MCP_BLOK_API_URL": "https://app.joinblok.co"
      }
    }
  }
}
```

## Available Tools

### Authentication

- **whoami** - Authenticate with email/password and return user info

### Personas

- **list_personas** - List all available personas for experiments

### Experiment Types

- **list_experiment_types** - List available experiment type templates

### Experiments

- **start_experiment** - Create and run a new experiment with full parameters
- **create_experiment_from_description** - Create experiment from natural language
- **list_experiments** - List past experiments with optional filters
- **get_experiment_results** - Get detailed results for an experiment

### ngrok Tunnels

- **start_ngrok** - Start a tunnel to expose local port
- **get_ngrok_status** - Check status of active tunnels
- **stop_ngrok** - Stop tunnels

## Example Usage

```
# Authenticate
> mcp__blok-experiments__whoami(email="user@example.com", password="...")

# List personas
> mcp__blok-experiments__list_personas()

# Create and run an experiment
> mcp__blok-experiments__create_experiment_from_description(
    test_description="complete the checkout flow",
    url="https://mystore.com",
    persona_ids=["uuid-1", "uuid-2"]
  )

# Check results
> mcp__blok-experiments__get_experiment_results(experiment_id="...")
```

## Development

### Setup

```bash
git clone https://github.com/blok-intelligence/blok-mcp.git
cd blok-mcp
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
ruff check .
ruff format .
```

## Deployment

The server can be deployed to Render using the included `render.yaml`:

1. Connect your GitHub repo to Render
2. Create a new Blueprint deployment
3. Configure environment variables:
   - `BLOK_MCP_BLOK_API_URL=https://app.joinblok.co`
   - `BLOK_MCP_DEBUG=false`

## License

MIT

## Support

- Documentation: https://docs.joinblok.co
- Issues: https://github.com/blok-intelligence/blok-mcp/issues
- Email: support@joinblok.co
