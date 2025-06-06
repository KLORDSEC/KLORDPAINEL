import asyncio
import os
import random
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from faker import Faker
from validate_docbr import CPF
from datetime import datetime

# === CONFIG TELEGRAM ===
api_id = 24344843
api_hash = '810897451143f53c4a437765a6eae76c'
session_name = 'session'
grupo = '@DBSPUXADASVIP'
topico_id = None

client = TelegramClient(session_name, api_id, api_hash)
console = Console()
fake = Faker('pt_BR')

# === USUÁRIOS FIXOS ===
usuarios = {
    "klord": "CR7",
    "vip1": "revpass1",
    "vip2": "10820265",
    "vip3": "20650273",
    "vip4": "01549227",
    "vip5": "29639265",
    "vip6": "0279483",
    "vip7": "gift365",
    "vip8": "klord029",
    "vip9": "klord87",
    "member": "member"
}

def login():
    console.print("[bold cyan]🔐 Usuários disponíveis:[/bold cyan]")
    for user in usuarios:
        console.print(f"🧑 {user}")
    user = Prompt.ask("[bold green]Escolha seu usuário").strip()
    senha = Prompt.ask("[bold yellow]Digite sua senha", password=True)
    if user in usuarios and usuarios[user] == senha:
        console.print(f"[green]✔ Acesso liberado para [bold]{user}[/bold]")
    else:
        console.print("[red]❌ Usuário ou senha incorretos.")
        exit()

ascii_lupa = """[bold green]
                ______
             .-'      `-.
           .'            `.
          /                \\
         ;                 ;`
         |          /      |;
         ;         / / /   ;|
         '\\       / / /   / ;
          \\`.    / /    .' /
           `.`-._____.-' .'
             / /`_____.-'
            / / /
           / / /
          / / /
         / / /
        / / /
       / / /
      / / /
     / / /
    / / /
    \\/_/[/bold green]
"""

menu_texto = """[bold bright_green]
╔══════════════════════════════════╗
║         OPÇÕES DE BUSCA          ║
╚══════════════════════════════════╝
[01] 🔍 CPF
[02] 📞 TELEFONE
[03] 🆔 RG
[04] 🚘 PLACA
[05] 🏢 CNPJ
[06] 👤 NOME
[07] 📍 CEP
[14] 🧬 GERAR PESSOA
[15] 💳 GERAR GG
[00] ❌ SAIR
[/bold bright_green]
"""

titulo = "[bold red]╔═╦═╦═╦═╦═╦═╦═╦═╦═╦═╦═╦═╗[/bold red]\n[bold red]║[/bold red] [bold white]K L O R D   B U S C A[/bold white] [bold red]║\n╚═╩═╩═╩═╩═╩═╩═╩═╩═╩═╩═╝[/bold red]"

comandos = {
    "1": "/cpf",
    "2": "/telefone",
    "3": "/rg",
    "4": "/placa",
    "5": "/cnpj",
    "6": "/nome",
    "7": "/cep"
}

def gerar_gg():
    bandeiras = {
        "Visa": "4",
        "MasterCard": "5",
        "Elo": "636368",
        "Amex": "34",
        "Hipercard": "38"
    }
    bandeira = random.choice(list(bandeiras.keys()))
    inicio = bandeiras[bandeira]
    numero = inicio + ''.join([str(random.randint(0, 9)) for _ in range(15 - len(inicio))])
    numero = ' '.join([numero[i:i+4] for i in range(0, len(numero), 4)])
    validade = f"{random.randint(1,12):02d}/{random.randint(2025,2030)}"
    cvv = f"{random.randint(100,999)}"
    nome = fake.name()
    cpf = CPF().generate()
    estado = fake.estado_sigla()
    gg = f"""
💳 Cartão Gerado:

Bandeira: {bandeira}
Número: {numero}
Validade: {validade}
CVV: {cvv}
Nome: {nome}
CPF: {cpf}
UF: {estado}
"""
    console.print(Panel(gg.strip(), title="[bold blue]GG Criado", subtitle="KLORD GEN"))

async def enviar_e_receber(comando, dado):
    msg_enviada = await client.send_message(grupo, f"{comando} {dado}", reply_to=topico_id)
    await asyncio.sleep(random.uniform(8, 12))
    me = await client.get_me()
    mensagens = await client.get_messages(grupo, limit=20)
    for msg in mensagens:
        if msg.reply_to_msg_id == msg_enviada.id and msg.buttons:
            botoes = [btn for row in msg.buttons for btn in row]
            console.print("\n[bold cyan]📦 Bases disponíveis:[/bold cyan]")
            for i, botao in enumerate(botoes):
                nome_base = botao.text.replace("VOID", "KLORD")
                console.print(f"[bold green][{i+1}][/bold green] 🔹 {nome_base}")
            escolha = Prompt.ask("[bold yellow]Escolha a base", choices=[str(i+1) for i in range(len(botoes))])
            btn_escolhido = botoes[int(escolha)-1]
            console.print(f"[green]▶ Clicando em: {btn_escolhido.text}")
            await msg.click(text=btn_escolhido.text)
            await asyncio.sleep(10)
            respostas = await client.get_messages(grupo, limit=10)
            return await filtrar_resposta(respostas, msg_enviada.id, me.id)
    return await filtrar_resposta(mensagens, msg_enviada.id, me.id)

async def filtrar_resposta(mensagens, reply_id, my_id):
    for msg in mensagens:
        if msg.reply_to_msg_id == reply_id and msg.file and msg.file.name.endswith('.txt') and msg.sender_id != my_id:
            return await tratar_resposta(msg)
    for msg in mensagens:
        if msg.reply_to_msg_id == reply_id and msg.text and not msg.file and msg.sender_id != my_id:
            return await tratar_resposta(msg)
    console.print("[red]❌ Nenhuma resposta encontrada.")
    input("\nPressione [ENTER] para voltar ao menu...")

async def tratar_resposta(msg):
    if msg.file:
        path = await msg.download_media()
        if path.endswith('.txt'):
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                linhas = f.readlines()
                conteudo = ''.join(linhas[:-2]) if len(linhas) > 2 else ''.join(linhas)
                console.print(Panel(conteudo.strip(), title="[bold green]Resultado", subtitle="KLORD BUSCAS"))
                with open("buscas_log.txt", "a", encoding="utf-8") as log:
                    log.write(f"\n[{datetime.now()}]\n{conteudo}\n")
            os.remove(path)
    elif msg.text:
        console.print(Panel(msg.text, title="[bold green]Resultado", subtitle="KLORD BUSCAS"))
    input("\n[bold cyan]Pressione [ENTER] para voltar ao menu...[/bold cyan]")

def gerar_pessoa():
    cpf = CPF().generate()
    sexo = Prompt.ask("[bold cyan]Sexo", choices=["1", "2"], default="1")
    nome = fake.name_male() if sexo == "1" else fake.name_female()
    idade = random.randint(18, 70)
    estado = fake.estado_nome()
    pessoa = f"Nome: {nome}\nCPF: {cpf}\nIdade: {idade}\nEstado: {estado}"
    console.print(Panel(pessoa, title="[bold green]Pessoa Gerada", subtitle="KLORD BUSCAS"))
    input("\nPressione [ENTER] para voltar ao menu...")

async def painel():
    login()
    await client.start()
    while True:
        os.system("clear")
        console.print(ascii_lupa)
        console.print(titulo)
        console.print(menu_texto)
        escolha = Prompt.ask("[bold yellow]Escolha uma opção", choices=list(comandos.keys()) + ["14", "15", "00"])
        if escolha == "14":
            gerar_pessoa()
        elif escolha == "15":
            gerar_gg()
            input("\nPressione [ENTER] para voltar ao menu...")
        elif escolha == "0":
            console.print("[bold red]Saindo...")
            break
        else:
            dado = Prompt.ask(f"[bold cyan]Digite o dado para {comandos[escolha]}")
            await enviar_e_receber(comandos[escolha], dado)

if __name__ == '__main__':
    asyncio.run(painel())
