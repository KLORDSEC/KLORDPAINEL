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
grupo = -1002890645155
topico_id = None
telefone = "+5515998519942"

client = TelegramClient(session_name, api_id, api_hash)
console = Console()
fake = Faker('pt_BR')

comandos = {
    "1": "/cpf",       "2": "/rg",         "3": "/nome",
    "4": "/placa",     "5": "/mae",        "6": "/cnpj",
    "7": "/cns",       "8": "/pis",        "9": "/pix",
    "10": "/telefone", "11": "/pai",       "12": "/titulo",
    "13": "/nis",      "14": "/bin",       "15": "/chassi",
    "16": "/motor",    "17": "/renavam",   "18": "/cep",
    "19": "/email"
}

emojis = {
    "👤": {
        "CPF", "NOME", "SEXO", "NASCIMENTO", "NOME MÃE", "NOME PAI",
        "MUNICÍPIO DE NASCIMENTO", "RAÇA", "TIPO SANGÚINEO", "RG",
        "RENDA", "SCORE", "ESTADO CIVIL", "ÓBITO"
    },
    "📊": {
        "STATUS NA RECEITA", "RECEBE INSS", "PIS", "NIS", "CNS"
    },
    "📚": {
        "CLASSE SOCIAL", "ESCOLARIDADE", "PROFISSÃO"
    }
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
    # msg_enviada agora é importante e precisa ser repassada.
    msg_enviada = await client.send_message(grupo, f"{comando} {dado}", reply_to=topico_id)
    await asyncio.sleep(random.uniform(8, 12))
    me = await client.get_me()
    mensagens = await client.get_messages(grupo, limit=20)
    
    # Repassa a ID da mensagem enviada para a próxima função
    return await filtrar_resposta(mensagens, msg_enviada.id, me.id, msg_enviada.id) 

async def filtrar_resposta(mensagens, reply_id, my_id, msg_enviada_id): # Adiciona msg_enviada_id aqui
    for msg in mensagens:
        if msg.reply_to_msg_id == reply_id and (msg.file or msg.text) and msg.sender_id != my_id:
            # Repassa a mensagem de resposta (msg) E a ID da mensagem enviada (msg_enviada_id)
            return await tratar_resposta(msg, msg_enviada_id) 
            
    console.print("[red]❌ Nenhuma resposta encontrada.")
    input("\nPressione ENTER para voltar ao menu...")

async def tratar_resposta(msg, msg_enviada_id): # Adiciona msg_enviada_id aqui
    # 1. Processa o conteúdo da mensagem (como antes)
    if msg.file:
        path = await msg.download_media()
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            conteudo = ''.join(f.readlines())
        os.remove(path)
    else:
        conteudo = msg.text

    # 2. Formata e exibe a resposta (como antes)
    resposta_formatada = formatar_resposta(conteudo)
    console.print(Panel(resposta_formatada.strip(), title="CONSULTA KLORD", subtitle="KLORD VIP", border_style="red"))
    with open("buscas_log.txt", "a", encoding="utf-8") as log:
        log.write(f"\n[{datetime.now()}]\n{conteudo}\n")
    
    # 3. APAGA A MENSAGEM DE RESPOSTA E A MENSAGEM ENVIADA (ALTERAÇÃO PRINCIPAL)
    try:
        # Apaga a mensagem de resposta
        await client.delete_messages(grupo, msg) 
        # Apaga a sua mensagem de comando (/cpf, /cnpj, etc.)
        await client.delete_messages(grupo, msg_enviada_id)
        
        console.print("[green]✅ RETORNO NA BASE DE DADOS DE API.[/green]")
    except Exception as e:
        # É bom ter um tratamento de erro caso não tenha permissão
        console.print(f"[yellow]⚠️ TIVEMOS ALGUM PROBLEMA DURANTE O PROCESSO DE TRANSFERÊNCIA. Erro: {e}[/yellow]")

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

        ascii_art = """
             ________________________________________________
            /                                                \\
           |    _________________________________________     |
           |   |                                         |    |
           |   |  C:\\> _                                 |    |
           |   |                                         |    |
           |   |                                         |    |
           |   |                                         |    |
           |   |_________________________________________|    |
           |                                                  |
            \\_________________________________________________/
                   \\___________________________________/
                ___________________________________________
             _-'    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.  --- `-_
          _-'.-.-. .---.-.-.-.-.-.-.-.-.-.-.-.-.-.-.--.  .-.-.`-_
       _-'.-.-.-. .---.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-`__`. .-.-.-.`-_
    _-'.-.-.-.-. .-----.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-----. .-.-.-.-.`-_
 _-'.-.-.-.-.-. .---.-. .-------------------------. .-.---. .---.-.-.-.`-_
:-------------------------------------------------------------------------:
`---._.-------------------------------------------------------------._.---'
                              -KLORD MALWARE-
        """

        menu = f"""
╔══════════════════════[ KLORDPAINEL ]══════════════════════╗
║                                                          ║
║  [01] CPF           [02] RG          [03] NOME           ║
║  [04] PLACA         [05] MÃE         [06] CNPJ           ║
║  [07] CNS           [08] PIS         [09] PIX            ║
║  [10] TELEFONE      [11] PAI         [12] TÍTULO         ║
║  [13] NIS           [14] BIN         [15] CHASSI         ║
║  [16] MOTOR         [17] RENAVAM     [18] CEP (VIZINHOS) ║
║  [19] EMAIL                                              ║
║                                                          ║
║  [98] GERAR PESSOA       [99] GERAR GG                   ║
║  [00] SAIR                                               ║
╚══════════════════════════════════════════════════════════╝
"""
        console.print(ascii_art, style="bold red")
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