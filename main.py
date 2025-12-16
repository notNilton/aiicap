#!/usr/bin/env python3
"""
AIICAP - Interface Principal
Interface CLI para gerenciar os serviços do projeto

Permite iniciar, parar e monitorar os módulos:
- Gerador de Imagens
- Corretor de Imagens
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    """Exibir cabeçalho"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}   AIICAP - AI Image Correction and Processing{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}\n")

def print_menu():
    """Exibir menu principal"""
    print(f"{Colors.BOLD}Escolha uma opção:{Colors.ENDC}\n")
    print(f"  {Colors.GREEN}1{Colors.ENDC} - Iniciar Gerador de Imagens")
    print(f"  {Colors.GREEN}2{Colors.ENDC} - Iniciar Corretor de Imagens")
    print(f"  {Colors.GREEN}3{Colors.ENDC} - Iniciar Ambos (Gerador + Corretor)")
    print(f"  {Colors.YELLOW}4{Colors.ENDC} - Ver Status dos Serviços")
    print(f"  {Colors.YELLOW}5{Colors.ENDC} - Ver Logs em Tempo Real")
    print(f"  {Colors.RED}6{Colors.ENDC} - Parar Todos os Serviços")
    print(f"  {Colors.CYAN}7{Colors.ENDC} - Configurações (.env)")
    print(f"  {Colors.CYAN}8{Colors.ENDC} - Estatísticas")
    print(f"  {Colors.CYAN}9{Colors.ENDC} - Executar Exemplo Completo")
    print(f"  {Colors.RED}0{Colors.ENDC} - Sair")
    print()

def get_service_status():
    """Verificar status dos serviços"""
    status = {
        'generator': {'running': False, 'pid': None},
        'corrector': {'running': False, 'pid': None}
    }
    
    # Verificar gerador
    gen_pid_file = Path("logs/generator.pid")
    if gen_pid_file.exists():
        try:
            pid = int(gen_pid_file.read_text().strip())
            # Verificar se processo está rodando
            os.kill(pid, 0)
            status['generator'] = {'running': True, 'pid': pid}
        except (ProcessLookupError, ValueError):
            pass
    
    # Verificar corretor
    corr_pid_file = Path("logs/corrector.pid")
    if corr_pid_file.exists():
        try:
            pid = int(corr_pid_file.read_text().strip())
            os.kill(pid, 0)
            status['corrector'] = {'running': True, 'pid': pid}
        except (ProcessLookupError, ValueError):
            pass
    
    return status

def start_service(service_name, script_name):
    """Iniciar um serviço"""
    os.makedirs("logs", exist_ok=True)
    
    print(f"{Colors.YELLOW}Iniciando {service_name}...{Colors.ENDC}")
    
    # Iniciar processo em background
    log_file = f"logs/{service_name.lower().replace(' ', '_')}.log"
    pid_file = f"logs/{service_name.lower().replace(' ', '_')}.pid"
    
    with open(log_file, 'w') as log:
        process = subprocess.Popen(
            [sys.executable, f"scripts/{script_name}"],
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
    
    # Salvar PID
    Path(pid_file).write_text(str(process.pid))
    
    time.sleep(1)
    
    # Verificar se iniciou corretamente
    try:
        os.kill(process.pid, 0)
        print(f"{Colors.GREEN}✓ {service_name} iniciado (PID: {process.pid}){Colors.ENDC}")
        print(f"  Log: {log_file}")
        return True
    except ProcessLookupError:
        print(f"{Colors.RED}✗ Falha ao iniciar {service_name}{Colors.ENDC}")
        return False

def stop_services():
    """Parar todos os serviços"""
    print(f"\n{Colors.YELLOW}Parando serviços...{Colors.ENDC}\n")
    
    stopped = 0
    status = get_service_status()
    
    for service, info in status.items():
        if info['running']:
            service_name = "Gerador" if service == 'generator' else "Corretor"
            try:
                os.kill(info['pid'], signal.SIGTERM)
                print(f"{Colors.GREEN}✓ {service_name} parado (PID: {info['pid']}){Colors.ENDC}")
                stopped += 1
                
                # Remover PID file
                pid_file = f"logs/{service}.pid"
                if Path(pid_file).exists():
                    Path(pid_file).unlink()
            except ProcessLookupError:
                print(f"{Colors.YELLOW}⚠ {service_name} já estava parado{Colors.ENDC}")
    
    if stopped == 0:
        print(f"{Colors.YELLOW}Nenhum serviço estava rodando{Colors.ENDC}")
    else:
        print(f"\n{Colors.GREEN}✓ {stopped} serviço(s) parado(s){Colors.ENDC}")

def show_status():
    """Mostrar status dos serviços"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Status dos Serviços{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
    
    # Verificar modo de storage
    use_db = "true"
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("USE_DATABASE="):
                use_db = line.split("=")[1].strip()
                break
    
    storage_mode = "PostgreSQL" if use_db.lower() == "true" else "File System"
    print(f"📦 Modo de Storage: {Colors.BOLD}{storage_mode}{Colors.ENDC}\n")
    
    status = get_service_status()
    
    # Gerador
    print(f"🎨 {Colors.BOLD}Gerador:{Colors.ENDC}")
    if status['generator']['running']:
        print(f"  Status: {Colors.GREEN}✓ Rodando{Colors.ENDC} (PID: {status['generator']['pid']})")
    else:
        print(f"  Status: {Colors.RED}✗ Parado{Colors.ENDC}")
    
    # Corretor
    print(f"\n🔧 {Colors.BOLD}Corretor:{Colors.ENDC}")
    if status['corrector']['running']:
        print(f"  Status: {Colors.GREEN}✓ Rodando{Colors.ENDC} (PID: {status['corrector']['pid']})")
    else:
        print(f"  Status: {Colors.RED}✗ Parado{Colors.ENDC}")
    
    print()

def show_logs():
    """Mostrar logs em tempo real"""
    print(f"\n{Colors.CYAN}Logs em Tempo Real{Colors.ENDC}")
    print(f"{Colors.YELLOW}Pressione Ctrl+C para voltar ao menu{Colors.ENDC}\n")
    
    time.sleep(1)
    
    # Usar tail -f para seguir os logs
    try:
        subprocess.run([
            "tail", "-f", 
            "logs/generator.log", 
            "logs/corrector.log"
        ])
    except KeyboardInterrupt:
        print(f"\n{Colors.GREEN}Voltando ao menu...{Colors.ENDC}")
    except FileNotFoundError:
        print(f"{Colors.RED}Arquivos de log não encontrados{Colors.ENDC}")
        time.sleep(2)

def show_config():
    """Mostrar e editar configurações"""
    print(f"\n{Colors.CYAN}Configurações (.env){Colors.ENDC}\n")
    
    env_file = Path(".env")
    if not env_file.exists():
        print(f"{Colors.YELLOW}.env não encontrado. Criando...{Colors.ENDC}")
        subprocess.run(["cp", ".env.example", ".env"])
    
    print(f"{Colors.BOLD}Arquivo: .env{Colors.ENDC}\n")
    
    # Exibir conteúdo
    content = env_file.read_text()
    for line in content.splitlines():
        if line.strip() and not line.startswith("#"):
            print(f"  {Colors.CYAN}{line}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Opções:{Colors.ENDC}")
    print("  1 - Editar com nano")
    print("  2 - Editar com vim")
    print("  0 - Voltar")
    
    choice = input(f"\n{Colors.BOLD}Escolha: {Colors.ENDC}").strip()
    
    if choice == "1":
        subprocess.run(["nano", ".env"])
    elif choice == "2":
        subprocess.run(["vim", ".env"])

def show_stats():
    """Mostrar estatísticas"""
    print(f"\n{Colors.CYAN}Estatísticas{Colors.ENDC}\n")
    
    # Executar script Python para pegar stats
    code = """
from modules.storage import get_storage
try:
    storage = get_storage()
    stats = storage.get_statistics()
    print(f"  Imagens geradas: {stats['total_generated_images']}")
    print(f"  Imagens corrigidas: {stats['total_corrected_images']}")
    print(f"  Total: {stats['total_images']}")
except Exception as e:
    print(f"  Erro: {e}")
"""
    
    subprocess.run([sys.executable, "-c", code])
    print()

def run_example():
    """Executar exemplo completo"""
    print(f"\n{Colors.CYAN}Executando exemplo completo...{Colors.ENDC}\n")
    subprocess.run([sys.executable, "scripts/exemplo_completo.py"])
    
    input(f"\n{Colors.YELLOW}Pressione Enter para voltar ao menu...{Colors.ENDC}")

def main():
    """Loop principal"""
    while True:
        print_header()
        
        # Mostrar status resumido
        status = get_service_status()
        running_services = sum(1 for s in status.values() if s['running'])
        
        if running_services > 0:
            print(f"{Colors.GREEN}✓ {running_services} serviço(s) rodando{Colors.ENDC}\n")
        
        print_menu()
        
        choice = input(f"{Colors.BOLD}Digite sua escolha: {Colors.ENDC}").strip()
        
        if choice == "1":
            start_service("generator", "run_generator.py")
            input(f"\n{Colors.YELLOW}Pressione Enter para continuar...{Colors.ENDC}")
        
        elif choice == "2":
            start_service("corrector", "run_corrector.py")
            input(f"\n{Colors.YELLOW}Pressione Enter para continuar...{Colors.ENDC}")
        
        elif choice == "3":
            print()
            start_service("generator", "run_generator.py")
            time.sleep(2)
            start_service("corrector", "run_corrector.py")
            input(f"\n{Colors.YELLOW}Pressione Enter para continuar...{Colors.ENDC}")
        
        elif choice == "4":
            show_status()
            input(f"\n{Colors.YELLOW}Pressione Enter para continuar...{Colors.ENDC}")
        
        elif choice == "5":
            show_logs()
        
        elif choice == "6":
            stop_services()
            input(f"\n{Colors.YELLOW}Pressione Enter para continuar...{Colors.ENDC}")
        
        elif choice == "7":
            show_config()
        
        elif choice == "8":
            show_stats()
            input(f"\n{Colors.YELLOW}Pressione Enter para continuar...{Colors.ENDC}")
        
        elif choice == "9":
            run_example()
        
        elif choice == "0":
            print(f"\n{Colors.CYAN}Até logo!{Colors.ENDC}\n")
            
            # Perguntar se quer parar serviços
            status = get_service_status()
            running = sum(1 for s in status.values() if s['running'])
            
            if running > 0:
                resp = input(f"{Colors.YELLOW}Há {running} serviço(s) rodando. Parar antes de sair? (s/N): {Colors.ENDC}").strip().lower()
                if resp == 's':
                    stop_services()
                    time.sleep(1)
            
            sys.exit(0)
        
        else:
            print(f"\n{Colors.RED}Opção inválida!{Colors.ENDC}")
            time.sleep(1)
        
        # Limpar tela (opcional)
        # os.system('clear' if os.name != 'nt' else 'cls')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrompido pelo usuário{Colors.ENDC}")
        print(f"{Colors.CYAN}Até logo!{Colors.ENDC}\n")
        sys.exit(0)