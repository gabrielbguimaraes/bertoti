import json
import os

def carregar_tracos_db() -> list:
    """Carrega o banco de dados de traços do arquivo JSON"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'tracos.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERRO: Não foi possível carregar tracos.json: {e}")
        return []

def adicionar_traco_db(nome: str, tipo: str, descricao_narrativa: str, efeito_mecanico: str) -> tuple[bool, str]:
    """Adiciona um novo traço ao banco de dados"""
    # Load current database
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'tracos.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
    except Exception as e:
        return False, f"Erro ao carregar banco: {str(e)}"
    
    # Check for duplicates
    if any(traco['nome'].lower() == nome.lower() for traco in db):
        return False, "Um traço com este nome já existe."
    
    # Add new trait
    novo_traco = {
        "nome": nome,
        "tipo": tipo,
        "descricao_narrativa": descricao_narrativa,
        "efeito_mecanico": efeito_mecanico
    }
    db.append(novo_traco)
    
    # Save to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        return True, "Traço adicionado com sucesso."
    except Exception as e:
        return False, f"Erro ao salvar: {str(e)}"

def remover_traco_db(nome: str) -> tuple[bool, str]:
    """Remove um traço do banco de dados"""
    # Load current database
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'tracos.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
    except Exception as e:
        return False, f"Erro ao carregar banco: {str(e)}"
    
    # Find and remove the trait
    original_length = len(db)
    db = [traco for traco in db if traco['nome'].lower() != nome.lower()]
    
    if len(db) == original_length:
        return False, f"Traço '{nome}' não encontrado."
    
    # Save updated database
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        return True, f"Traço '{nome}' removido com sucesso."
    except Exception as e:
        return False, f"Erro ao salvar: {str(e)}"

def recarregar_tracos_db() -> list:
    """Recarrega o banco de traços do arquivo JSON"""
    return carregar_tracos_db()