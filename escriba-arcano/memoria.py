import json
import os
from typing import Dict, Any, Optional

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
    return {
        'estresse_atual': 0,
        'limite_estresse': 10,
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
    return {
        'estresse_atual': jogador.get('estresse_atual', 0),
        'limite_estresse': jogador.get('limite_estresse', 10),
        'tracos_atuais': jogador.get('tracos_atuais', [])
    }

def atualizar_estresse(jogador_nome: str, valor_adicional: int) -> bool:
    banco, jogador = obter_banco_e_jogador(jogador_nome)

    estresse_atual = jogador.get('estresse_atual', 0)
    limite = jogador.get('limite_estresse', 10)
    novo = estresse_atual + valor_adicional

    if novo >= limite:
        jogador['estresse_atual'] = 0
        gatilho = True
    else:
        jogador['estresse_atual'] = novo
        gatilho = False

    banco[jogador_nome] = jogador
    escrever_banco(banco)
    return gatilho

def adicionar_traco(jogador_nome: str, nome_traco: str) -> bool:
    banco, jogador = obter_banco_e_jogador(jogador_nome)

    tracos = jogador.setdefault('tracos_atuais', [])
    if nome_traco in tracos:
        return False

    tracos.append(nome_traco)
    banco[jogador_nome] = jogador
    escrever_banco(banco)
    return True

def consultar_estado_real(jogador_nome: str) -> Dict[str, Any]:
    return consultar_estado(jogador_nome)

def atualizar_estado_real(jogador_nome: str, novo_traco: str) -> bool:
    return adicionar_traco(jogador_nome, novo_traco)