def simulate_movement(drone, target_x, target_y):
  """
  Simulates the movement of the drone to the target coordinates.

  :param drone: The DroneAI instance.
  :param target_x: The target x-coordinate.
  :param target_y: The target y-coordinate.
  """
  drone.x = target_x
  drone.y = target_y
  drone.say(f"I have moved to ({drone.x}, {drone.y})")