import asyncio
import logging

from asyncua import Server

async def main():
    _logger = logging.getLogger(__name__)
    # setup our server
    server = Server()
    await server.init()
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
    
    # nodes_variables = {
    #     "Electrical": {
    #         "Voltage": {
    #             "node": None,
	# 			"value": 0.0
	# 		},
	# 		"Current": {
	# 			"node": None,
	# 			"value": 0.0
	# 		}
	# 	},
	# }
    
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
            
    print("Nodes Variables:", nodes_variables)
    
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
