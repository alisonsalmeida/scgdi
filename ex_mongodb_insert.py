import asyncio
import pymongo


async def main():
	client = pymongo.AsyncMongoClient(
		host='0.0.0.0',
		port=27017,
		username='shell-manager-user',
		password='743bce6144f65c117b7673bc6787db01',
	)

	# await client.admin.command({'ping':1})
	# print("MongoDB connection established successfully.")
	
	# posso fazer assim também:
	# await client.scgdi.alunos.insert_one({
	# 	'nome': 'João da Silva',
	# 	'idade': 20,
	# 	'curso': 'Ciência da Computação'
	# })

	db = client['scgdi']
	alunos = db['alunos']

	await alunos.insert_one({
		'nome': 'João da Silva',
		'idade': 20,
		'curso': 'Ciência da Computação'
	})

	await alunos.insert_one({
		'nome': 'Maria Oliveira',
		'idade': 22,
		'curso': 'Engenharia de Software'
	})

	await alunos.insert_one({
		'nome': 'Pedro Santos',
		'idade': 19,
		'curso': 'Ciência da Computação'
	})

	await alunos.insert_one({
		'nome': 'Ana Costa',	
		'idade': 21,
		'curso': 'Engenharia de Produção'
	})

if __name__ == '__main__':
	asyncio.run(main())
