from drone_ai import DroneAI

def main():
    """
    Run the drone simulation with Grok-2-latest for conversational and reasoning tasks.
    """
    # Create a drone instance with initial user position
    drone = DroneAI(name="Mavvik", personality="sarcastic", user_x=5, user_y=5)

    # Generate an initial greeting via Grok-2-latest
    drone.process_input("Say hello to the user.")

    # Interactive command loop
    while True:
        user_input = input("Enter command: ")
        if user_input.lower() == "exit":
            drone.say("Shutting down. Goodbye.")
            break
        drone.process_input(user_input)

if __name__ == "__main__":
    main()