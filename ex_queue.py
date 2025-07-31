import asyncio


async def task_producer(queue: asyncio.Queue):
	count = 0

	while True:
		print("producer send: ", count)
		queue.put_nowait(count)
		count += 1
		print(f'queue: {queue}')
		await asyncio.sleep(2.0)


async def task_consumer(queue: asyncio.Queue[int]):
	while True:
		data = await queue.get()
		print("consumer receive: ", data)


async def main():
	queue = asyncio.Queue()
	asyncio.create_task(task_producer(queue))
	asyncio.create_task(task_consumer(queue))

	await asyncio.Event().wait()


if __name__ == '__main__':
	asyncio.run(main())