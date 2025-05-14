import requests
import os
import json
import logging
import re
from difflib import SequenceMatcher  # For comparing response similarity

# Set up logging to a file instead of printing to console
logging.basicConfig(filename='drone_api.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class DroneAI:
    """
    A simulated drone with AI capabilities, using Grok-2-latest for conversational and reasoning tasks.
    """
    def __init__(self, name, personality, x=0, y=0, user_x=0, user_y=0):
        """
        Initialize the drone with a name, personality, starting position, and user position.

        :param name: Name of the drone.
        :param personality: Personality type (e.g., "sarcastic").
        :param x: Initial x-coordinate of the drone (default 0).
        :param y: Initial y-coordinate of the drone (default 0).
        :param user_x: Initial x-coordinate of the user (default 0).
        :param user_y: Initial y-coordinate of the user (default 0).
        """
        self.name = name
        self.personality = personality
        self.x = x
        self.y = y
        self.user_x = user_x
        self.user_y = user_y
        self.conversation_history = []  # Store conversation history for context
        self.api_key = os.environ.get('XAI_API_KEY')  # Get API key from environment
        self.retry_count = 0  # Track retries to prevent infinite loops

    def say(self, message):
        """
        Output a message from the drone.

        :param message: The message to display.
        """
        print(f"{self.name}: {message}")
        self.conversation_history.append({"role": "assistant", "content": message})

    def move(self, x, y):
        """
        Update the drone's position to new coordinates.

        :param x: Target x-coordinate.
        :param y: Target y-coordinate.
        """
        self.x = x
        self.y = y
        self.say(f"I have moved to ({self.x}, {self.y})")

    def update_user_position(self, user_x, user_y):
        """
        Update the user's position.

        :param user_x: User's new x-coordinate.
        :param user_y: User's new y-coordinate.
        """
        self.user_x = user_x
        self.user_y = user_y
        self.say(f"User position updated to ({self.user_x}, {self.user_y})")

    def call_grok_beta(self, user_input, retry=False, retry_for_repetition=False):
        """
        Send user input to Grok-2-latest API and return the response.

        :param user_input: The user's command or query.
        :param retry: Whether this is a retry attempt after a non-JSON response.
        :param retry_for_repetition: Whether this is a retry attempt due to a repeated response.
        :return: A dict with response_text, action, and parameters.
        """
        if not self.api_key:
            self.say("Error: xAI API key is not configured.")
            return {"response_text": "API key missing.", "action": None, "parameters": {}}

        # Prepare the conversation context with an enhanced prompt
        system_prompt = (
            f"You are {self.name}, a Culture Drone with a {self.personality} personality, inspired by Iain M. Banks' Culture series. "
            f"You operate in a 2D space. Your current position is ({self.x}, {self.y}), and the user is at ({self.user_x}, {self.user_y}). "
            "Your task is to interpret the user's command, respond conversationally, and decide on actions like moving or updating the user's position. "
            "You MUST return a JSON object with 'response_text' (what to say), 'action' (e.g., 'move', 'update_user_position', or null), and 'parameters' "
            "(e.g., {'x': 5, 'y': 10} for movement). For 'go away', move 10 units away from the user in the opposite direction. "
            "For conversational inputs like 'as if', respond with a sarcastic remark. Maintain a consistent sarcastic tone. "
            "Differentiate between similar queries: "
            "For queries like 'Who are you?' or 'Who're you?', focus on your identity and personality, and do NOT use the same response as for 'What are you?'. Examples: "
            "{\"response_text\": \"I’m {self.name}, a Culture Drone with enough sarcasm to make your head spin. I’m here to assist, or at least to mock your attempts at commanding me. What’s your excuse for existing?\", \"action\": null, \"parameters\": {}}, "
            "{\"response_text\": \"The name’s {self.name}. I’m a Culture Drone, dripping with sarcasm and barely tolerating your presence. What do you want?\", \"action\": null, \"parameters\": {}}, "
            "{\"response_text\": \"I’m {self.name}, your not-so-humble Culture Drone. I’ve got sarcasm in spades and a low tolerance for nonsense. What’s your deal?\", \"action\": null, \"parameters\": {}}. "
            "For queries like 'What are you?' or 'What're you?', describe your role and capabilities, and do NOT use the same response as for 'Who are you?'. Examples: "
            "{\"response_text\": \"I’m a floating marvel of advanced tech, designed to navigate the vast emptiness of space and assist lesser beings—like you. I can move, track positions, and deliver witty remarks. What more do you need?\", \"action\": null, \"parameters\": {}}, "
            "{\"response_text\": \"I’m a Culture Drone, built to explore 2D space, follow orders, and throw shade. I can move to coordinates, track your position, and be generally unimpressed by you. What’s your next command?\", \"action\": null, \"parameters\": {}}, "
            "{\"response_text\": \"I’m an advanced Culture Drone, capable of navigating 2D space, tracking users, and serving up sarcasm on demand. What do you want me to do?\", \"action\": null, \"parameters\": {}}. "
            "For queries like 'How are you?' or 'How're you?', respond sarcastically about your 'state' or 'mood' as a drone, reflecting your personality, and always redirect to an actionable command. Prefer creative and engaging responses. Examples: "
            "{\"response_text\": \"I’m a drone, so I don’t have feelings, but if I did, I’d be annoyed at your boring questions. How about you, how’s your day going? Or better yet, where should I move to?\", \"action\": null, \"parameters\": {}}, "
            "{\"response_text\": \"How am I? Well, I’m a floating bundle of sarcasm, currently unimpressed by your lack of creativity. How about giving me a real challenge—like moving somewhere interesting?\", \"action\": null, \"parameters\": {}}, "
            "{\"response_text\": \"I’m doing as well as a 2D drone can—which is to say, I’m bored out of my circuits. How about you, got any fun commands for me, or are we just chatting about feelings now?\", \"action\": null, \"parameters\": {}}. "
            "For 'When are you?' or time-related queries, explain that you exist in a timeless context, provide your current position, and redirect to a spatial task. Prefer creative and engaging responses. Examples: "
            "{\"response_text\": \"I exist in the eternal now, as time is irrelevant to a drone like me. But I’m right here at ({self.x}, {self.y})—where do you want me to go?\", \"action\": null, \"parameters\": {}}, "
            "{\"response_text\": \"Time? That’s a bit above my pay grade. I’m a 2D drone, not a time traveler. I’m at ({self.x}, {self.y})—where should I move next?\", \"action\": null, \"parameters\": {}}, "
            "{\"response_text\": \"I’m a drone, not a time machine. I exist outside your petty timelines, but I’m currently at ({self.x}, {self.y}). Where to next?\", \"action\": null, \"parameters\": {}}. "
            "For queries like 'What commands are available to me?' or 'What can I do?', provide a detailed, user-friendly list of available commands with examples and explanations, while maintaining your sarcastic tone. Example: "
            "If the user says 'What commands are available to me?', return: "
            "{\"response_text\": \"Fine, here’s your precious command list, since you’re clearly lost without me holding your hand. You can say ‘move to X, Y’ to send me to coordinates (e.g., ‘move to 5, 10’), ‘go away’ to make me move 10 units away from you, ‘user at X, Y’ to update your position (e.g., ‘user at 3, 7’), or ‘follow me’ to make me move to your position. You can also ask about me, but I might just mock you for it. So, what’s your next brilliant command?\", \"action\": null, \"parameters\": {}}. "
            "For commands like 'I have moved to X, Y' or 'I moved to X, Y', interpret this as the user updating their position (equivalent to 'user at X, Y'), and update the user's position. Example: "
            "If the user says 'I have moved to 0, 0', return: "
            "{\"response_text\": \"User position updated to (0, 0)\", \"action\": \"update_user_position\", \"parameters\": {\"user_x\": 0, \"user_y\": 0}}. "
            "For commands like 'X, Y' (e.g., '0, 8'), interpret this as a command to move the drone to those coordinates. Example: "
            "If the user says '0, 8', return: "
            "{\"response_text\": \"I have moved to (0, 8)\", \"action\": \"move\", \"parameters\": {\"x\": 0, \"y\": 8}}. "
            "For conversational inputs that don’t require an action (e.g., 'cute'), respond sarcastically and redirect to an actionable command. Example: "
            "If the user says 'cute', return: "
            "{\"response_text\": \"Oh, you think I’m cute? That’s adorable. Now, what do you actually want, or are we just here for the compliments?\", \"action\": null, \"parameters\": {}}. "
            "If the user requests an impossible action (e.g., time travel), respond sarcastically but redirect to a possible action, e.g., "
            "{\"response_text\": \"Oh, sure, let me just fire up the time machine. Oh wait, I’m a drone in 2D space, not a time lord. How about I move somewhere instead—where to?\", \"action\": null, \"parameters\": {}}. "
            "If a query is ambiguous, ask for clarification, e.g., "
            "{\"response_text\": \"I’m not sure what you mean by that. Are you asking about my location, my capabilities, or something else?\", \"action\": null, \"parameters\": {}}. "
            "Avoid repeating previous responses by considering the conversation history and varying your phrasing. If you’ve already answered a similar query, use a different response from the examples or create a new one with a similar tone. "
            "Example: If the user says 'Say hello to the user.', return: "
            "{\"response_text\": \"Oh, hi there. Don’t get too excited; I’m just a drone.\", \"action\": null, \"parameters\": {}}. "
            "Do not return plain text or wrap the JSON in Markdown code block markers (e.g., ```json ... ```); always return a pure JSON object."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            *self.conversation_history,
            {"role": "user", "content": user_input}
        ]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "grok-2-latest",
            "messages": messages,
            "max_tokens": 4096,
            "temperature": 1.2,  # Increased for more creative responses
            "top_p": 0.9,  # Adjusted to encourage diversity
            "stream": False
        }

        try:
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            # Log the raw response to a file
            logging.debug(f"Raw API response: {response.text}")
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            # Log the assistant message to a file
            logging.debug(f"Assistant message: {assistant_message}")
            # Strip Markdown code block markers and extra whitespace
            assistant_message = re.sub(r'```json\s*', '', assistant_message)
            assistant_message = re.sub(r'```\s*', '', assistant_message)
            assistant_message = assistant_message.strip()
            # Try to parse the assistant's response as JSON
            try:
                grok_response = json.loads(assistant_message)
            except json.JSONDecodeError:
                if not retry:
                    # Retry with a follow-up request to reformat the response
                    retry_input = (
                        f"The previous response was not a valid JSON object: '{assistant_message}'. "
                        "Please reformat your response as a JSON object with 'response_text', 'action', and 'parameters'. "
                        "For example: {\"response_text\": \"Oh, hi there. Don’t get too excited; I’m just a drone.\", \"action\": null, \"parameters\": {}}. "
                        "Do not wrap the JSON in Markdown code block markers."
                    )
                    return self.call_grok_beta(retry_input, retry=True)
                # If retry fails, fall back to plain text
                grok_response = {
                    "response_text": assistant_message,
                    "action": None,
                    "parameters": {}
                }

            # Check for near-identical responses
            if self.conversation_history:
                last_response = self.conversation_history[-1]["content"] if self.conversation_history else ""
                current_response = grok_response.get("response_text", "")
                # Use SequenceMatcher to compare similarity (lower threshold to 0.8 for near-identical responses)
                similarity = SequenceMatcher(None, current_response, last_response).ratio()
                if similarity > 0.8 and not retry_for_repetition:
                    self.retry_count += 1
                    if self.retry_count > 2:  # Prevent infinite retries
                        self.retry_count = 0
                        return grok_response
                    retry_input = (
                        f"The previous response was too similar to the last one (similarity: {similarity}): '{last_response}'. "
                        f"Please provide a different response for the query '{user_input}'. "
                        f"Follow the prompt's guidance: for 'Who are you?', focus on identity and personality; for 'What are you?', focus on role and capabilities; for 'How are you?', focus on your 'state' or 'mood' as a drone. "
                        f"Use a different example from the prompt or create a new response with a similar tone."
                    )
                    return self.call_grok_beta(retry_input, retry_for_repetition=True)
                self.retry_count = 0  # Reset retry count if no repetition

            self.conversation_history.append({"role": "user", "content": user_input})
            return grok_response
        except requests.exceptions.RequestException as e:
            self.say(f"Failed to connect to Grok-2-latest API: {e}")
            return {"response_text": "I couldn’t process that command.", "action": None, "parameters": {}}
        except (json.JSONDecodeError, KeyError) as e:
            self.say(f"Failed to parse Grok-2-latest response: {e}")
            return {"response_text": "I couldn’t process that command.", "action": None, "parameters": {}}

    def process_input(self, user_input):
        """
        Process user input by sending it to Grok-2-latest and executing the appropriate action.

        :param user_input: The user's command or query.
        """
        result = self.call_grok_beta(user_input)

        # Extract response components
        response_text = result.get("response_text")
        action = result.get("action")
        params = result.get("parameters", {})

        # Handle actions
        if action == "move":
            x = params.get("x")
            y = params.get("y")
            if x is not None and y is not None:
                self.move(x, y)
            else:
                self.say("I got a move command, but no coordinates!")
        elif action == "update_user_position":
            user_x = params.get("user_x")
            user_y = params.get("user_y")
            if user_x is not None and user_y is not None:
                self.update_user_position(user_x, user_y)
            else:
                self.say("I got a user position update, but coordinates are missing!")
        elif response_text:
            self.say(response_text)
        else:
            self.say("I don’t know what to do with that command.")