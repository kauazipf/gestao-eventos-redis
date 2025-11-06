import redis
import time
import threading
import json

# Conexão com o Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Simulação da fonte de dados (banco de dados real) – agora com mais eventos!
eventos_db = {
    "1": {"id": "1", "titulo": "Show do Rock", "local": "Estádio XYZ", "data": "2025-11-10", "ingressos_disponiveis": 1500},
    "2": {"id": "2", "titulo": "Palestra de IA", "local": "Centro de Convenções", "data": "2025-11-15", "ingressos_disponiveis": 300},
    "3": {"id": "3", "titulo": "Festival Gastronômico", "local": "Parque Central", "data": "2025-12-01", "ingressos_disponiveis": 2000},
    "4": {"id": "4", "titulo": "Conferência de Sustentabilidade", "local": "Auditório Verde", "data": "2025-11-22", "ingressos_disponiveis": 500},
    "5": {"id": "5", "titulo": "Feira de Tecnologia 2025", "local": "Expo Center", "data": "2025-12-10", "ingressos_disponiveis": 3000},
    "6": {"id": "6", "titulo": "Lançamento do Jogo 'Galaxy Quest'", "local": "Game Arena", "data": "2025-11-30", "ingressos_disponiveis": 800},
    "7": {"id": "7", "titulo": "Workshop de Python Avançado", "local": "Tech Hub", "data": "2025-11-18", "ingressos_disponiveis": 100},
}

# =============================================
# Parte 1 – Cache de Dados de Evento
# =============================================

def obter_evento_com_cache(event_id: str):
    chave = f"event:{event_id}"
    dados_cache = r.get(chave)
    if dados_cache:
        print(f"[CACHE HIT] Evento {event_id} retornado do cache.")
        return json.loads(dados_cache)
    else:
        print(f"[CACHE MISS] Buscando evento {event_id} na fonte de dados...")
        evento = eventos_db.get(event_id)
        if evento:
            r.setex(chave, 60, json.dumps(evento))
            print(f"[CACHE SET] Evento {event_id} armazenado no cache por 60s.")
        else:
            print(f"[ERRO] Evento {event_id} não encontrado.")
        return evento

# =============================================
# Parte 2 – Fila de Notificações
# =============================================

def enviar_notificacao(usuario: str, mensagem: str):
    notificacao = json.dumps({"usuario": usuario, "mensagem": mensagem})
    r.lpush("notificacao:fila", notificacao)
    print(f"[FILA] Notificação enviada para {usuario}: {mensagem}")

def processar_fila_notificacoes():
    print("[FILA] Iniciando processamento de notificações (BRPOP bloqueante)...")
    while True:
        resultado = r.brpop("notificacao:fila", timeout=0)
        if resultado:
            _, notificacao_json = resultado
            notificacao = json.loads(notificacao_json)
            print(f"[NOTIFICAÇÃO PROCESSADA] Usuário: {notificacao['usuario']} | Mensagem: {notificacao['mensagem']}")

# =============================================
# Parte 3 – Canal de Publicação e Assinatura
# =============================================

def publicar_atualizacao_evento(event_id: str, titulo: str):
    mensagem = json.dumps({"event_id": event_id, "titulo": titulo})
    r.publish("eventos:atualizacoes", mensagem)
    print(f"[PUB] Publicado no canal 'eventos:atualizacoes': {mensagem}")

def ouvir_atualizacoes_evento():
    pubsub = r.pubsub()
    pubsub.subscribe("eventos:atualizacoes")
    print("[SUB] Inscrito no canal 'eventos:atualizacoes'. Aguardando mensagens...")
    for mensagem in pubsub.listen():
        if mensagem["type"] == "message":
            dados = json.loads(mensagem["data"])
            print(f"[RECEBIDO] Atualização de evento → ID: {dados['event_id']}, Título: {dados['titulo']}")

# =============================================
# Demonstração (main) – com mais testes
# =============================================

if __name__ == "__main__":
    print("=== Aplicação de Gestão de Eventos com Redis ===\n")

    # Parte 1: Teste de cache com múltiplos eventos
    print(">>> Parte 1: Testando cache de eventos")
    print("Buscando evento 2 (deve ser CACHE MISS):")
    print(obter_evento_com_cache("2"))
    print("\nBuscando evento 2 novamente (deve ser CACHE HIT):")
    print(obter_evento_com_cache("2"))
    print("\nBuscando evento 5 (novo evento):")
    print(obter_evento_com_cache("5"))
    print()

    # Parte 2: Iniciar processamento da fila em thread separada
    print(">>> Parte 2: Iniciando processamento da fila em background")
    thread_fila = threading.Thread(target=processar_fila_notificacoes, daemon=True)
    thread_fila.start()
    time.sleep(1)

    # Enviar múltiplas notificações
    enviar_notificacao("Carla", "Seu ingresso para a Feira de Tecnologia foi reservado!")
    enviar_notificacao("Diego", "Workshop de Python: lembre-se de trazer seu notebook.")
    enviar_notificacao("Elena", "Atualização: Show do Rock terá abertura às 19h!")
    time.sleep(2)
    print()

    # Parte 3: Iniciar listener de atualizações
    print(">>> Parte 3: Iniciando ouvinte de atualizações de evento")
    thread_pubsub = threading.Thread(target=ouvir_atualizacoes_evento, daemon=True)
    thread_pubsub.start()
    time.sleep(1)

    # Publicar atualizações para eventos diferentes
    publicar_atualizacao_evento("4", "Conferência de Sustentabilidade: novo palestrante confirmado!")
    publicar_atualizacao_evento("6", "Lançamento do Jogo: sessão de autógrafos após o evento!")
    publicar_atualizacao_evento("7", "Workshop de Python: material disponível no portal!")

    # Manter o programa rodando para demonstração
    try:
        print("\n[MAIN] Aplicação em execução. Pressione Ctrl+C para encerrar.")
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n[MAIN] Encerrando aplicação...")