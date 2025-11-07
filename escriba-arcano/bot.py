import discord
from discord import app_commands
import os
import json
from typing import Dict, Any
# Import our RPG system modules
from agente import processar_narrativa_mestre
from memoria import consultar_estado_real
from tracos import carregar_tracos_db, adicionar_traco_db, remover_traco_db, recarregar_tracos_db  # Updated import
# Load environment variables
from dotenv import load_dotenv
load_dotenv()
intents = discord.Intents.default()
intents.members = False
intents.message_content = False
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Load the traits database once at startup
TRACOS_DB = carregar_tracos_db()

def formatar_status_personagem(nome_personagem: str, estado: Dict[str, Any]) -> discord.Embed:
    """Formata o status do personagem para um embed do Discord"""
    embed = discord.Embed(
        title=f"🧠 Status de {nome_personagem}",
        color=0x7289da
    )
    tracos = estado.get('tracos_atuais', [])
    if tracos:
        tracos_str = "\n".join([f"• {traco}" for traco in tracos])
        embed.add_field(name="Traços Atuais", value=tracos_str, inline=False)
    else:
        embed.description = "Nenhum traço registrado até o momento."
    return embed

def formatar_info_traco(nome_traco: str) -> discord.Embed:
    """Formata informações sobre um traço específico"""
    if not TRACOS_DB:
        return discord.Embed(
            title="Erro",
            description="Banco de traços não carregado corretamente.",
            color=0xff0000
        )
    # Procurar o traço no banco de dados
    traco_encontrado = None
    for traco in TRACOS_DB:
        if traco['nome'].lower() == nome_traco.lower():
            traco_encontrado = traco
            break
    if not traco_encontrado:
        return discord.Embed(
            title="Traço não encontrado",
            description=f"O traço '{nome_traco}' não existe no banco de dados.",
            color=0xff0000
        )
    # Criar embed com as informações
    embed = discord.Embed(
        title=f"📖 {traco_encontrado['nome']} ({traco_encontrado['tipo']})",
        description=traco_encontrado['descricao_narrativa'],
        color=0x57f287 if traco_encontrado['tipo'] == "Virtude" else 0xf04747
    )
    embed.add_field(
        name="Efeito Mecânico",
        value=traco_encontrado['efeito_mecanico'],
        inline=False
    )
    return embed

@tree.command(name="processar-evento", description="Processa um evento narrativo e verifica traços")
@app_commands.describe(
    personagem="Nome do personagem que sofreu o evento",
    descricao="Descrição do evento que ocorreu"
)
async def processar_evento(
    interaction: discord.Interaction,
    personagem: str,
    descricao: str
):
    await interaction.response.defer()  # Defer to handle potential delays with LLM
    try:
        # Processar o evento usando o sistema existente
        resposta = processar_narrativa_mestre(personagem, descricao)
        # Criar embed para a resposta
        embed = discord.Embed(
            title=f"📜 Evento Processado para {personagem}",
            description=resposta,
            color=0x9b59b6
        )
        embed.set_footer(text="O sistema analisou o evento e aplicou os efeitos relevantes")
        await interaction.followup.send(embed=embed)
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Erro ao processar evento",
            description=f"Ocorreu um erro: {str(e)}\nVerifique se o Ollama está rodando e o modelo Llama3 está instalado.",
            color=0xff0000
        )
        await interaction.followup.send(embed=error_embed)

@tree.command(name="status-personagem", description="Mostra os traços atuais de um personagem")
@app_commands.describe(
    personagem="Nome do personagem a ser verificado"
)
async def status_personagem(
    interaction: discord.Interaction,
    personagem: str
):
    await interaction.response.defer()
    try:
        # Consultar o estado do personagem
        estado = consultar_estado_real(personagem)
        # Formatar e enviar a resposta
        embed = formatar_status_personagem(personagem, estado)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Erro ao verificar status",
            description=f"Ocorreu um erro: {str(e)}",
            color=0xff0000
        )
        await interaction.followup.send(embed=error_embed)

@tree.command(name="info-traco", description="Mostra informações detalhadas sobre um traço específico")
@app_commands.describe(
    nome="Nome do traço a ser consultado"
)
async def info_traco(
    interaction: discord.Interaction,
    nome: str
):
    await interaction.response.defer()
    try:
        # Formatar e enviar informações do traço
        embed = formatar_info_traco(nome)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Erro ao buscar informações do traço",
            description=f"Ocorreu um erro: {str(e)}",
            color=0xff0000
        )
        await interaction.followup.send(embed=error_embed)

@tree.command(name="listar-traços", description="Lista todos os traços disponíveis")
@app_commands.describe(
    tipo="Filtrar por tipo (Aflição, Virtude, ou deixe em branco para todos)"
)
@app_commands.choices(tipo=[
    app_commands.Choice(name="Aflição", value="Aflição"),
    app_commands.Choice(name="Virtude", value="Virtude")
])
async def listar_tracos(
    interaction: discord.Interaction,
    tipo: str = None
):
    await interaction.response.defer()
    if not TRACOS_DB:
        await interaction.followup.send("⚠️ Banco de traços não carregado. Verifique o arquivo tracos.json.")
        return
    # Filtrar por tipo se especificado
    tracos_filtrados = TRACOS_DB
    if tipo:
        tracos_filtrados = [t for t in TRACOS_DB if t['tipo'] == tipo]
    if not tracos_filtrados:
        await interaction.followup.send(f"⚠️ Nenhum traço encontrado do tipo '{tipo}'.")
        return
    # Criar embed com a lista de traços
    embed = discord.Embed(
        title=f"📚 Lista de Traços {'- ' + tipo if tipo else ''}",
        color=0x3498db
    )
    # Agrupar por tipo para exibição clara
    tipos = {}
    for traco in tracos_filtrados:
        tipo_traco = traco['tipo']
        if tipo_traco not in tipos:
            tipos[tipo_traco] = []
        tipos[tipo_traco].append(traco['nome'])
    for tipo_nome, lista in tipos.items():
        embed.add_field(
            name=tipo_nome,
            value="\n".join([f"• {nome}" for nome in lista[:10]]),  # Mostrar até 10 por tipo
            inline=True
        )
    if len(tracos_filtrados) > 10:
        embed.set_footer(text=f"Mostrando 10 de {len(tracos_filtrados)} traços. Use /info-traco para detalhes.")
    await interaction.followup.send(embed=embed)

# --- NEW COMMANDS FOR TRAIT DATABASE MANAGEMENT ---
@tree.command(name="adicionar-traco-db", description="Adiciona um novo traço ao banco de dados")
@app_commands.describe(
    nome="Nome do novo traço",
    tipo="Tipo do traço (Aflição ou Virtude)",
    descricao="Descrição narrativa do traço",
    efeito="Efeito mecânico do traço"
)
@app_commands.choices(tipo=[
    app_commands.Choice(name="Aflição", value="Aflição"),
    app_commands.Choice(name="Virtude", value="Virtude")
])
async def adicionar_traco_db_cmd(
    interaction: discord.Interaction,
    nome: str,
    tipo: str,
    descricao: str,
    efeito: str
):
    # Check if user has permission (you might want to add more robust permission checks)
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permissão negada",
            description="Apenas administradores podem modificar o banco de traços.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    sucesso, mensagem = adicionar_traco_db(nome, tipo, descricao, efeito)
    
    embed = discord.Embed(
        title="Adicionar Traço ao Banco" + (" ✅" if sucesso else " ❌"),
        description=mensagem,
        color=0x57f287 if sucesso else 0xf04747
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="remover-traco-db", description="Remove um traço do banco de dados")
@app_commands.describe(
    nome="Nome do traço a ser removido"
)
async def remover_traco_db_cmd(
    interaction: discord.Interaction,
    nome: str
):
    # Check if user has permission
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permissão negada",
            description="Apenas administradores podem modificar o banco de traços.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    sucesso, mensagem = remover_traco_db(nome)
    
    embed = discord.Embed(
        title="Remover Traço do Banco" + (" ✅" if sucesso else " ❌"),
        description=mensagem,
        color=0x57f287 if sucesso else 0xf04747
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="recarregar-traços", description="Recarrega o banco de traços sem reiniciar o bot")
async def recarregar_tracos(interaction: discord.Interaction):
    # Check if user has permission
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permissão negada",
            description="Apenas administradores podem modificar o banco de traços.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        # This would trigger agente.py to use the updated database
        global TRACOS_DB
        TRACOS_DB = recarregar_tracos_db()
        
        embed = discord.Embed(
            title="✅ Banco de traços recarregado",
            description=f"{len(TRACOS_DB)} traços carregados.",
            color=0x57f287
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erro ao recarregar",
            description=str(e),
            color=0xf04747
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync()
    print(f'✅ Bot está online! Conectado como {bot.user}')
    print(f'➡️ Comandos slash sincronizados para todos os servidores')

if __name__ == "__main__":
    # Verificar se o token do Discord está configurado
    if not os.getenv('DISCORD_TOKEN'):
        print("ERRO: DISCORD_TOKEN não encontrado no .env")
        print("Certifique-se de ter um arquivo .env com DISCORD_TOKEN=seu_token_aqui")
        exit(1)
    # Verificar se os arquivos necessários existem
    required_files = ['tracos.json', 'estado_jogador.json']
    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        print(f"⚠️ Arquivos necessários não encontrados: {', '.join(missing)}")
        print("Certifique-se de que esses arquivos estão na pasta atual.")
    # Iniciar o bot
    bot.run(os.getenv('DISCORD_TOKEN'))