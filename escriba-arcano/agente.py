import json
import random
from langchain_community.llms import Ollama
import memoria
# Não vamos mais usar o 'conhecimento.py'

try:
    # --- A ÚNICA MUDANÇA ESTÁ AQUI ---
    llm = Ollama(model="llama3") 
    print("Conexão com Ollama/Llama3 estabelecida.")
except Exception as e:
    print(f"FALHA AO CONECTAR NO OLLAMA: {e}")
    llm = None

# --- Carregando o Contexto (O JSON) ---
try:
    with open('tracos.json', 'r', encoding='utf-8') as f:
        TRACOS_DB = json.load(f)
    print(f"[Agente] Banco de {len(TRACOS_DB)} traços carregado na memória.")
except Exception as e:
    print(f"ERRO CRÍTICO: 'tracos.json' não foi encontrado. {e}")
    TRACOS_DB = []

# --- Wrappers da FRENTE 3 (Memória) ---
def consultar_estado_real(jogador_nome: str) -> dict:
    print(f"\n[FRENTE 3] Consultando estado de {jogador_nome} via memoria.py...")
    return memoria.consultar_estado_real(jogador_nome)

def atualizar_estado_real(jogador_nome: str, novo_traco: str) -> bool:
    print(f"\n[FRENTE 3] ATUALIZANDO {jogador_nome} -> Adicionando Traço: {novo_traco} via memoria.py...")
    return memoria.atualizar_estado_real(jogador_nome, novo_traco)


# --- FRENTE 1: O AGENTE ORQUESTRADOR (NLI) ---

def encontrar_traco_com_llm(resumo: str) -> dict:
    """
    Esta é a nova NLI de "Entendimento" (RAG).
    Usa o LLM para ler o tracos.json e escolher o melhor.
    """
    if llm is None: raise Exception("OLLAMA NÃO ESTÁ RODANDO.")
    
    contexto_tracos = json.dumps(TRACOS_DB, indent=2, ensure_ascii=False)
    
    prompt_escolha = f"""
    Você é um Mestre de Jogo (IA). Sua tarefa é analisar um evento e compará-lo com um banco de dados de traços.
    
    O EVENTO:
    "{resumo}"
    
    O BANCO DE DADOS DE TRAÇOS (JSON):
    {contexto_tracos}
    
    Analise o EVENTO e encontre o traço do BANCO DE DADOS que melhor se aplica semanticamente.
    (Ex: "faca enferrujada" pode se aplicar a "Exposto a Doenças").
    (Ex: "tesouro" pode se aplicar a "Ganância").
    (Ex: "pedrada na cabeça" pode se aplicar a "Cabeça Dura").
    
    Responda APENAS com o nome exato do traço (ex: "Aracnofobia") ou "Nenhum" se nada se aplicar.
    Sua Resposta:
    """
    
    print(f"[Agente IA] Invocando Llama3 para ESCOLHER um traço...")
    resposta_llm = llm.invoke(prompt_escolha).strip()
    
    resposta_llm = resposta_llm.replace('"', '').replace("'", "")
    
    print(f"[Agente IA] Llama3 escolheu: '{resposta_llm}'")
    
    if resposta_llm.lower() == "nenhum":
        return None
        
    for traco in TRACOS_DB:
        if traco['nome'].lower() == resposta_llm.lower():
            return traco
            
    print(f"[Agente IA] AVISO: Llama3 escolheu '{resposta_llm}', mas não achei no DB.")
    return None


def processar_narrativa_mestre(personagem: str, resumo: str) -> str:
    """
    Função principal do Agente (FRENTE 1).
    Orquestra a FRENTE 3, e o LLM (para Entendimento E Geração).
    """
    print(f"\n--- Processando narrativa para {personagem} (Agente NLI v2.0) ---")
    try:
        # 1. AGENTE chama NLI (LLM) para encontrar o traço
        traco_encontrado = encontrar_traco_com_llm(resumo)
        
        # 2. AGENTE analisa a resposta
        if traco_encontrado is None:
            msg = f"O Mestre narra o evento de {personagem}, mas nada profundamente marcante acontece."
            print(f"[Agente] Resposta: {msg}")
            return msg
        
        # --- ADIÇÃO DA LÓGICA DO D20 (Sua ideia) ---
        d20_roll = random.randint(1, 20)
        gravidade_dc = 10  # Teste de resistência (Fácil)
        
        print(f"[Agente] Evento ({traco_encontrado['nome']}) detectado. Rolando D20 (CD {gravidade_dc})...")
        
        if d20_roll >= gravidade_dc:
            msg = (
                f"Apesar do evento '{traco_encontrado['nome']}', {personagem} resistiu (D20: {d20_roll})!"
                f"\nO traço **não** foi aplicado."
            )
            print(f"[Agente] Resposta: {msg}")
            return msg
            
        print(f"[Agente] Falhou no teste (D20: {d20_roll}). O traço será aplicado.")

        # 3. AGENTE chama MEMÓRIA (FRENTE 3)
        nome_traco = traco_encontrado['nome']
        estado_jogador = consultar_estado_real(personagem) 
        
        # --- CORREÇÃO DO BUG ('list' object has no attribute 'get') ---
        if isinstance(estado_jogador, dict):
            lista_de_tracos_atuais = estado_jogador.get('tracos_atuais', [])
        elif isinstance(estado_jogador, list):
            lista_de_tracos_atuais = estado_jogador 
        else:
            lista_de_tracos_atuais = []

        # 4. AGENTE toma a decisão (Lógica)
        if nome_traco in lista_de_tracos_atuais:
            msg = f"A experiência de {personagem} reforça um traço existente: **{nome_traco}**."
            print(f"[Agente] Resposta: {msg}")
            return msg
        
        # 5. É um TRAÇO NOVO!
        atualizado = atualizar_estado_real(personagem, nome_traco)
        if not atualizado:
            msg = f"A experiência de {personagem} reforça um traço existente: **{nome_traco}**."
            print(f"[Agente] Resposta: {msg}")
            return msg

        # 5b. Gerar a resposta NLI (Chamar o LLM de novo, agora para NARRAR)
        prompt_nli = f"""
        Você é um Mestre de Jogo sombrio, como o Narrador de Darkest Dungeon.
        Um jogador chamado '{personagem}' acabou de passar por um evento e falhou num teste de resistência (Rolou {d20_roll} / CD {gravidade_dc}).
        Ele desenvolveu um novo traço.

        O EVENTO: {resumo}
        O TRAÇO: {traco_encontrado['nome']} ({traco_encontrado['tipo']})
        DESCRIÇÃO: {traco_encontrado['descricao_narrativa']}
        EFEITO MECÂNICO: {traco_encontrado['efeito_mecanico']}
        
        Escreva uma resposta NARRATIVA e dramática para o jogador.
        Anuncie a falha no teste, o novo traço adquirido e seu efeito.
        """

        print(f"[Agente IA] Invocando Llama3 para gerar a narrativa...")
        resposta_narrativa = llm.invoke(prompt_nli)
        
        print(f"[Agente IA] Resposta NLI gerada.")
        return resposta_narrativa

    except Exception as e:
        print(f"Erro no Agente: {e}")
        return f"Ocorreu um erro: {e}"

# --- Bloco de Teste ---
if __name__ == "__main__":
    if llm is not None and TRACOS_DB:
        print("--- INICIANDO TESTE DO AGENTE (FRENTE 1) - NLI v2.0 com Llama3 ---")
        
        print("\n\n--- TESTE 1: RESUMO NEUTRO (Llama3 deve dizer 'Nenhum') ---")
        resultado1 = processar_narrativa_mestre(
            personagem="Grog", 
            resumo="Grog tomou um café e leu um livro."
        )
        print("\n--- RESULTADO FINAL (Teste 1) ---")
        print(resultado1)
        
        print("\n\n--- TESTE 2: RESUMO 'FACA' (Llama3 deve ACHAR 'Exposto a Doenças') ---")
        resultado3 = processar_narrativa_mestre(
            personagem="Biel",
            resumo="biel tomou uma pedrada na cabeça na dungeon durante uma luta, matou um orc bem grande mas tomou um corte de uma faca enferrujada"
        )
        print("\n--- RESULTADO FINAL (Teste 2) ---")
        print(resultado3)
        
        print("\n\n--- TESTE 3: RESUMO 'COGUMELO' (Llama3 deve ACHAR 'Imprudente') ---")
        resultado4 = processar_narrativa_mestre(
            personagem="Biel",
            resumo="biel lambeu um cogumelo estranho na caverna"
        )
        print("\n--- RESULTADO FINAL (Teste 3) ---")
        print(resultado4)

    else:
        if llm is None: print("ERRO CRÍTICO: Ollama não está conectado.")
        if not TRACOS_DB: print("ERRO CRÍTICO: 'tracos.json' não foi encontrado ou está vazio.")