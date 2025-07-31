import asyncio


async def task_request_sensor():
	while True:
		event = asyncio.Event()
		asyncio.create_task(task_response_sensor(event))

		print('task 1: request sensor')
		await asyncio.sleep(5)
		event.set()

		await asyncio.sleep(2)


async def task_response_sensor(event: asyncio.Event):
	print('task 2: awaiting sensor response')
	await event.wait()
	print('task 2: response sensor')
	event.clear()


async def main():
	asyncio.create_task(task_request_sensor())
	await asyncio.Event().wait()

if __name__ == '__main__':
	asyncio.run(main())
