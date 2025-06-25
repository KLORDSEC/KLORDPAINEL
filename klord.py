import asyncio, os, random, re
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from faker import Faker
from validate_docbr import CPF
from datetime import datetime

# ==== CONFIG ====
api_id = 24344843
api_hash = '810897451143f53c4a437765a6eae76c'
session_name = 'session'
grupo = '@DBSPUXADASVIP'
topico_id = None
telefone = "+5531987705212"

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

emoji_grupo_1 = {
    "CPF", "NOME", "SEXO", "NASCIMENTO", "NOME MÃE", "NOME PAI",
    "MUNICÍPIO DE NASCIMENTO", "RAÇA", "TIPO SANGÚINEO", "RG",
    "RENDA", "SCORE", "ESTADO CIVIL", "ÓBITO"
}

emoji_grupo_2 = {"STATUS NA RECEITA", "RECEBE INSS", "PIS", "NIS", "CNS"}
emoji_grupo_3 = {"CLASSE SOCIAL", "ESCOLARIDADE", "PROFISSÃO"}

emojis = {
    "👤": emoji_grupo_1,
    "📊": emoji_grupo_2,
    "📚": emoji_grupo_3
}

blocos = {
    "EMPRESAS": "🏢",
    "EMAILS": "✉️",
    "TELEFONES": "☎️",
    "BANCOS": "🏦",
    "EMPREGOS": "💼",
    "PARENTES": "👥",
    "VEICULOS": "🚗",
    "ENDERECOS": "🏡",
    "INTERESSES PESSOAIS": "📦"
}

def formatar_resposta(conteudo):
    linhas = conteudo.splitlines()
    resultado = []
    bloco_atual = ""

    for linha in linhas:
        linha = linha.strip()
        if not linha or "@" in linha or "http" in linha:
            continue

        if "⎯" in linha:
            chave, valor = map(str.strip, linha.split("⎯", 1))
            emoji = next((e for e, campos in emojis.items() if chave.upper() in campos), "📦")
            resultado.append(f"{emoji} {chave.upper()}: {valor}")
        elif any(linha.startswith(k + ":") for k in blocos):
            chave_bloco = linha.split(":")[0]
            bloco_atual = chave_bloco.upper()
            resultado.append(f"\n{blocos.get(bloco_atual, '📦')} {bloco_atual}:")
        elif linha.startswith("•"):
            resultado.append(f"• {linha[1:].strip()}")
        elif linha.startswith("-"):
            resultado.append(f"🔹 {linha[1:].strip()}")
        elif re.match(r"^[A-Z ]+: .*", linha):
            chave = linha.split(":")[0].strip()
            valor = ":".join(linha.split(":")[1:]).strip()
            emoji = next((e for e, campos in emojis.items() if chave.upper() in campos), "📦")
            resultado.append(f"{emoji} {chave.upper()}: {valor}")

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
        os.remove(path)
    else:
        conteudo = msg.text

    resposta_formatada = formatar_resposta(conteudo)
    console.print(Panel(resposta_formatada.strip(), title="Consulta KLORD", subtitle="KLORD VIP"))
    with open("buscas_log.txt", "a", encoding="utf-8") as log:
        log.write(f"\n[{datetime.now()}]\n{conteudo}\n")
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

async def main():
    await client.start(phone=telefone, code_callback=lambda: Prompt.ask("🔐 INSIRA O CÓDIGO:"))
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        menu = """
============ KLORD PAINEL ============

-- CONSULTAS:
[1] CPF
[2] RG
[3] NOME
[4] PLACA
[5] MÃE
[6] CNPJ
[7] CNS
[8] PIS
[9] PIX
[10] TELEFONE
[11] PAI
[12] TÍTULO
[13] NIS
[14] BIN

-- UTILIDADES:
[98] GERAR PESSOA
[99] GERAR GG

-- SISTEMA:
[00] SAIR
"""
        console.print(menu, style="bold cyan")
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
