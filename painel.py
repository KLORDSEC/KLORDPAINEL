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
grupo = '@YunaDivulgadora'

client = TelegramClient(session_name, api_id, api_hash)
console = Console()
fake = Faker('pt_BR')

comandos = {
    "1": "/cpf",
    "2": "/telefone",
    "3": "/placa",
    "4": "/nome",
    "5": "/cnpj",
    "6": "/email",
    "7": "/vacina",
    "8": "/rg",
    "9": "/cep",
    "10": "/ip",
    "11": "/score",
    "12": "/obito",
    "13": "/beneficio"
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
[01] CPF
[02] TELEFONE
[03] PLACA
[04] NOME
[05] CNPJ
[06] EMAIL
[07] VACINA
[08] RG
[09] CEP
[10] IP
[11] SCORE
[12] ÓBITO
[13] BENEFÍCIO
[14] GERAR PESSOA
[00] SAIR[/bold bright_green]
"""

titulo = "[bold red]╔═╦═╦═╦═╦═╦═╦═╦═╦═╦═╦═╦═╗[/bold red]\n[bold red]║[/bold red] [bold white]K L O R D   P A N E L[/bold white] [bold red]║\n╚═╩═╩═╩═╩═╩═╩═╩═╩═╩═╩═╝[/bold red]"

# ======= FUNÇÕES =======
async def enviar_e_receber(mensagem):
    me = await client.get_me()
    msg_enviada = await client.send_message(grupo, mensagem)
    msg_id = msg_enviada.id

    await asyncio.sleep(15)

    mensagens = await client.get_messages(grupo, limit=30)
    for msg in mensagens:
        if msg.out or not msg.reply_to_msg_id:
            continue

        try:
            original = await client.get_messages(grupo, ids=msg.reply_to_msg_id)
            if original.sender_id != me.id:
                continue
        except:
            continue

        # Se tiver anexo, processa o arquivo primeiro
        if msg.file:
            path = await msg.download_media()
            if path and os.path.exists(path):
                linhas = []
                for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'utf-16']:
                    try:
                        with open(path, 'r', encoding=encoding) as f:
                            linhas = f.readlines()[:-3]
                            break
                    except Exception:
                        continue

                if not linhas:
                    os.remove(path)
                    continue

                conteudo = ''.join(linhas)
                console.print(Panel(conteudo, title="[bold green]Resultado", subtitle="KLORD BUSCAS"))
                os.remove(path)
                input("\nPressione [ENTER] para voltar ao menu...")
                return

        # Se não tiver anexo, mostra o texto
        elif msg.text:
            console.print(Panel(msg.text, title="[bold green]Resultado", subtitle="KLORD BUSCAS"))
            input("\nPressione [ENTER] para voltar ao menu...")
            return

    console.print("[red]Nenhuma resposta recebida pra você.")
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
            await enviar_e_receber(f"{comandos[opcao]} {dado}")

# ===== EXECUÇÃO =====
if __name__ == "__main__":
    async def main():
        await client.start()
        await painel()

    client.loop.run_until_complete(main())