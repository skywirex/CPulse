# CPulse

## Monitor Docker Container Health with Telegram Notifications

This guide explains how to build and run a Docker container (`skywirex/cpulse`) that monitors the health of other containers and sends notifications to a Telegram chat when issues are detected.

## Building and Running the Container

### Build the Docker Image
To create the `skywirex/cpulse` image, use the following command:

```bash
docker build -t skywirex/cpulse .
```

### Run the Container
Launch the container in detached mode with the necessary volume mounts:

```bash
docker run -d --name cpulse \
  -v /root/docker/cpulse/.env:/app/.env \
  -v /root/docker/cpulse/containers.json:/app/containers.json \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  skywirex/cpulse
```

#### Explanation of Flags:
- `-d`: Runs the container in the background.
- `--name cpulse`: Names the container `cpulse`.
- `-v /root/docker/cpulse/.env:/app/.env`: Mounts the `.env` file for configuration.
- `-v /root/docker/cpulse/containers.json:/app/containers.json`: Mounts the local `containers.json` file listing containers to monitor.
- `-v /var/run/docker.sock:/var/run/docker.sock:ro`: Provides read-only access to the Docker daemon.

### Stop and Remove the Container
To stop and delete the container when no longer needed:

```bash
docker stop cpulse && docker rm cpulse
```

## Configuring the `.env` File
Create a `.env` file at `/root/docker/cpulse/.env` with the following content:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
JSON_URL=https://example.com/containers.json
LOCAL_JSON_PATH=containers.json
CHECK_INTERVAL=60
```

#### Explanation of Variables:
- `TELEGRAM_BOT_TOKEN`: The token for your Telegram bot (e.g., `123456789:AAF...`), obtained from BotFather.
- `TELEGRAM_CHAT_ID`: The chat ID where notifications will be sent (e.g., `123456789` for a user or `-123456789` for a group).
- `JSON_URL`: URL to an online JSON file with container names (fallback if local file fails).
- `LOCAL_JSON_PATH`: Path to the local JSON file inside the container (set to `containers.json`).
- `CHECK_INTERVAL`: How often (in seconds) to check container health (default: `60`).

## Setting Up a Telegram Bot

### Create a Telegram Bot:
1. Open Telegram and start a chat with `@BotFather`.
2. Send `/newbot`, follow the instructions, and record the bot token (e.g., `123456789:AAF...`).

### Obtain the Chat ID:
1. Add the bot to a group or send it a direct message.
2. Send a test message, then retrieve the chat ID using:

```bash
curl https://api.telegram.org/bot<your_bot_token>/getUpdates
```

3. In the JSON response, find `"chat":{"id":<chat_id>}` (e.g., `123456789` or `-123456789` for groups).
4. Alternatively, use `@GetIDsBot` to get the chat ID easily.

### Test the Bot:
Send a manual test message to verify setup:

```bash
curl -X POST "https://api.telegram.org/bot<your_bot_token>/sendMessage" -d "chat_id=<your_chat_id>&text=Test message"
```

## Notes
- Ensure `/root/docker/cpulse/.env` and `/root/docker/cpulse/containers.json` exist on the host before running the container.
- The Docker socket mount (`/var/run/docker.sock`) allows the container to monitor other containers on the host.
- Adjust paths in the `docker run` command if your `.env` or `containers.json` files are stored elsewhere.

This setup enables continuous monitoring of Docker container health with Telegram notifications for any issues detected.




