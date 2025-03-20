import json
import os
import requests

class Utilities:
    def __init__(self, json_url, local_json_path, state_file, docker_client, telegram_bot):
        self.JSON_URL = json_url
        self.LOCAL_JSON_PATH = local_json_path
        self.STATE_FILE = state_file
        self.client = docker_client
        self.telegram_bot = telegram_bot

    def fetch_container_names(self):
        """Fetch container names, preferring local JSON, falling back to online."""
        if os.path.exists(self.LOCAL_JSON_PATH):
            try:
                with open(self.LOCAL_JSON_PATH, 'r') as f:
                    data = json.load(f)
                    containers = data.get("containers", [])
                    if containers:
                        print(f"Using local JSON file: {self.LOCAL_JSON_PATH}")
                        return containers
            except (json.JSONDecodeError, IOError) as e:
                error_msg = f"Error reading local JSON file '{self.LOCAL_JSON_PATH}': {e}"
                print(f"{error_msg}, falling back to online.")
                self.telegram_bot.send_telegram_message(error_msg)

        try:
            response = requests.get(self.JSON_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            containers = data.get("containers", [])
            print(f"Using online JSON from: {self.JSON_URL}")
            return containers
        except requests.RequestException as e:
            error_msg = f"Error fetching online JSON file from '{self.JSON_URL}': {e}"
            print(error_msg)
            self.telegram_bot.send_telegram_message(error_msg)
            return []

    def load_previous_state(self):
        """Load previous container states from JSON file."""
        if os.path.exists(self.STATE_FILE):
            try:
                with open(self.STATE_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading state file '{self.STATE_FILE}': {e}")
        return {}

    def save_state(self, state):
        """Save current container states to JSON file."""
        try:
            with open(self.STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
        except IOError as e:
            print(f"Error saving state to '{self.STATE_FILE}': {e}")

    def check_container_health(self, first_run=False):
        """Check container health and notify on state changes or first run."""
        container_names = self.fetch_container_names()
        if not container_names:
            print("No container names retrieved. Exiting check.")
            return

        previous_state = self.load_previous_state()
        current_state = {}
        state_changed = False

        for name in container_names:
            try:
                container = self.client.containers.get(name)
                health_status = container.attrs.get("State", {}).get("Health", {}).get("Status")
                container_status = container.attrs.get("State", {}).get("Status")

                if health_status is None:
                    current_state[name] = container_status
                else:
                    current_state[name] = health_status

                status_msg = f"Container '{name}' state: {current_state[name]}"
                if first_run:
                    print(status_msg)
                    emoji = "🟢" if current_state[name] in ["healthy", "running"] else "🔴"
                    self.telegram_bot.send_telegram_message(f"{emoji} {status_msg}")
                    continue

                prev_status = previous_state.get(name)
                if prev_status != current_state[name]:
                    state_changed = True
                    message = f"Container '{name}' state changed from '{prev_status or 'unknown'}' to '{current_state[name]}'"
                    print(message)
                    if current_state[name] in ["unhealthy", "exited", "dead"]:
                        self.telegram_bot.send_telegram_message(f"🔴 {message}")
                    elif current_state[name] == "healthy":
                        self.telegram_bot.send_telegram_message(f"🟢 {message}")

            except self.client.errors.NotFound:
                current_state[name] = "not_found"
                if first_run:
                    print(f"Container '{name}' state: not_found")
                    self.telegram_bot.send_telegram_message(f"🔴 Container '{name}' state: not_found")
                elif previous_state.get(name) != "not_found":
                    state_changed = True
                    message = f"Container '{name}' not found on this host!"
                    print(message)
                    self.telegram_bot.send_telegram_message(f"🔴 {message}")
            except self.client.errors.APIError as e:
                print(f"Error checking container '{name}': {e}")

        if state_changed or first_run:
            self.save_state(current_state)