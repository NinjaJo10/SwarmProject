from flask import flash

import djitellopy
from djitellopy import Tello, TelloSwarm, TelloException


# All Swarm Drones IP
#     "192.168.1.102",
#     "192.168.1.103",
#     "192.168.1.104",
#     "192.168.1.105",
#     "192.168.1.106",
#     "192.168.1.107"
#       Test for drone server is: 127.0.0.1 Port: 8889


# swarm = TelloSwarm.fromIps([])


def jo_swarm_connect(passed_addresses):
    ip_addresses = passed_addresses
    connected = False
    print("You have passed these IP address:", ip_addresses)

    try:
        swarm = TelloSwarm.fromIps(ip_addresses)

        swarm.connect()
        connected = True
    except djitellopy.TelloException():
        flash("Whoops no ips provided, please try connecting with a different swarm")
    finally:
        return connected


def jo_swarm_takeoff(passed_addresses):
    ip_addresses = passed_addresses
    print("You have passed these IP address to Takeoff:", ip_addresses)
    swarm = TelloSwarm.fromIps(ip_addresses)
    swarm.takeoff()


def jo_swarm_land(passed_addresses):
    ip_addresses = passed_addresses
    print("You have passed these IP address to Land:", ip_addresses)
    swarm = TelloSwarm.fromIps(ip_addresses)
    swarm.land()


def jo_swarm_routine_simple(passed_addresses):
    ip_addresses = passed_addresses
    print("You have passed these IP address to Routine Simple:", ip_addresses)
    swarm = TelloSwarm.fromIps(ip_addresses)

    swarm.takeoff()

    swarm.move_left(100)
    swarm.rotate_clockwise(90)
    swarm.move_forward(100)

    swarm.land()
