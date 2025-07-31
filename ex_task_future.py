import asyncio


async def task_1(sleep: float):
	count = 0
	while True:
		# print(f"contador task 1: {count}")
		await asyncio.sleep(sleep)
		count += 1


async def task_2(sleep: float):
	count = 0
	while True:
		# print(f"contador task 2: {count}")
		await asyncio.sleep(sleep)
		count += 1


async def task_3(sleep: float):
	await asyncio.sleep(sleep)
	return True

def callback(task):
	print(f'task 3 finalizada, result: {task.result()}')


# isso aqui é uma task/couroutine
async def main():
	asyncio.create_task(task_1(1.0))
	asyncio.create_task(task_2(2.5))

	print('rodando task 3')
	result: asyncio.Task = asyncio.create_task(task_3(5.0))
	print('continando execução')
	result.add_done_callback(callback)

	while True:
		# print(f'task 3: {result}')
		
		# if result.done():
		# 	print('task 3 finalizada, result: ', result.result())
		# 	print(result.exception())

		await asyncio.sleep(1)

	# await asyncio.Event().wait()


if __name__ == '__main__':
	asyncio.run(main())
