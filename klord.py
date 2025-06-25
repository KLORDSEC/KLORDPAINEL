import asyncio, os, random, re, sys, contextlib
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align
from rich import box
from faker import Faker
from validate_docbr import CPF
from datetime import datetime

# ==== CONFIGURAÇÕES ====
api_id = 24344843
api_hash = '810897451143f53c4a437765a6eae76c'
session_name = 'session'
grupo = '@DBSPUXADASVIP'
topico_id = None
telefone = "+5531987705212"  # coloque o seu número aqui

client = TelegramClient(session_name, api_id, api_hash)
console = Console()
fake = Faker('pt_BR')

comandos = {
    "1": "/cpf",
    "2": "/rg",
    "3": "/nome",
    "4": "/placa",
    "5": "/mae",
    "6": "/cnpj",
    "7": "/cns",
    "8": "/pis",
    "9": "/pix",
    "10": "/telefone",
    "11": "/pai",
    "12": "/titulo",
    "13": "/nis",
    "14": "/bin"
}

menu_texto = """\
╔══════════════════════════════╗
║        🔎 KLORD PAINEL       ║
╠══════════════════════════════╣
║ [01] 👤 CPF                  ║
║ [02] 🪪 RG                    ║ 
║ [03] 👤 NOME                 ║
║ [04] 🚘 PLACA                ║
║ [05] 👩‍❤️‍👨 MÃE               ║
║ [06] 🏢 CNPJ                 ║
║ [07] 🩺 CNS                  ║
║ [08] 📌 PIS                  ║
║ [09] 💰 PIX                  ║
║ [10] 📞 TELEFONE             ║
║ [11] 👨 PAI                  ║
║ [12] 🗳️ TÍTULO                ║
║ [13] 🧾 NIS                  ║
║ [14] 💳 BIN                  ║
╠══════════════════════════════╣
║ [00] ❌ SAIR                 ║
╚══════════════════════════════╝
"""

def mostrar_menu():
    os.system('cls' if os.name == 'nt' else 'clear')

    painel = Panel(
        Align.center(menu_texto, vertical="middle"),
        title="[bold bright_green]🔎 KLORD PAINEL 🔎[/bold bright_green]",
        border_style="bright_green",
        width=90,  # largura maior
        padding=(3, 8),  # espaço interno maior (topo/baixo, esquerda/direita)
        box=box.DOUBLE
    )

    print("\n" * 15)  # muitas linhas em branco antes para centralizar verticalmente
    console.print(Align.center(painel))
    print("\n" * 15)  # muitas linhas em branco depois

def formatar_resposta(conteudo):
    linhas = conteudo.splitlines()
    resultado = []

    emojis = {
        "CPF": "👤", "NOME": "👤", "NASCIMENTO": "👤", "SEXO": "👤",
        "NOME MÃE": "👤", "NOME PAI": "👤", "MUNICÍPIO DE NASCIMENTO": "🌍",
        "RAÇA": "🌈", "TIPO SANGÚINEO": "🩸", "RG": "🪪",
        "RENDA": "💰", "SCORE": "📊", "ESTADO CIVIL": "💍",
        "ÓBITO": "⚰️", "STATUS NA RECEITA": "", "RECEBE INSS": "",
        "PIS": "", "NIS": "", "CNS": "💳", "CLASSE SOCIAL": "🏷️",
        "ESCOLARIDADE": "🎓", "PROFISSÃO": "🧑‍💼",
        "EMPRESAS": "🏢", "EMAILS": "✉️", "TELEFONES": "☎️",
        "BANCOS": "🏦", "EMPREGOS": "💼", "PARENTES": "👥",
        "VEICULOS": "🚗", "ENDERECOS": "🏡", "INTERESSES PESSOAIS": "📦"
    }

    for linha in linhas:
        linha_strip = linha.strip()

        if not linha_strip or "t.me/" in linha_strip or "@QueryBuscasBot" in linha_strip:
            continue

        if "⎯" in linha_strip:
            chave, valor = map(str.strip, linha_strip.split("⎯", 1))
            emoji = emojis.get(chave.upper(), "🔹")
            resultado.append(f"{emoji}{chave.upper()}: {valor}")
            continue

        if linha_strip.startswith("•"):
            resultado.append(f"   • {linha_strip[1:].strip()}")
            continue

        if linha_strip.startswith("- "):
            resultado.append(f"     - {linha_strip[2:].strip()}")
            continue

        if ':' in linha_strip:
            chave, valor = map(str.strip, linha_strip.split(':', 1))
            chave_upper = chave.upper()
            emoji = emojis.get(chave_upper, "🔹")
            if emoji:
                resultado.append(f"{emoji}{chave_upper}: {valor}")
            else:
                resultado.append(f"{chave_upper}: {valor}")
            continue

        resultado.append(linha_strip)

    return '\n'.join(resultado)

async def enviar_e_receber(comando, dado):
    msg_enviada = await client.send_message(grupo, f"{comando} {dado}", reply_to=topico_id)
    await asyncio.sleep(random.uniform(8, 12))
    me = await client.get_me()
    mensagens = await client.get_messages(grupo, limit=20)
    return await filtrar_resposta(mensagens, msg_enviada.id, me.id)

async def filtrar_resposta(mensagens, reply_id, my_id):
    for msg in mensagens:
        if msg.reply_to_msg_id == reply_id and msg.file and msg.file.name.endswith('.txt') and msg.sender_id != my_id:
            return await tratar_resposta(msg)
    for msg in mensagens:
        if msg.reply_to_msg_id == reply_id and msg.text and msg.sender_id != my_id:
            return await tratar_resposta(msg)
    console.print("[red]❌ Nenhuma resposta encontrada.")
    input("\nPressione ENTER para voltar ao menu...")

async def tratar_resposta(msg):
    if msg.file:
        path = await msg.download_media()
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            conteudo = ''.join(f.readlines())
            resposta_formatada = formatar_resposta(conteudo)
            console.print(Panel(resposta_formatada.strip(), title="Consulta Formatada", subtitle="KLORD VIP"))
            with open("buscas_log.txt", "a", encoding="utf-8") as log:
                log.write(f"\n[{datetime.now()}]\n{conteudo}\n")
        os.remove(path)
    elif msg.text:
        conteudo = msg.text
        resposta_formatada = formatar_resposta(conteudo)
        console.print(Panel(resposta_formatada.strip(), title="Consulta Formatada", subtitle="KLORD VIP"))

    # Clicar no botão apagar, se existir
    if msg.buttons:
        for row in msg.buttons:
            for button in row:
                if hasattr(button, 'text') and button.text.lower() == "apagar":
                    await msg.click(text=button.text)
                    break

    input("\nPressione ENTER para voltar ao menu...")

def gerar_pessoa():
    nome = fake.name()
    cpf = CPF().generate()
    email = fake.email()
    telefone = fake.phone_number()
    nascimento = fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%d/%m/%Y')
    endereco = fake.address().replace('\n', ', ')
    info = (f"Nome: {nome}\nCPF: {cpf}\nEmail: {email}\nTelefone: {telefone}\n"
            f"Data Nascimento: {nascimento}\nEndereço: {endereco}")
    console.print(Panel(info, title="Pessoa Gerada", subtitle="KLORD VIP"))
    with open("buscas_log.txt", "a", encoding="utf-8") as log:
        log.write(f"\n[{datetime.now()}] Pessoa Gerada:\n{info}\n")
    input("\nPressione ENTER para voltar ao menu...")

def gerar_gg():
    gg = fake.bothify(text='??####???##')
    console.print(f"[bold green]GG gerado: [bold yellow]{gg}")
    with open("buscas_log.txt", "a", encoding="utf-8") as log:
        log.write(f"\n[{datetime.now()}] GG Gerado: {gg}\n")
    input("\nPressione ENTER para voltar ao menu...")

@contextlib.contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

async def main():
    with suppress_stdout():  # suprime mensagens do Telethon
        await client.start(phone=telefone, code_callback=lambda: Prompt.ask("🔐 INSIRA O CÓDIGO:"))
    while True:
        mostrar_menu()
        opcao = Prompt.ask("[bold yellow]Escolha uma opção").strip()

        if opcao == "00":
            console.print("[red]Saindo...[/red]")
            await client.disconnect()
            break
        elif opcao in comandos:
            dado = Prompt.ask(f"[bold cyan]Digite o dado para {comandos[opcao][1:].upper()}").strip()
            await enviar_e_receber(comandos[opcao], dado)
        elif opcao == "98":
            gerar_pessoa()
        elif opcao == "99":
            gerar_gg()
        else:
            console.print("[red]Opção inválida.")
            input("\nPressione ENTER para continuar...")

if __name__ == "__main__":
    asyncio.run(main())
