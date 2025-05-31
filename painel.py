import asyncio
import os
import random
import string
import getpass
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

client = TelegramClient(session_name, api_id, api_hash)
console = Console()
fake = Faker('pt_BR')

# === SENHAS KLORD ===
senhas_disponiveis = [
    "KLRD-7TAX", "KLRD-LZ99", "KLRD-B33Q",
    "KLRD-YX18", "KLRD-Q4VE", "KLRD-92LM"
]
senhas_usadas = []
SENHA_ADMIN_SECRETA = "klordvip123"  # TROQUE AQUI se quiser

def gerar_senhas(qtd=5):
    novas = []
    for _ in range(qtd):
        s = "KLRD-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        novas.append(s)
    console.print("[bold magenta]🔐 Novas senhas geradas:[/bold magenta]")
    for senha in novas:
        console.print(f"  [green]{senha}[/green]")
    return novas

def validar_senha_embutida():
    senha = Prompt.ask("[bold cyan]Digite sua senha de acesso ou [/bold cyan][magenta]/admin[/magenta]")

    if senha == "/admin":
        senha_admin = getpass.getpass(prompt="🔐 Digite a senha secreta do ADMIN (oculta): ")
        if senha_admin == SENHA_ADMIN_SECRETA:
            console.print("[bold green]✔ Acesso ADMIN concedido. Liberado geral.")
            if Prompt.ask("[bold yellow]Deseja gerar novas senhas?", choices=["s", "n"], default="n") == "s":
                gerar_senhas()
            return
        else:
            console.print("[red]❌ Senha de ADMIN incorreta.")
            return validar_senha_embutida()

    if senha in senhas_disponiveis and senha not in senhas_usadas:
        console.print(f"[green]✔ Acesso liberado com a chave [bold]{senha}[/bold].")
        senhas_usadas.append(senha)
    else:
        console.print("[red]❌ Senha inválida ou já usada.")
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
[01] CPF         [02] TELEFONE
[03] RG          [04] PLACA
[05] CNPJ        [06] NOME
[07] CEP
[14] GERAR PESSOA
[00] SAIR[/bold bright_green]
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

async def enviar_e_receber(comando, dado):
    modo = Prompt.ask("[bold magenta]Modo de seleção de base[/bold magenta]: [1] Automático [2] Manual", choices=["1", "2"], default="1")
    base_auto = "VOID"

    msg_enviada = await client.send_message(grupo, f"{comando} {dado}")
    await asyncio.sleep(random.uniform(8, 12))
    me = await client.get_me()
    mensagens = await client.get_messages(grupo, limit=20)

    for msg in mensagens:
        if msg.reply_to_msg_id == msg_enviada.id and msg.buttons:
            botoes = []
            for row in msg.buttons:
                for btn in row:
                    botoes.append(btn)

            if modo == "1":
                for btn in botoes:
                    if base_auto.lower() in btn.text.lower():
                        console.print(f"[green]▶ Clicando automaticamente em: {btn.text}")
                        await msg.click(text=btn.text)
                        await asyncio.sleep(10)
                        respostas = await client.get_messages(grupo, limit=10)
                        return await filtrar_resposta(respostas, msg_enviada.id, me.id)
            else:
                console.print("\n[bold cyan]Bases disponíveis:[/bold cyan]")
                for i, botao in enumerate(botoes):
                    console.print(f"[green][{i+1}][/green] {botao.text}")
                escolha = Prompt.ask("[bold yellow]Escolha o número da base que deseja usar", choices=[str(i+1) for i in range(len(botoes))])
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

    console.print("[red]Nenhuma resposta encontrada.")
    input("\nPressione [ENTER] para voltar ao menu...")

async def tratar_resposta(msg):
    if msg.file:
        path = await msg.download_media()
        if path.endswith('.txt'):
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    linhas = f.readlines()
                    conteudo = ''.join([linha for linha in linhas if linha.strip()])
                    console.print(Panel(conteudo, title="[bold green]Resultado", subtitle="KLORD BUSCAS"))
                    with open("buscas_log.txt", "a", encoding="utf-8") as log:
                        log.write(f"=== {datetime.now()} ===\n{conteudo}\n\n")
            except Exception as e:
                console.print(f"[red]Erro ao ler o arquivo: {e}")
            finally:
                os.remove(path)
        else:
            console.print(Panel(f"📁 Arquivo baixado: {os.path.basename(path)}", title="[yellow]Arquivo"))
    elif msg.text:
        console.print(Panel(msg.text, title="[bold green]Resultado", subtitle="KLORD BUSCAS"))

    input("\n[bold cyan]Pressione [ENTER] para voltar ao menu...[/bold cyan]")

def gerar_pessoa():
    cpf = CPF().generate()
    sexo = Prompt.ask("[bold cyan]Escolha o sexo", choices=["1", "2"], default="1")
    nome = fake.name_male() if sexo == "1" else fake.name_female()
    idade = random.randint(18, 70)
    estado = fake.estado_nome()
    pessoa = f"Nome: {nome}\nCPF: {cpf}\nIdade: {idade}\nEstado: {estado}"
    console.print(Panel(pessoa, title="[bold green]Pessoa Gerada", subtitle="KLORD BUSCAS"))
    input("\nPressione [ENTER] para voltar ao menu...")

async def painel():
    validar_senha_embutida()
    await client.start()
    while True:
        os.system("clear")
        console.print(ascii_lupa)
        console.print(titulo)
        console.print(menu_texto)
        escolha = Prompt.ask("[bold yellow]Escolha uma opção", choices=list(comandos.keys()) + ["14", "00"])

        if escolha == "14":
            gerar_pessoa()
        elif escolha == "00":
            console.print("[bold red]Saindo...")
            break
        else:
            dado = Prompt.ask(f"[bold cyan]Digite o dado para {comandos[escolha]}")
            await enviar_e_receber(comandos[escolha], dado)

if __name__ == '__main__':
    asyncio.run(painel())