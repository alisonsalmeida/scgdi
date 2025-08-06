from ex_mqtt import MQTTChannel
import asyncio
import random


async def task_sensor_electrical(channel):
	while True:
		voltage = random.uniform(220.0, 240.0)
		current = random.uniform(5.0, 7.0)
		power = voltage * current

		channel.client.publish(
			'scgdi/sensor/electrical', 
			{'Voltage': voltage, 'Current': current, 'Power': power}
		)

		await asyncio.sleep(1)


async def task_sensor_vibration(channel):
	while True:
		accell_x = random.uniform(-0.05, 0.05)
		accell_y = random.uniform(-0.05, 0.05)
		accell_z = random.uniform(-0.05, 0.05)

		channel.client.publish(
			'scgdi/sensor/vibration', 
			{'accell_X': accell_x, 'accell_Y': accell_y, 'accell_Z': accell_z}
		)

		await asyncio.sleep(1)

async def task_sensor_environment(channel):
	while True:
		temperature = random.uniform(22.0, 24.0)
		humidity = random.uniform(41.0, 44.0)

		channel.client.publish(
			'scgdi/sensor/environment', 
			{'temperature': temperature, 'humidity': humidity}
		)

		await asyncio.sleep(1)


async def main():
	channel = MQTTChannel()
	await channel.init()
	asyncio.create_task(task_sensor_electrical(channel))
	# asyncio.create_task(task_sensor_environment(channel))
	# asyncio.create_task(task_sensor_vibration(channel))	

	await asyncio.Event().wait()


if __name__ == '__main__':
	asyncio.run(main())
