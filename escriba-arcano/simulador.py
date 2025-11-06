import agente  # Importa o seu agente.py (FRENTE 1)
import os

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
        print("="*50)

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear') # Limpa a tela
    simular_bot_discord()
    print("\n--- Simulador encerrado. ---")