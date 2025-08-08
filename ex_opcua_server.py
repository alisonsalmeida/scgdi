from ex_mqtt import MQTTChannel
from ex_opcua_hda import HistoryMongoDB
from asyncua import Server, Client
from asyncua.ua import ObjectIds, VariantType, Variant, LocalizedText
from datetime import datetime

import asyncio
import logging
import json
import random


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


async def task_register_discovery(server: Server, registration_interval=10):
    while True:
        try:
            async with Client("opc.tcp://192.168.0.238:4840") as client:
                await client.register_server(server)

        except Exception as e:
            print(f"Error registering server: {e}")

        finally:
            await asyncio.sleep(registration_interval)


async def main():
    _logger = logging.getLogger(__name__)
    # setup our server
    server = Server()
    server.iserver.history_manager.set_storage(HistoryMongoDB(server))
    
    await server.init()
    mqtt_channel = await mqtt_init()

    server.set_endpoint("opc.tcp://192.168.0.238:4841")
    await server.set_build_info(
        product_uri="http://examples.freeopcua.github.io",
        manufacturer_name="Almeida LTDA",
        product_name="aas-opcua-server",
        software_version="1.0.0",
        build_number="1",
        build_date=datetime.utcnow(),
    )
    await server.set_application_uri("urn:almeida:aas-opcua-server")
    server.name = "Almeida AAS - OPCUA Server"
    server.manufacturer_name = "Almeida LTDA"

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
    
    # etype = await server.create_custom_event_type(
    #     idx,
    #     "MyFirstEvent",
    #     ObjectIds.BaseEventType,
    #     [("MyNumericProperty", VariantType.Float), ("MyStringProperty", VariantType.String)],
    # )
    # myevgen = await server.get_event_generator(etype, sub_condition_monitoring)

    etype = await server.create_custom_event_type(
        idx,
        "ConditionMonitoringEvent",
        ObjectIds.BaseEventType,
        [("Current", VariantType.Float), ("Temperature", VariantType.Float)],
    )

    event_generator = await server.get_event_generator(etype, sub_condition_monitoring)
    # server.iserver.enable_history_event(myobj, period=None)
    await server.iserver.enable_history_event(sub_condition_monitoring, period=None)

    # await server.start()
    mqtt_channel.client.on_message = lambda *args: callback_mqtt_message_handler(nodes_variables, *args)
    asyncio.create_task(task_register_discovery(server, registration_interval=10))

    _logger.info("Starting server!")
    async with server:
        count = 0

        while True:
            if count > 3:
                event_generator.event.Message = LocalizedText("Contador passou de 10!")
                event_generator.event.Severity = random.randint(800, 1000)

                event_generator.event.Current = await nodes_variables["Current"].get_value()
                event_generator.event.Temperature = await nodes_variables["Temperature"].get_value()

                await event_generator.trigger()
                count = 0

            else:
                count += 1

            # await myevgen2.trigger(message="This is MySecondEvent " + str(count))
            await asyncio.sleep(1)
            

if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
