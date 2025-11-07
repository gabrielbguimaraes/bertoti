import agente  # Importa o seu agente.py (FRENTE 1)
import os
from tracos import adicionar_traco_db, remover_traco_db

def simular_bot_discord():
    """
    Este script simula o trabalho da FRENTE 2.
    Ele pede os inputs do "Mestre" e chama a FRENTE 1.
    """
    print("--- Simulador de Bot (FRENTE 2) ---")
    print("Digite 'sair' a qualquer momento para terminar.")
    # Verifica se a FRENTE 1 conseguiu se conectar ao Ollama
    if agente.llm is None:
         print("\nERRO CRÍTICO: Não foi possível conectar ao Ollama (Qwen).")
         print("Por favor, verifique se o Ollama está rodando e reinicie este simulador.")
         return
    print("\n[Simulador] Agente NLI pronto para receber comandos.")
    while True:
        print("\n" + "="*50)
        print("--- Nova Requisição (Simulando o Mestre) ---")
        print("1. Processar evento narrativo")
        print("2. Adicionar traço ao banco de dados")
        print("3. Remover traço do banco de dados")
        print("4. Sair")
        
        opcao = input("Escolha uma opção: ")
        if opcao == '4' or opcao.lower() == 'sair':
            break
            
        elif opcao == '1':
            # 1. Simula o Mestre digitando o nome do personagem
            personagem = input("Nome do Personagem: ")
            if personagem.lower() == 'sair':
                break
            # 2. Simula o Mestre digitando o resumo
            resumo = input("Resumo do Evento: ")
            if resumo.lower() == 'sair':
                break
            # 3. Simula a "requisição" do Discord para o seu agente
            print("\n[Simulador] Enviando para o Agente NLI... Aguarde a resposta do Qwen...")
            # Esta é a chamada de integração. O bot (FRENTE 2) chama o agente (FRENTE 1)
            resposta_nli = agente.processar_narrativa_mestre(personagem, resumo)
            # 4. Simula a resposta do bot no canal do Discord
            print("\n--- Resposta do Escriba Arcano (O que iria para o Discord) ---")
            print(resposta_nli)
            
        elif opcao == '2':
            print("\n--- Adicionar Traço ao Banco de Dados ---")
            nome = input("Nome do traço: ")
            tipo = input("Tipo do traço (Aflição/Virtude): ")
            descricao = input("Descrição narrativa: ")
            efeito = input("Efeito mecânico: ")
            
            sucesso, mensagem = adicionar_traco_db(nome, tipo, descricao, efeito)
            print(f"\nResultado: {'SUCESSO' if sucesso else 'ERRO'}")
            print(mensagem)
            
        elif opcao == '3':
            print("\n--- Remover Traço do Banco de Dados ---")
            nome = input("Nome do traço a remover: ")
            
            sucesso, mensagem = remover_traco_db(nome)
            print(f"\nResultado: {'SUCESSO' if sucesso else 'ERRO'}")
            print(mensagem)
            
        else:
            print("Opção inválida. Tente novamente.")
            
        print("="*50)
        
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear') # Limpa a tela
    simular_bot_discord()
    print("\n--- Simulador encerrado. ---")