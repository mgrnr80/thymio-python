# This file is part of thymiodirect.
# Copyright 2020 ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE,
# Miniature Mobile Robots group, Switzerland
# Author: Yves Piguet
#
# Copyright 2025 Massimo Guarnieri
# Changes: added support for invocation of Thymio native functions
#
# SPDX-License-Identifier: BSD-3-Clause

# Test of the communication with Thymio via serial port

from thymiodirect import Thymio
from thymiodirect.thymio_serial_ports import ThymioSerialPort
from thymiodirect.assembler import Assembler
import sys
import os
import time

if __name__ == "__main__":
    # check arguments
    use_tcp = False
    serial_port = None
    host = None
    tcp_port = None
    if len(sys.argv) == 3:
        # tcp: argv[1] = host, argv[2] = port
        use_tcp = True
        host = sys.argv[1]
        tcp_port = int(sys.argv[2])
    elif len(sys.argv) == 2:
        if sys.argv[1] == "--help":
            print("Usage: {sys.argv[0]} [serial_port | host port]")
            sys.exit(0)
        # serial port: argv[1] = serial port
        serial_port = sys.argv[1]

    # read the assembly code from a file
    with open('runtime.asm', 'r') as f:
        asm = f.read()

    # use thymio_serial_ports for default Thymio serial port
    if not tcp_port and serial_port is None:
        thymio_serial_ports = ThymioSerialPort.get_ports()
        if len(thymio_serial_ports) > 0:
            serial_port = thymio_serial_ports[0].device
            print("Thymio serial ports:")
            for thymio_serial_port in thymio_serial_ports:
                print(" ", thymio_serial_port, thymio_serial_port.device)

    # connect
    try:
        th = Thymio(use_tcp=use_tcp,
                    serial_port=serial_port,
                    host=host, tcp_port=tcp_port,
                    refreshing_coverage={"prox.horizontal", "button.center"},
                    )
        # constructor options: on_connect, on_disconnect, on_comm_error,
        # refreshing_rate, refreshing_coverage, discover_rate, loop
    except Exception as error:
        print(error)
        exit(1)


    def on_comm_error(error):
        # loss of connection: display error and exit
        print(error)
        os._exit(1)  # forced exit despite coroutines


    th.on_comm_error = on_comm_error

    th.connect()

    # wait 2-3 sec until robots are known
    id = th.first_node()
    print(f"id: {id}")
    print(f"variables: {th.variables(id)}")
    print(f"events: {th.events(id)}")
    print(f"native functions: {th.native_functions(id)[0]}")

    # get a variable
    th[id]["prox.horizontal"]

    # set a variable (scalar or array)
    # th[id]["leds.top"] = [0, 0, 32]
    remote_node = th.thymio_proxy.connection.remote_nodes[id]
    a = Assembler(remote_node, asm)
    bc = a.assemble()
    th.thymio_proxy.connection.set_bytecode(id, bc)
    th.thymio_proxy.connection.run(id)

    # set a function called after new variable values have been fetched
    prox_prev = 0
    done = False

    th[id].set_leds_top([0, 0, 32])
    th[id].set_leds_top([32, 0, 0])
    th[id].set_leds_top([0, 32, 0])
    th[id].set_leds_bottom_left([0, 0, 32])
    th[id].set_leds_bottom_left([32, 0, 0])
    th[id].set_leds_bottom_right([0, 0, 32])

    def obs(node_id):
        global prox_prev, done
        prox = (th[node_id]["prox.horizontal"][5] - th[node_id]["prox.horizontal"][2]) // 10
        if prox != prox_prev:
            th[node_id]["motor.left.target"] = prox
            th[node_id]["motor.right.target"] = prox
            print(prox)
            # if prox > 5:
            #    th[id]["leds.top"] = [0, 32, 0]
            # elif prox < -5:
            #    th[id]["leds.top"] = [32, 32, 0]
            # elif abs(prox) < 3:
            #    th[id]["leds.top"] = [0, 0, 32]
            prox_prev = prox
        if th[node_id]["button.center"]:
            print("button.center")
            done = True


    th.set_variable_observer(id, obs)

    while not done:
        time.sleep(0.1)
    th.disconnect()
