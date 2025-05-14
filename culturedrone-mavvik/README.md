# CultureDrone

A sarcastic Culture Drone project inspired by Iain M. Banks' Culture series, built with Python and the xAI API. The drone, named Mavvik, can navigate a 2D space, respond to commands, and deliver witty remarks.

## Features
- Responds to commands like "Who are you?", "What are you?", "When are you?", and "How are you?" with sarcastic replies.
- Supports movement commands like "move to X, Y", "go away", "user at X, Y", and "follow me".
- Provides a list of available commands with examples.

## Prerequisites
- Python 3.8 or higher
- An xAI API key (sign up at [xAI](https://x.ai) to get one)

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/CultureDrone.git
   cd CultureDrone

  1.	Install dependencies:
pip install requests python-dotenv

  2.	Create a .env file in the project root and add your xAI API key:
echo "XAI_API_KEY=your-api-key-here" > .env

  3.	Run the project:
python main.py

Usage

  •	Start the program and interact with Mavvik by entering commands.
  •	Example commands:
  •	Who are you? - Learn about Mavvik’s identity and personality.
  •	What are you? - Learn about Mavvik’s role and capabilities.
  •	move to 5, 10 - Move Mavvik to coordinates (5, 10).
  •	user at 3, 7 - Update your position to (3, 7).
  •	follow me - Make Mavvik move to your position.
  •	What commands are available to me? - Get a list of available commands.

Contributing

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request. Here are some areas for improvement:
  •	Fix the “400 Bad Request” error when connecting to the xAI API.
  •	Add more commands (e.g., “where are you?” to get the drone’s current position).
  •	Improve response variety for repeated queries.

License

This project is licensed under the MIT License - see the LICENSE file for details.

  •	Replace your-username with your actual GitHub username, and update the license section if you chose a different license.
  2.	Add Dependencies to a requirements.txt File:
  •	Create a file named requirements.txt in your project folder to list the Python dependencies.
  •	Add the following:
requests
python-dotenv

  •	This ensures that others can easily install the required packages using pip install -r requirements.txt.
  3.	Add a .env.example File:
  •	Create a file named .env.example to show the expected format for the .env file without including your actual API key:
XAI_API_KEY=your-api-key-here

  •	This helps contributors understand how to set up their own .env file.
  4.	Commit and Push the Documentation:
  •	Stage the new files:
git add README.md requirements.txt .env.example

  •	Commit the changes:
git commit -m "Add README, requirements, and .env.example for collaboration"

  •	Push the changes to GitHub:
git push origin main

