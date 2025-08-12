from ex_mqtt import MQTTChannel
from datetime import datetime, UTC

import asyncio
import random


async def task_sensor_electrical(channel):
	HP = 50
	KW_RATED = HP * 0.7355          # Conversão HP → kW
	V_RATED = 380                   # Tensão nominal trifásica
	FREQ_RATED = 60                 # Hz
	PF_RATED = 0.88                  # Fator de potência típico
	EFFICIENCY = 0.93               # Eficiência típica
	I_RATED = (KW_RATED * 1000) / (1.732 * V_RATED * PF_RATED)  # Corrente nominal

	# Limites para eventos
	OVERVOLTAGE_LIMIT = V_RATED * 1.1
	UNDERVOLTAGE_LIMIT = V_RATED * 0.9
	OVERCURRENT_LIMIT = I_RATED * 1.2

	# Variáveis para energia acumulada
	energy_kWh = 0
	energy_kvah = 0
	energy_kvarh = 0

	last_time = datetime.now(UTC)

	while True:
		voltages = [random.uniform(V_RATED * 0.97, V_RATED * 1.03) for _ in range(3)]
		currents = [random.uniform(I_RATED * 0.95, I_RATED * 1.05) for _ in range(3)]
		freq = random.uniform(FREQ_RATED - 0.05, FREQ_RATED + 0.05)

		V_avg = sum(voltages) / 3
		I_avg = sum(currents) / 3
		pf = random.uniform(PF_RATED * 0.95, PF_RATED * 1.05)
		S = 1.732 * V_avg * I_avg / 1000   # kVA
		P = S * pf                         # kW
		Q = (S**2 - P**2) ** 0.5            # kVAR

		# Energia acumulada
		now = datetime.now(UTC)
		dt_h = (now - last_time).seconds / 3600

		energy_kWh += P * dt_h
		energy_kvah += V_avg * I_avg * dt_h
		energy_kvarh += Q * dt_h

		last_time = now

		if random.random() < 0.01:  # 1% de chance
			voltages[random.randint(0, 2)] = random.uniform(OVERVOLTAGE_LIMIT, OVERVOLTAGE_LIMIT * 1.05)

		if random.random() < 0.01:
			voltages[random.randint(0, 2)] = random.uniform(UNDERVOLTAGE_LIMIT * 0.95, UNDERVOLTAGE_LIMIT)
		
		if random.random() < 0.01:
			currents[random.randint(0, 2)] = random.uniform(OVERCURRENT_LIMIT, OVERCURRENT_LIMIT * 1.2)

		event = {
			"timestamp": now.isoformat(),
			"voltage": {"a": voltages[0], "b": voltages[1], "c": voltages[2]},
			"current": {"a": currents[0], "b": currents[1], "c": currents[2]},
			"power": {"active": P, "reactive": Q, "apparent": S},
			"energy": {"active": energy_kWh, "reactive": energy_kvarh, "apparent": energy_kvah},
			"powerFactor": pf,
			"frequency": freq
		}

		print(event)
		channel.client.publish('scgdi/motor/electrical', event)
		await asyncio.sleep(5)


async def task_sensor_vibration(channel):
	# Faixas normais de operação
	RADIAL_MIN, RADIAL_MAX = 1.5, 3.0   # mm/s RMS
	AXIAL_MIN, AXIAL_MAX = 1.0, 2.0     # mm/s RMS

	# Faixas em falha
	RADIAL_FAULT = (4.0, 6.0)
	AXIAL_FAULT = (3.5, 5.0)

	FAULT_DURATION = 15   # segundos

	fault_active = False
	fault_start = None

	while True:
		if not fault_active and random.random() < 0.003:  # 0,3% chance por segundo
			fault_active = True
			fault_start = datetime.now(UTC)

		# Se está em falha
		if fault_active:
			vib_radial = random.uniform(*RADIAL_FAULT)
			vib_axial = random.uniform(*AXIAL_FAULT)
			if (datetime.now(UTC) - fault_start).seconds >= FAULT_DURATION:
				fault_active = False
		else:
			vib_radial = random.uniform(RADIAL_MIN, RADIAL_MAX)
			vib_axial = random.uniform(AXIAL_MIN, AXIAL_MAX)

		event = {
			"timestamp": datetime.now(UTC).isoformat(),
			"axial": vib_axial,
			"radial": vib_radial
		}

		print(event)
		channel.client.publish('scgdi/motor/vibration', event)
		await asyncio.sleep(60)

async def task_sensor_environment(channel):
	# Parâmetros de operação normal
	TEMP_AMB_MIN, TEMP_AMB_MAX = 20, 30     # Temperatura ambiente
	HUM_MIN, HUM_MAX = 40, 70               # Umidade (%)
	TEMP_CARC_MIN, TEMP_CARC_MAX = 40, 55   # Carcaça (operação normal)

	# Parâmetros de sobrecarga
	TEMP_CARC_OVERLOAD = 65                 # Temperatura na sobrecarga
	OVERLOAD_DURATION = 20                  # Segundos

	# Controle da simulação
	overload_active = False
	overload_start = None

	while True:
		# Temperatura e umidade ambiente (variação natural)
		temp_amb = random.uniform(TEMP_AMB_MIN, TEMP_AMB_MAX)
		hum = random.uniform(HUM_MIN, HUM_MAX)

		# Verifica início de sobrecarga
		if not overload_active and random.random() < 0.05:  # ~5% de chance por ciclo
			overload_active = True
			overload_start = datetime.now(UTC)

		# Se está em sobrecarga
		if overload_active:
			temp_carc = random.uniform(TEMP_CARC_OVERLOAD, TEMP_CARC_OVERLOAD + 2)
			if (datetime.now(UTC) - overload_start).seconds >= OVERLOAD_DURATION:
				overload_active = False  # Fim da sobrecarga
		else:
			temp_carc = random.uniform(TEMP_CARC_MIN, TEMP_CARC_MAX)

		event = {
			"timestamp": datetime.now(UTC).isoformat(),
			"temperature": temp_amb,
			"humidity": hum,
			"caseTemperature": temp_carc
		}

		print(event)
		channel.client.publish('scgdi/motor/environment', event)
		await asyncio.sleep(5)


async def main():
	channel = MQTTChannel()
	await channel.init()
	
	asyncio.create_task(task_sensor_electrical(channel))
	asyncio.create_task(task_sensor_environment(channel))
	asyncio.create_task(task_sensor_vibration(channel))	

	await asyncio.Event().wait()


if __name__ == '__main__':
	asyncio.run(main())
