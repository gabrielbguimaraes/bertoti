# Importa a integração do Ollama com o LangChain
from langchain_community.llms import Ollama

def testar_conexao_ollama():
    print("--- Iniciando teste de conexão ---")

    try:
        # 1. Inicializa o modelo (aponta para o 'qwen' que baixamos)
        llm = Ollama(model="qwen")

        # 2. Prepara um prompt de teste
        prompt_teste = "Qual é a capital do Brasil?"
        print(f"Enviando prompt: '{prompt_teste}'")

        # 3. 'invoke' envia o prompt e espera a resposta
        resposta = llm.invoke(prompt_teste)

        # 4. Imprime a resposta
        print("\n--- Resposta do Qwen ---")
        print(resposta)
        print("\n--- Teste de conexão CONCLUÍDO com sucesso! ---")

    except Exception as e:
        print(f"\n--- ERRO NA CONEXÃO ---")
        print(f"Ocorreu um erro: {e}")
        print("Verifique se o aplicativo Ollama está rodando (deve haver um ícone na bandeja do sistema).")

if __name__ == "__main__":
    testar_conexao_ollama()