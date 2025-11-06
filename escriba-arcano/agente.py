import json
from langchain_community.llms import Ollama
import memoria
import conhecimento

# Tenta conectar ao Ollama (LLM)
try:
    llm = Ollama(model="qwen")
    print("Conexão com Ollama/Qwen estabelecida.")
except Exception as e:
    print(f"FALHA AO CONECTAR NO OLLAMA: {e}")
    llm = None

# --- Wrapper da FRENTE 3 (Memória) ---

def consultar_estado_real(jogador_nome: str) -> dict:
    """Delega a chamada para memoria.py"""
    print(f"\n[FRENTE 3] Consultando estado de {jogador_nome} via memoria.py...")
    return memoria.consultar_estado_real(jogador_nome) 

def atualizar_estado_real(jogador_nome: str, novo_traco: str) -> bool:
    """Delega a chamada para memoria.py"""
    print(f"\n[FRENTE 3] ATUALIZANDO {jogador_nome} -> Adicionando Traço: {novo_traco} via memoria.py...")
    return memoria.atualizar_estado_real(jogador_nome, novo_traco)

# --- Wrapper da FRENTE 4 (Conhecimento) ---

def buscar_traco_relevante_real(resumo_evento: str) -> dict:
    """Delega a chamada para conhecimento.py e trata a resposta."""
    print(f"\n[FRENTE 4] Buscando traço via conhecimento.py...")
    
    # Chama a função real da FRENTE 4
    resultado = conhecimento.buscar_traco_relevante(resumo_evento)
    
    # "Tradução" da resposta: A FRENTE 4 retorna {'erro':...} se não achar nada.
    # Esta função converte isso para 'None' para o resto da lógica funcionar.
    if 'erro' in resultado:
        print(f"[FRENTE 4] {resultado['erro']}")
        return None  
    
    return resultado

# --- FRENTE 1: O AGENTE ORQUESTRADOR (NLI) ---

def processar_narrativa_mestre(personagem: str, resumo: str) -> str:
    """
    Função principal do Agente.
    Orquestra as Frentes 3 (memoria), 4 (conhecimento) e o LLM.
    """
    print(f"\n--- Processando narrativa para {personagem} (Agente NLI) ---")
    try:
        # 1. AGENTE chama RAG (FRENTE 4)
        traco_encontrado = buscar_traco_relevante_real(resumo)
        
        # 2. AGENTE analisa a resposta do RAG
        if traco_encontrado is None:
            msg = f"O Mestre narra o evento de {personagem}, mas nada profundamente marcante acontece."
            print(f"[Agente] Resposta: {msg}")
            return msg
        
        # 3. AGENTE chama MEMÓRIA (FRENTE 3)
        nome_traco = traco_encontrado['nome']
        estado_atual = consultar_estado_real(personagem) 
        
        # 4. AGENTE toma a decisão (Lógica)
        if nome_traco in estado_atual.get('tracos_atuais', []):
            msg = f"A experiência de {personagem} reforça um traço existente: **{nome_traco}**."
            print(f"[Agente] Resposta: {msg}")
            return msg
        
        # 5. É um TRAÇO NOVO!
        # 5a. Salvar o novo traço (FRENTE 3)
        atualizado = atualizar_estado_real(personagem, nome_traco)
        if not atualizado:
            # A FRENTE 3 (memoria.py) retorna False se o traço já existia
            msg = f"A experiência de {personagem} reforça um traço existente: **{nome_traco}**."
            print(f"[Agente] Resposta: {msg}")
            return msg

        # 5b. Gerar a resposta NLI (Chamar o LLM)
        if llm is None:
            raise Exception("OLLAMA/QWEN NÃO ESTÁ RODANDO.")
            
        prompt_nli = f"""
        Você é um Mestre de Jogo sombrio, como o Narrador de Darkest Dungeon.
        Um jogador chamado '{personagem}' acabou de passar por um evento e desenvolveu um novo traço.

        O EVENTO: {resumo}
        O TRAÇO: {traco_encontrado['nome']} ({traco_encontrado['tipo']})
        DESCRIÇÃO: {traco_encontrado['descricao_narrativa']}
        EFEITO MECÂNICO: {traco_encontrado['efeito_mecanico']}
        
        Escreva uma resposta NARRATIVA e dramática para o jogador.
        Anuncie o novo traço adquirido e seu efeito.
        """

        print(f"[Agente IA] Invocando Qwen para gerar a narrativa...")
        resposta_narrativa = llm.invoke(prompt_nli)
        
        print(f"[Agente IA] Resposta NLI gerada.")
        return resposta_narrativa

    except Exception as e:
        print(f"Erro no Agente: {e}")
        return f"Ocorreu um erro: {e}"

# --- Bloco de Teste para rodar o 'agente.py' sozinho ---

if __name__ == "__main__":
    if llm is not None:
        print("--- INICIANDO TESTE DO AGENTE (FRENTE 1) - INTEGRADO ---")
        
        print("\n\n--- TESTE 1: RESUMO NEUTRO ---")
        resultado1 = processar_narrativa_mestre(
            personagem="Grog", 
            resumo="Grog tomou um café e leu um livro."
        )
        print("\n--- RESULTADO FINAL (Teste 1) ---")
        print(resultado1)
        
        print("\n\n--- TESTE 2: TRAÇO NOVO (Aracnofobia) ---")
        resultado2 = processar_narrativa_mestre(
            personagem="Grog",
            resumo="Grog foi pego na teia e ficou apavorado com a Aranha Rainha gigante."
        )
        print("\n--- RESULTADO FINAL (Teste 2) ---")
        print(resultado2)
        
        print("\n\n--- TESTE 3: TRAÇO REPETIDO (Noturno) ---")
        # O 'estado_jogador.json' diz que Grog já tem "Noturno"
        resultado3 = processar_narrativa_mestre(
            personagem="Grog",
            resumo="Grog caçou perfeitamente durante a noite." 
            # (O 'conhecimento.py' provavelmente não tem "noite" como gatilho, 
            # então este teste pode falhar ou dar 'nada marcante' 
            # dependendo do 'tracos.json' que a FRENTE 4 criou)
        )
        print("\n--- RESULTADO FINAL (Teste 3) ---")
        print(resultado3)

    else:
        print("ERRO CRÍTICO: Não foi possível rodar os testes pois o Ollama não está conectado.")