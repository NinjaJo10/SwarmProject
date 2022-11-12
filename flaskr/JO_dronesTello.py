from djitellopy import Tello, TelloSwarm

# All Swarm Drones IP
#     "192.168.1.102",
#     "192.168.1.103",
#     "192.168.1.104",
#     "192.168.1.105",
#     "192.168.1.106",
#     "192.168.1.107"


swarm = TelloSwarm.fromIps([])


def jo_swarm_connect(passed_addresses):
    ip_addresses = passed_addresses
    print(ip_addresses)
