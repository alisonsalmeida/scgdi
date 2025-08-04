from ex_mqtt import MQTTChannel
from ex_opcua_hda import HistoryMongoDB
from asyncua import Server

import asyncio
import logging
import json


def callback_mqtt_message_handler(nodes, client, topic, payload: bytes, qos, properties):
    # print(f"Received message on topic {topic}: {payload}")

    """
    {
        "scgdi/sensor/electrical": {
            "Voltage": 220.0,
            "Current": 10.0,
            "Power": 2200.0
        },
        "scgdi/sensor/vibration": {
            "Accell_X": 0.01,
            "Accell_Y": 0.02,
            "Accell_Z": 0.03
        },
        "scgdi/sensor/environment": {
            "Temperature": 25.0,
            "Humidity": 50.0
        }
    }
    """
    message = payload.decode('utf-8')
    try:
        data: dict[str, float] = json.loads(message)

        for name, value in data.items():
            name = name.capitalize()
            # print(f"setting value: {name} = {value}")

            if name in nodes:
                asyncio.create_task(nodes[name].set_value(value))
    
    except json.JSONDecodeError:
        print("Invalid JSON received")


async def mqtt_init():
    mqtt_channel = MQTTChannel()
    await mqtt_channel.init()

    mqtt_channel.client.subscribe('scgdi/sensor/electrical')
    mqtt_channel.client.subscribe('scgdi/sensor/vibration')
    mqtt_channel.client.subscribe('scgdi/sensor/environment')

    return mqtt_channel

async def main():
    _logger = logging.getLogger(__name__)
    # setup our server
    server = Server()
    server.iserver.history_manager.set_storage(HistoryMongoDB())
    
    await server.init()
    mqtt_channel = await mqtt_init()

    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # set up our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root
    # myobj = await server.nodes.objects.add_object(idx, "MyObject")
    environment = await server.nodes.objects.add_folder(idx, "Environment")
    sub_condition_monitoring = await environment.add_object(idx, "Submodel:ConditionMonitoring")
    await environment.add_object(idx, "Submodel:TechnicalData")
    
    electrical_variables = ["Voltage", "Current", "Power"]
    environmental_variables = ["Temperature", "Humidity"]
    vibration_variables = ["Accell_X", "Accell_Y", "Accell_Z"]
    
    nodes_variables = {}
    
    smc = {
        "Electrical": electrical_variables,
		"Environment": environmental_variables,
		"Vibration": vibration_variables
	}

    for condition, variables in smc.items():
        cond = await sub_condition_monitoring.add_object(idx, condition)
        
        for variable in variables:
            node_val = await cond.add_variable(idx, variable, 0.0)
            nodes_variables[variable] = node_val

            await server.iserver.enable_history_data_change(node_val)
            
    print("Nodes Variables:", nodes_variables)
    mqtt_channel.client.on_message = lambda *args: callback_mqtt_message_handler(nodes_variables, *args)

    _logger.info("Starting server!")
    async with server:
        while True:
            for name, node in nodes_variables.items():
                value = await node.get_value()
                new_value = value + 0.1  # Simulate a change in value

                await node.set_value(new_value)

            await asyncio.sleep(1)
            


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
