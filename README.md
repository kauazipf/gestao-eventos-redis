# 🎪 Gestão de Eventos com Redis

Projeto prático que demonstra o uso do **Redis** como camada intermediária de desempenho e comunicação em uma aplicação de **gestão de eventos ao vivo**. Implementa três funcionalidades essenciais: **cache de dados**, **fila de notificações** e **canal de atualizações em tempo real** via Pub/Sub.

Ideal para cenários com alto volume de requisições, onde é necessário **responder rapidamente aos usuários** sem sobrecarregar a fonte de dados principal.

---

## 🧩 Funcionalidades Implementadas

### 1. **Cache de Eventos**
- Verifica se os dados de um evento (`event:<id>`) estão no cache do Redis.
- Se não estiverem, busca em uma fonte simulada (dicionário local) e armazena no Redis com **TTL de 60 segundos**.
- Usa os comandos `GET` e `SETEX`.

### 2. **Fila de Notificações**
- Notificações (usuário + mensagem) são **enfileiradas** na lista `notificacao:fila`.
- Um consumidor em **modo bloqueante** (`BRPOP`) processa as mensagens em tempo real.
- Usa `LPUSH` para inserção e `BRPOP` para consumo.

### 3. **Publicação/Assinatura (Pub/Sub)**
- Atualizações de eventos são **publicadas** no canal `eventos:atualizacoes`.
- Um ouvinte **inscrito** no canal exibe todas as mensagens recebidas em tempo real.
- Exemplo: "Evento X foi atualizado!".

---

## 📦 Estrutura do Projeto
  gestao-eventos-redis/
    ├── main.py # Código principal com as 3 funcionalidades
    ├── requirements.txt # Dependências do projeto
    └── README.md # Este arquivo

---

## ⚙️ Requisitos

- **Python 3.7+**
- **Docker** (para rodar o Redis facilmente)
- Biblioteca `redis` (instalada via `pip`)
