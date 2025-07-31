### 📡 Exercício: Coletor MQTT com Fila e Processamento Assíncrono
## Objetivo

Implemente uma classe MQTTSensorClient que:

    Conecta-se a um broker MQTT;

    Assina tópicos relacionados a três sensores:

        sensor/vibracao

        sensor/energia

        sensor/ambiente

    Sempre que uma mensagem for recebida, ela é colocada em uma fila asyncio.Queue;

    Uma corrotina consumidora (consumer) processa os dados da fila, simulando um tratamento dos dados (por exemplo, com asyncio.sleep).

## Corpo das mensagens dos sensores (o que o sensor irá enviar)
  Vibração:
    
  ```json
  {
    "accel_x": float,
    "accel_y": float,
    "accel_z": float,
  }
  ```

  Energia:
    
  ```json
  {
    "voltage": float,
    "current": float,
    "active_power": float,
    "reactive_power": float,
    "apparent_power": float,
  }
  ```

  Ambiente

  ```json
  {
    "temperature": float,
    "humidity": float,
  }
  ```

## Requisitos

    Python 3.7+

    Instalar gmqtt:

```bash
pip install gmqtt
```

# Estrutura esperada

    MQTTSensorClient (classe):

        Conecta-se ao broker

        Assina os três tópicos

        Envia mensagens recebidas para a fila

    async def consumer(queue):

        Processa mensagens da fila (exibe no terminal, simula escrita em banco, etc.)

# Comportamento esperado (saída exemplo)

```bash
[MQTT] Conectado ao broker.
[MQTT] Assinado aos tópicos dos sensores.
[MQTT] Mensagem recebida de sensor/vibracao: {"valor": 3.5}
[CONSUMER] Processando dado: tópico=sensor/vibracao, valor=3.5

[MQTT] Mensagem recebida de sensor/energia: {"valor": 120}
[CONSUMER] Processando dado: tópico=sensor/energia, valor=120

[MQTT] Mensagem recebida de sensor/ambiente: {"temperatura": 22.5, "umidade": 55}
[CONSUMER] Processando dado: tópico=sensor/ambiente, temperatura=22.5, umidade=55

```

# Dicas

    A classe deve usar os métodos on_connect, on_message, e on_disconnect.

    Utilize asyncio.Queue compartilhada entre a classe e a task consumer.

    A mensagem MQTT pode ser convertida de JSON usando json.loads.

# Desafio extra (opcional)

    Simule o envio de dados MQTT usando um publisher externo ou um segundo script Python.

    Adicione timestamps às mensagens recebidas.

    Registre os dados em um arquivo .csv.