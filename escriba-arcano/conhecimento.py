import json
import re

print("[Conhecimento] Carregando tracos.json para a memória...")
try:
    with open('tracos.json', 'r', encoding='utf-8') as f:
        TRACOS_DB = json.load(f)
except FileNotFoundError:
    print("[Conhecimento] ERRO CRÍTICO: tracos.json não encontrado.")
    TRACOS_DB = []

print(f"[Conhecimento] Banco de dados com {len(TRACOS_DB)} traços carregado.")

def limpar_texto(texto: str) -> set:
    """Converte texto em um conjunto de palavras normalizadas."""
    palavras = re.findall(r'\b\w+\b', texto.lower())
    return set(palavras)


def buscar_traco_relevante(resumo_evento: str, tipo_desejado: str = None) -> dict:
    """
    Busca o traço mais relevante no JSON com base na contagem de gatilhos.
    Esta é a função que a FRENTE 1 (Agente) irá chamar.
    """
    print(f"\n[Conhecimento] Nova Busca (NÃO-IA) Recebida: '{resumo_evento}'")
    
    palavras_resumo = limpar_texto(resumo_evento)
    if not palavras_resumo:
        return {"erro": "Resumo do evento estava vazio."}

    melhor_traco = None
    maior_score = 0

    for traco in TRACOS_DB:
        if tipo_desejado and traco['tipo'] != tipo_desejado:
            continue

        gatilhos_traco = set(traco['gatilhos'])
        score_atual = len(palavras_resumo.intersection(gatilhos_traco))

        print(f"  - Verificando '{traco['nome']}': Score = {score_atual}")

        if score_atual > maior_score:
            maior_score = score_atual
            melhor_traco = traco

    if not melhor_traco:
        print("[Conhecimento] Nenhum traço encontrado (score 0).")
        return {"erro": "Nenhum traço relevante encontrado."}

    print(f"[Conhecimento] Traço Escolhido (Score: {maior_score}): {melhor_traco['nome']}")
    return melhor_traco


if __name__ == "__main__":
    print("\n--- INICIANDO TESTE DE PRECISÃO (ENTREGÁVEL 4) ---")
    
    resumo1 = "O Grog ficou apavorado e com muito medo daquela aranha gigante."
    print(f"\nTeste 1 (Aflição): {resumo1}")
    resultado1 = buscar_traco_relevante(resumo1)
    
    if 'erro' in resultado1:
        print(f"Erro no Teste 1: {resultado1['erro']}")
    else:
        print(f"Resultado 1: {resultado1['nome']}")
        assert resultado1['nome'] == 'Aracnofobia', f"Falha no Teste 1: Esperava 'Aracnofobia', mas recebi '{resultado1['nome']}'"

    resumo2 = "A Lirael não resistiu e pegou mais ouro do que devia do baú de tesouro."
    print(f"\nTeste 2 (Aflição): {resumo2}")
    resultado2 = buscar_traco_relevante(resumo2)
    if 'erro' in resultado2:
        print(f"Erro no Teste 2: {resultado2['erro']}")
    else:
        print(f"Resultado 2: {resultado2['nome']}")
        assert resultado2['nome'] == 'Ganância', f"Falha no Teste 2: Esperava 'Ganância', mas recebi '{resultado2['nome']}'"

    resumo3 = "Kaelen manteve a linha e não recuou um centímetro contra o dragão."
    print(f"\nTeste 3 (Virtude): {resumo3}")
    resultado3 = buscar_traco_relevante(resumo3)
    if 'erro' in resultado3:
        print(f"Erro no Teste 3: {resultado3['erro']}")
    else:
        print(f"Resultado 3: {resultado3['nome']}")
        assert resultado3['nome'] == 'Coragem Inabalável', f"Falha no Teste 3: Esperava 'Coragem Inabalável', mas recebi '{resultado3['nome']}'"

    print("\n--- TESTES CONCLUÍDOS ---")
    print("(Se você não viu um 'AssertionError', passou em tudo!)")