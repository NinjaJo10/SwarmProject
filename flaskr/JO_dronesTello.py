from djitellopy import Tello, TelloSwarm

# All Swarm Drones IP
#     "192.168.1.102",
#     "192.168.1.103",
#     "192.168.1.104",
#     "192.168.1.105",
#     "192.168.1.106",
#     "192.168.1.107"


# swarm = TelloSwarm.fromIps([])


def jo_swarm_connect(passed_addresses):
    ip_addresses = passed_addresses
    print("You have passed these IP address:", ip_addresses)
    swarm = TelloSwarm.fromIps(ip_addresses)

    swarm.connect()
    swarm.takeoff()

    swarm.move_left(100)
    swarm.rotate_clockwise(90)
    swarm.move_forward(100)

    swarm.land()
