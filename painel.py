import asyncio
import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from faker import Faker
from validate_docbr import CPF
import random

# ======= CONFIG =======
api_id = 24344843
api_hash = '810897451143f53c4a437765a6eae76c'
session_name = 'session'
grupo = '@GOLDSPACEOFC'
thread_id = 19423

client = TelegramClient(session_name, api_id, api_hash)
console = Console()
fake = Faker('pt_BR')

comandos = {
    "1": "/cpf",
    "2": "/telefone",
    "3": "/placa",
    "4": "/nome",
    "5": "/cnpj",
    "6": "/rg",
    "7": "/score",
    "8": "/obito",
    "9": "/beneficio",
    "10": "/cep",
    "11": "/ip"
}

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
[03] PLACA       [04] NOME
[05] CNPJ        [06] RG
[07] SCORE       [08] ÓBITO
[09] BENEFÍCIO   [10] CEP
[11] IP
[14] GERAR PESSOA
[00] SAIR[/bold bright_green]
"""

titulo = "[bold red]╔═╦═╦═╦═╦═╦═╦═╦═╦═╦═╦═╦═╗[/bold red]\n[bold red]║[/bold red] [bold white]K L O R D   B U S C A[/bold white] [bold red]║\n╚═╩═╩═╩═╩═╩═╩═╩═╩═╩═╩═╝[/bold red]"

async def enviar_e_receber(comando, dado):
    msg_enviada = await client.send_message(
        entity=grupo,
        message=f"{comando} {dado}",
        reply_to=thread_id
    )

    await asyncio.sleep(10)
    me = await client.get_me()
    mensagens = await client.get_messages(grupo, limit=20)

    # CPF: botão CPF | COMPLETO
    if comando == "/cpf":
        for msg in mensagens:
            if msg.reply_to_msg_id == msg_enviada.id and msg.buttons:
                for row in msg.buttons:
                    for btn in row:
                        if "CPF | COMPLETO" in btn.text.upper():
                            await msg.click(text=btn.text)
                            await asyncio.sleep(10)
                            respostas = await client.get_messages(grupo, limit=10)
                            filtradas = [r for r in respostas if r.reply_to_msg_id == msg_enviada.id and r.sender_id != me.id]
                            for r in filtradas:
                                if r.file:
                                    return await tratar_resposta(r)
                            for r in filtradas:
                                if r.text:
                                    return await tratar_resposta(r)

    # NOME: botão NOME
    elif comando == "/nome":
        for msg in mensagens:
            if msg.reply_to_msg_id == msg_enviada.id and msg.buttons:
                for row in msg.buttons:
                    for btn in row:
                        if "NOME" in btn.text.upper():
                            await msg.click(text=btn.text)
                            await asyncio.sleep(10)
                            respostas = await client.get_messages(grupo, limit=10)
                            filtradas = [r for r in respostas if r.reply_to_msg_id == msg_enviada.id and r.sender_id != me.id]
                            for r in filtradas:
                                if r.file:
                                    return await tratar_resposta(r)
                            for r in filtradas:
                                if r.text:
                                    return await tratar_resposta(r)

    # Respostas padrão
    respostas_validas = [
        msg for msg in mensagens
        if msg.reply_to_msg_id == msg_enviada.id and msg.sender_id != me.id
    ]

    for msg in respostas_validas:
        if msg.file:
            return await tratar_resposta(msg)
    for msg in respostas_validas:
        if msg.text:
            return await tratar_resposta(msg)

    console.print("[red]Nenhuma resposta encontrada.")
    input("\nPressione [ENTER] para voltar ao menu...")

async def tratar_resposta(msg):
    if msg.file:
        path = await msg.download_media()
        if path.endswith('.txt'):
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                linhas = f.readlines()
                conteudo = ''.join(linhas[:-3]) if len(linhas) > 3 else ''.join(linhas)
                console.print(Panel(conteudo, title="[bold green]Resultado", subtitle="KLORD BUSCAS"))
        else:
            console.print(Panel(f"Arquivo baixado: {os.path.basename(path)}", title="[yellow]Arquivo"))
        os.remove(path)
    elif msg.text:
        console.print(Panel(msg.text, title="[bold green]Resultado", subtitle="KLORD BUSCAS"))
    input("\nPressione [ENTER] para voltar ao menu...")

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
    while True:
        os.system("clear")
        console.print(ascii_lupa)
        console.print(titulo, justify="center")
        console.print(Panel(menu_texto, border_style="bright_black", padding=(1, 4)))

        opcao = Prompt.ask("[bold yellow]Escolha uma opção", choices=list(comandos.keys()) + ["0", "14"])

        if opcao == "0":
            console.print("[bold red]Saindo... até logo!")
            break
        elif opcao == "14":
            gerar_pessoa()
        else:
            dado = Prompt.ask(f"[bold cyan]Digite o dado para a consulta ({comandos[opcao]})")
            await enviar_e_receber(comandos[opcao], dado)

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(painel())
