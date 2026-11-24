# Contrato de Comunicação — MoveSafe

## 1. Estrutura dos dados

O Servidor 1 deverá enviar os dados ao Servidor 2 através de um pedido HTTP POST, utilizando JSON.

```json
{
  "sessao_id": 1,
  "timestamp": "2026-11-17T10:30:01",
  "temperatura": 36.8,
  "fc": 82,
  "rmssd": 35.2,
  "emg_rms": 0.42,
  "fadiga_pct": 41.0,
  "zona": "limite",
  "alerta_ativo": false
}
```

## 2. Descrição dos campos

|    Campo     |   Tipo  |                     Descrição                     |
|--------------|---------|---------------------------------------------------|
| sessao_id    | Integer | Identificador da sessão                           |
| timestamp    | String  | Data e hora do registo                            |
| temperatura  | Float   | Temperatura corporal                              |
| fc           | Integer | Frequência cardíaca                               |
| rmssd        | Float   | Indicador de variabilidade da frequência cardíaca |
| emg_rms      | Float   | Valor RMS do sinal EMG                            |
| fadiga_pct   | Float   | Percentagem estimada de fadiga                    |
| zona         | String  | Classificação da zona de esforço                  |
| alerta_ativo | Boolean | Indica se existe um alerta ativo                  |

## 3. Valores permitidos

O campo `zona` só poderá assumir um dos seguintes valores:

- `segura`
- `limite`
- `sobrecarga`

O campo `alerta_ativo` deverá ser um valor booleano (`true` ou `false`).

## 4. Comunicação entre servidores

- **Método HTTP:** POST
- **Formato:** JSON
- **Endpoint:** `/api/dados`
- **Frequência de envio:** 1 envio por segundo (1 Hz).
- **Servidor emissor:** Servidor 1.
- **Servidor recetor:** Servidor 2.

O endereço completo será:

`https://teudominio/api/dados`

O domínio será definido quando o Servidor 2 estiver alojado.