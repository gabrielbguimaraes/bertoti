import json
import os
from typing import Dict, Any, List

DB_FILE = os.path.join(os.path.dirname(__file__), 'estado_jogador.json')

def ler_banco() -> Dict[str, Any]:
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}
    except Exception as e:
        print(f"Erro ao ler o banco de dados: {e}")
        return {}

def escrever_banco(dados: Dict[str, Any]):
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao escrever no banco de dados: {e}")

def criar_jogador_padrao() -> Dict[str, Any]:
    # Removemos a lógica de estresse
    return {
        'tracos_atuais': []
    }

def obter_banco_e_jogador(jogador_nome: str):
    banco = ler_banco()
    if jogador_nome not in banco:
        banco[jogador_nome] = criar_jogador_padrao()
        escrever_banco(banco)
    return banco, banco[jogador_nome]

def consultar_estado(jogador_nome: str) -> Dict[str, Any]:
    banco = ler_banco()
    jogador = banco.get(jogador_nome)
    if not jogador:
        return criar_jogador_padrao()
    # Retorna apenas os traços
    return {
        'tracos_atuais': jogador.get('tracos_atuais', [])
    }

def adicionar_traco(jogador_nome: str, nome_traco: str) -> bool:
    banco, jogador = obter_banco_e_jogador(jogador_nome)

    tracos = jogador.setdefault('tracos_atuais', [])
    if nome_traco in tracos:
        return False # Retorna False se o jogador JÁ TINHA o traço

    tracos.append(nome_traco)
    banco[jogador_nome] = jogador
    escrever_banco(banco)
    return True # Retorna True (traço novo foi adicionado)

# --- Funções do Contrato (Chamadas pela FRENTE 1) ---

def consultar_estado_real(jogador_nome: str, silent: bool = False) -> Dict[str, Any]:
    """Retorna o dicionário de estado do jogador."""
    if not silent:
        print(f"\n[FRENTE 3] Consultando estado de {jogador_nome} via memoria.py...")
    return consultar_estado(jogador_nome)

def atualizar_estado_real(jogador_nome: str, novo_traco: str, silent: bool = False) -> bool:
    """Adiciona um novo traço. Retorna True se foi adicionado, False se já existia."""
    if not silent:
        print(f"\n[FRENTE 3] ATUALIZANDO {jogador_nome} -> Adicionando Traço: {novo_traco} via memoria.py...")
    return adicionar_traco(jogador_nome, novo_traco)