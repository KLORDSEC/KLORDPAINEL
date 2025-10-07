import asyncio, os, random, re
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from faker import Faker
from validate_docbr import CPF
from datetime import datetime
import requests 
import webbrowser 

# ==== CONFIG ====
api_id = 24344843
api_hash = '810897451143f53c4a437765a6eae76c'
session_name = 'session'
grupo = -1002890645155
topico_id = None
telefone = "+5515998519942"

# OBS: Não é mais necessário para o Litterbox, mas mantemos.
CATBOX_API_KEY = 'na' 

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
    "19": "/email",
    "20": "/fotorj",
    "21": "/fotoes",
    "22": "/fotosp",
    "23": "/fotoms"
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

# --- NOVO UPLOAD SERVICE (Litterbox.cat) ---
def upload_service(file_path):
    """
    Faz o upload do arquivo para o Litterbox.cat (irmão do Catbox, para arquivos temporários).
    É mais robusto para uploads anônimos. A expiração é de 72h.
    """
    console.print(f"[yellow]⏳ Tentando upload de {os.path.basename(file_path)} para Litterbox.cat...[/yellow]")
    url = "https://litterbox.catbox.moe/resources/internals/api.php"
    
    try:
        with open(file_path, 'rb') as f:
            files = {
                'fileToUpload': f 
            }
            data = {
                'reqtype': 'fileupload',
                'time': '72h', # Tempo de expiração máximo
                'userhash': '' # Litterbox não precisa de chave, mas é bom passar vazio
            }

            response = requests.post(url, data=data, files=files)
            response.raise_for_status() 
            
            # O Litterbox retorna a URL diretamente se for bem-sucedido
            if response.text.startswith("https://"):
                console.print("[green]✅ Upload concluído com sucesso![/green]")
                return response.text.strip()
            else:
                # Captura a resposta de falha da API
                console.print(f"[red]❌ Falha no upload do Litterbox. Resposta: {response.text}[/red]")
                return None
    except requests.exceptions.RequestException as e:
        # Erros de conexão ou 4xx/5xx
        console.print(f"[red]❌ Erro de conexão/requisição ao Litterbox: {e}[/red]")
        return None
    except Exception as e:
        console.print(f"[red]❌ Erro inesperado ao tentar subir: {e}[/red]")
        return None


async def enviar_e_receber(comando, dado):
    msg_enviada = await client.send_message(grupo, f"{comando} {dado}", reply_to=topico_id)
    await asyncio.sleep(random.uniform(8, 12))
    me = await client.get_me()
    mensagens = await client.get_messages(grupo, limit=30) 
    
    # Passa o comando para o filtro
    return await filtrar_resposta(mensagens, msg_enviada.id, me.id, msg_enviada.id, comando) 

# --- FUNÇÃO FILTRAR RESPOSTA (mantida, pois a lógica está correta) ---
async def filtrar_resposta(mensagens, reply_id, my_id, msg_enviada_id, comando):
    
    is_photo_command = comando in ["/fotorj", "/fotoes", "/fotosp", "/fotoms"]
    
    respostas = []
    
    # 1. Coletar respostas relevantes e limitá-las (1 para texto, 3 para foto)
    for msg in mensagens:
        if msg.reply_to_msg_id == reply_id and msg.sender_id != my_id:
            respostas.append(msg)
            
            if not is_photo_command and len(respostas) >= 1:
                 break
            if is_photo_command and len(respostas) >= 3:
                break
    
    if not respostas:
        console.print("[red]❌ Nenhuma resposta encontrada.[/red]")
        input("\nPressione ENTER para voltar ao menu...")
        return

    mensagem_para_tratar = respostas[0]
    
    # 2. Lógica de priorização de MÍDIA (SOMENTE PARA COMANDOS DE FOTO)
    if is_photo_command:
        for msg in respostas:
            # CHECA SE É UMA FOTO DIRETA (msg.photo)
            if msg.photo: 
                return await tratar_resposta(msg, msg_enviada_id)
            
            # Se for um documento, checa se o mime_type é de imagem
            if msg.document:
                is_document_media = getattr(msg.document.mime_type, 'startswith', lambda x: False)('image/')
                if is_document_media:
                    return await tratar_resposta(msg, msg_enviada_id) 
            
    # 3. Se não for comando de foto OU se for de foto mas nenhuma mídia foi encontrada nas 3,
    # processa a resposta mais recente (o texto ou o log .txt).
    return await tratar_resposta(mensagem_para_tratar, msg_enviada_id)


# --- FUNÇÃO TRATAR RESPOSTA REVISADA (usa upload_service) ---
async def tratar_resposta(msg, msg_enviada_id):
    upload_url = None
    file_path = None
    conteudo = None
    
    is_media_message = msg.photo or msg.document and getattr(msg.document.mime_type, 'startswith', lambda x: False)('image/')
    
    if msg.file:
        file_path = await msg.download_media()
        
        if is_media_message:
            # É uma foto/mídia: tenta o upload para o novo serviço
            upload_url = upload_service(file_path)
            # Define um conteúdo simples para o log
            conteudo = f"FOTO PROCESSADA: {os.path.basename(file_path)}"
            
        else:
            # Não é mídia (ex: .txt, .log): lê o conteúdo
            console.print(f"[yellow]⚠️ Arquivo não é mídia. Lendo o conteúdo como texto.[/yellow]")
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    conteudo = ''.join(f.readlines())
            except Exception as e:
                 console.print(f"[red]❌ Não foi possível ler o arquivo: {e}[/red]")
                 conteudo = f"Erro ao processar arquivo desconhecido: {file_path}"
        
        try:
            os.remove(file_path)
        except Exception as e:
            console.print(f"[red]❌ Erro ao remover arquivo temporário {file_path}: {e}[/red]")

    else:
        # Mensagem de texto simples
        conteudo = msg.text

    # 3. Exibe o resultado da consulta (texto ou log)
    if conteudo and not upload_url: 
        resposta_formatada = formatar_resposta(conteudo)
        console.print(Panel(resposta_formatada.strip(), title="CONSULTA KLORD", subtitle="KLORD VIP", border_style="red"))
        with open("buscas_log.txt", "a", encoding="utf-8") as log:
            log.write(f"\n[{datetime.now()}]\n{conteudo}\n")
    
    # 4. Abertura do URL se houver uma foto
    if upload_url:
        console.print(f"\n[bold magenta]🖼️ Link da Foto Litterbox:[/bold magenta] [underline]{upload_url}[/underline]")
        
        try:
            webbrowser.open(upload_url)
            console.print("[green]✅ Tentando abrir o link no navegador (Chrome/padrão)...[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️ Falha ao tentar abrir o navegador: {e}[/yellow]")

    # 5. Apaga as mensagens no Telegram
    try:
        await client.delete_messages(grupo, msg) 
        await client.delete_messages(grupo, msg_enviada_id)
        
        console.print("[green]✅ RETORNO NA BASE DE DADOS DE API e mensagens apagadas.[/green]")
    except Exception as e:
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
║             -- CONSULTA DE FOTO (DOCUMENTOS) --          ║
║  [20] FOTO RJ       [21] FOTO ES                         ║
║  [22] FOTO SP       [23] FOTO MS                         ║
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
        
