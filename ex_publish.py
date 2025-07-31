from ex_mqtt import MQTTChannel
import asyncio


async def main():
	channel = MQTTChannel()
	await channel.init()

	count = 0
	while True:
		channel.client.publish('topico-aleatorio', count)
		count += 1
		
		await asyncio.sleep(1)


if __name__ == '__main__':
	asyncio.run(main())
