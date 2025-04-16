# Command Line Interface

The CLI provides an easy way to interact with the AI Agent directly from your terminal.

## Features

- **Interactive Chat**: Have multi-turn conversations with the agent
- **Memory**: Maintains conversation context across messages
- **Rich Formatting**: Displays responses with Markdown support
- **Single Query Mode**: Run one-off queries without entering interactive mode
- **Session Management**: Continue previous conversations with session IDs

## Installation

Make sure you have installed the required dependencies:

```bash
pip install -r requirements.txt
```

The CLI requires the `rich` package for pretty formatting.

## Usage

### Starting the Agent

Before using the CLI, make sure the agent is running:

```bash
python src/main.py
```

### Interactive Mode

For a full conversation experience, use interactive mode:

```bash
python cli.py
```

This will:
1. Generate a new session ID
2. Start an interactive chat session
3. Maintain conversation context throughout the session

You can exit the interactive mode by typing `exit`, `quit`, or `q`.

### Single Query Mode

For quick, one-off questions:

```bash
python cli.py --query "What's the weather in New York?"
```

This will:
1. Generate a new session ID
2. Send the query to the agent
3. Display the response
4. Exit

### Continuing a Session

To continue a previous conversation, use the `--session` flag:

```bash
python cli.py --session "cli-session-12345"
```

This is useful when you want to:
- Continue a conversation after closing the terminal
- Split a conversation across multiple CLI invocations
- Reference the same conversation context in different sessions

You can also combine this with single query mode:

```bash
python cli.py --session "cli-session-12345" --query "Tell me more about that"
```

## Advanced Usage

### Custom User IDs

By default, the CLI uses "cli-user" as the user ID. You can modify the script to use custom user IDs if needed.

### Error Handling

The CLI includes robust error handling for:
- Agent API not running
- Connection errors
- Authentication issues
- Missing environment variables

## Implementation Details

The CLI works by:

1. Sending queries to the agent API
2. Directly querying the Supabase database to get the latest response
3. Formatting and displaying the response with rich text formatting

## Troubleshooting

If you encounter issues:

1. Make sure the agent is running (`python src/main.py`)
2. Check that your `.env` file has the correct credentials:
   - `API_BEARER_TOKEN`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
3. Verify network connectivity to both the agent API and Supabase 