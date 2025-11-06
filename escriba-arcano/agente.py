import json
from langchain_community.llms import Ollama

try:
    llm = Ollama(model="qwen")
    print("Conexão com Ollama/Qwen estabelecida.")
except Exception as e:
    print(f"FALHA AO CONECTAR NO OLLAMA: {e}")
    llm = None


def stub_consultar_estado(jogador_nome: str) -> dict:
    """Função FALSA que simula a FRENTE 3."""
    print(f"\n[STUB FRENTE 3] Consultando estado de {jogador_nome}...")
    if jogador_nome.lower() == "grog":
        return {'tracos_atuais': ['Noturno']}
    return {'tracos_atuais': []}

def stub_atualizar_estado_jogador(jogador_nome: str, novo_traco: str) -> bool:
    """Função FALSA que simula a FRENTE 3. (Removemos o estresse)"""
    print(f"\n[STUB FRENTE 3] ATUALIZANDO {jogador_nome} -> Adicionando Traço: {novo_traco}")
    return True

def stub_buscar_traco_relevante(resumo_evento: str) -> dict:
    """Função FALSA que simula a FRENTE 4 (RAG)."""
    print(f"\n[STUB FRENTE 4] Buscando traço para: '{resumo_evento}'...")
    if "aranha" in resumo_evento.lower() or "apavorado" in resumo_evento.lower():
        return {
            'nome': 'Aracnofobia', 'tipo': 'Aflição',
            'descricao_narrativa': 'Pavor de aranhas.',
            'efeito_mecanico': 'Desvantagem contra aranhas.'
        }
    if "corajoso" in resumo_evento.lower():
        return {
            'nome': 'Coragem Inabalável', 'tipo': 'Virtude',
            'descricao_narrativa': 'Você viu o abismo e não piscou.',
            'efeito_mecanico': '+1 em salvaguardas contra Medo.'
        }

    return None


def processar_narrativa_mestre(personagem: str, resumo: str) -> str:
    """
    Esta é a função principal que o bot do Discord (FRENTE 2) irá chamar.
    O "Agente" aqui é esta própria função, que orquestra as Frentes 3, 4 e o LLM.
    """
    print(f"\n--- Processando narrativa para {personagem} (Agente NLI) ---")
    try:
        traco_encontrado = stub_buscar_traco_relevante(resumo)
        
        if traco_encontrado is None:
            msg = f"O Mestre narra o evento de {personagem}, mas nada profundamente marcante acontece."
            print(f"[Agente] Resposta: {msg}")
            return msg
        
        nome_traco = traco_encontrado['nome']
        estado_atual = stub_consultar_estado(personagem) 
        
        if nome_traco in estado_atual['tracos_atuais']:
            msg = f"A experiência de {personagem} reforça um traço existente: **{nome_traco}**."
            print(f"[Agente] Resposta: {msg}")
            return msg
        
        stub_atualizar_estado_jogador(personagem, nome_traco)

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


if __name__ == "__main__":
    if llm is not None:
        print("--- INICIANDO TESTE DO AGENTE (FRENTE 1) - NLI PURO ---")
        
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
        
        stub_original = stub_buscar_traco_relevante
        
        def stub_para_teste_3(resumo_evento: str):
            """Stub modificado para o Teste 3"""
            print(f"\n[STUB FRENTE 4 - TESTE 3] Buscando traço para: '{resumo_evento}'...")
            if "noite" in resumo_evento.lower(): 
                return {
                    'nome': 'Noturno', 
                    'tipo': 'Virtude',
                    'descricao_narrativa': 'A noite é sua aliada.',
                    'efeito_mecanico': 'Vantagem em furtividade à noite.'
                }
            return None

        stub_buscar_traco_relevante = stub_para_teste_3

        print("\n\n--- TESTE 3: TRAÇO REPETIDO (Noturno) ---")
        resultado3 = processar_narrativa_mestre(
            personagem="Grog",
            resumo="Grog caçou perfeitamente durante a noite."
        )
        print("\n--- RESULTADO FINAL (Teste 3) ---")
        print(resultado3)
        

        stub_buscar_traco_relevante = stub_original


    else:
        print("ERRO CRÍTICO: Não foi possível rodar os testes pois o Ollama não está conectado.")