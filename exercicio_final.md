# 🧠 Exercício Final SCGDI OPC UA: Monitoramento de Motor Trifásico
## 🎯 Objetivo

### Desenvolver um servidor OPC UA com suporte a:

  * Discovery (Local e Global)
  * Alarmes e Eventos
  * Histórico de Variáveis
  * Histórico de Eventos
  * Nodeset personalizado
  * Integração com MQTT


## 🛠️ Cenário

### Uma indústria precisa monitorar um motor trifásico de 50cv. Três sensores são responsáveis por coletar dados e enviá-los periodicamente:

## 📡 Sensores e Frequência de Envio

| Categoria   | Sensor             | Variáveis                                                                                      | Frequência |
| ----------- | ------------------ | ---------------------------------------------------------------------------------------------- | ---------- |
| Electrical  | Sensor Elétrico    | Tensão (3 fases), Corrente (3 fases), Potência (3), Energia (3), Fator de Potência, Frequência | A cada 1s  |
| Environment | Sensor Ambiental   | Temperatura, Umidade, Temperatura da Carcaça                                                   | A cada 5s  |
| Vibration   | Sensor de Vibração | Vibração Axial, Vibração Radial                                                                | A cada 2s  |

## 📂 Organização dos Nodeset OPC UA

### A estrutura de nós no servidor deve seguir o seguinte modelo:

```markdown
Motor50CV
├── Electrical
│   ├── VoltageA
│   ├── VoltageB
│   ├── VoltageC
│   ├── CurrentA
│   ├── CurrentB
│   ├── CurrentC
│   ├── PowerActive
│   ├── PowerReactive
│   ├── PowerApparent
│   ├── EnergyActive
│   ├── EnergyReactive
│   ├── EnergyApparent
│   ├── PowerFactor
│   └── Frequency
├── Environment
│   ├── Temperature
│   ├── Humidity
│   └── CaseTemperature
└── Vibration
    ├── Axial
    └── Radial
```

## 🔔 Alarmes e Eventos

### O servidor OPC UA deve gerar eventos e alarmes com as seguintes condições:

| Evento                          | Categoria   | Severidade | Mensagem                  |
| ------------------------------- | ----------- | ---------- | ------------------------- |
| Tensão > 10% acima da nominal   | Electrical  | Alta       | Overvoltage detected      |
| Tensão < 10% abaixo da nominal  | Electrical  | Alta       | Undervoltage detected     |
| Corrente > 10% acima da nominal | Electrical  | Alta       | Overcurrent detected      |
| Temperatura da carcaça > 60°C   | Environment | Crítica    | Case temperature critical |

## 🔢 Tabela para os valores de criticidade

| Criticidade     | Valor de `Severity` | Uso no seu exercício                           |
| --------------- | ------------------- | ---------------------------------------------- |
| **Informativo** | `100`               | Eventos de status, heartbeat, etc.             |
| **Baixa**       | `250`               | Vibração leve ou pequenas variações ambientais |
| **Média**       | `500`               | Temperatura levemente acima do esperado        |
| **Alta**        | `700`               | Sobrecorrente ou sobretensão moderada          |
| **Crítica**     | `900`               | Temperatura da carcaça acima de 60°C           |



## 🕓 Histórico

  * Armazene o histórico das variáveis elétricas e temperatura da carcaça, com resolução de 1s.

  * Armazene o histórico de eventos/alarmes em um banco local ou em arquivo.

## 🔌 Discovery

  * Crie uma task que faça o registro em um LDS customizado.

## ☁️ Integração com MQTT

  * Receber as mensagens via MQTT (subscribe).
  * Atualizar as variáveis no servidor OPC UA.
  * Gerar alarmes e armazenar histórico conforme as regras acima.

## 📦 Formato das Mensagens MQTT
### Use o seguinte formato JSON para os tópicos de cada sensor:

Tópico: `scgdi/motor/electrical`

```json
{
  "timestamp": "2025-08-08T12:00:00Z",
  "voltage": {"a": 220.0, "b": 221.1, "c": 219.5},
  "current": {"a": 10.5, "b": 10.4, "c": 10.6},
  "power": {"active": 4500, "reactive": 500, "apparent": 4600},
  "energy": {"active": 10000, "reactive": 1200, "apparent": 10200},
  "powerFactor": 0.95,
  "frequency": 60.0
}
```

Tópico: `scgdi/motor/environment`

```json
{
  "timestamp": "2025-08-08T12:00:00Z",
  "temperature": 34.5,
  "humidity": 55.2,
  "caseTemperature": 62.0
}
```

Tópico: `scgdi/motor/vibration`

```json
{
  "timestamp": "2025-08-08T12:00:00Z",
  "axial": 0.12,
  "radial": 0.15
}
```

## ✅ Tarefas

  * Implemente o servidor OPC UA com a árvore e variáveis conforme estrutura.
  * Implemente regras de geração de eventos e alarmes.
  * Habilite o histórico das variáveis e eventos.
  * Integre com um broker MQTT remoto: `lse.dev.br`.
  * Implemente um cliente MQTT que recebe dados dos sensores.
  * Implemente o registro em um LDS customizado.

## 🎓 Dicas de Ferramentas
  * OPC UA SDKs recomendados:
      * Python: asyncio-opcua: `asyncua`
  * Cliente MQTT: MQTT Explorer e `gmqtt`
  * Ferramenta de Teste OPC UA: `UaExpert`