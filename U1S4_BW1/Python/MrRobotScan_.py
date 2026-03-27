import socket
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.rule import Rule

console = Console()

PORTS_TO_SCAN = [20, 21, 22, 23, 25, 53, 80, 110, 111, 139, 143, 443, 445, 512, 513, 514, 1524, 3306, 8080]


# ======================
#       BANNER
# ======================
def banner():
    console.print(Rule("[bold green]BOOT SEQUENCE INITIATED[/bold green]"))

    ascii_art = r"""
 __  __      _____       _           _    _____                                 
|  \/  |    |  __ \     | |         | |  / ____|                                
| \  / |_ __| |__) |___ | |__   ___ | |_| (___   ___ __ _ _ __  _ __   ___ _ __ 
| |\/| | '__|  _  // _ \| '_ \ / _ \| __|\___ \ / __/ _` | '_ \| '_ \ / _ \ '__|
| |  | | |  | | \ \ (_) | |_) | (_) | |_ ____) | (_| (_| | | | | | | |  __/ |   
|_|  |_|_|  |_|  \_\___/|_.__/ \___/ \__|_____/ \___\__,_|_| |_|_| |_|\___|_|   
"""

    console.print(Panel.fit(
        f"[bold red]{ascii_art}[/bold red]\n"
        "[bold magenta]MR.ROBOT SCANNER[/bold magenta]\n"
        "[cyan]HTTP • PORT SCAN • SOCKET CAPTURE[/cyan]",
        border_style="red"
    ))

    console.print(Rule("[bold green]READY[/bold green]"))



# ======================
#       INPUT IP
# ======================
def chiedi_ip():
    while True:
        target_ip = console.input("\n[bold cyan]TARGET IP >> [/bold cyan]").strip()
        if target_ip:
            return target_ip
        console.print("[bold red]Invalid IP. Retry.[/bold red]")


# ======================
#       MENU
# ======================
def menu():
    console.print(Panel.fit(
        "[bold green]1[/bold green] › HTTP Test\n"
        "[bold green]2[/bold green] › Port Scan (Multithread)\n"
        "[bold green]3[/bold green] › Socket Capture\n"
        "[bold green]4[/bold green] › Run All\n"
        "[bold green]5[/bold green] › Exit",
        title="[bold magenta]MAIN MENU[/bold magenta]",
        border_style="magenta"
    ))
    return console.input("[bold cyan]SELECT >> [/bold cyan]").strip()


# ======================
#       HTTP TEST
# ======================
def test_http(target_ip):
    risultati = []
    base_url = f"http://{target_ip}"

    console.print(Rule("[bold green]HTTP MODULE[/bold green]"))

    metodi = [
        ("GET", None),
        ("POST", {"nome": "test", "tipo": "post"}),
        ("PUT", {"nome": "test", "tipo": "put"}),
        ("DELETE", None),
    ]

    for metodo, data in metodi:
        try:
            if metodo == "GET":
                response = requests.get(base_url, timeout=5)
            elif metodo == "POST":
                response = requests.post(base_url, data=data, timeout=5)
            elif metodo == "PUT":
                response = requests.put(base_url, data=data, timeout=5)
            elif metodo == "DELETE":
                response = requests.delete(base_url, timeout=5)

            console.print(f"[bold green]{metodo}[/bold green] → [cyan]{response.status_code}[/cyan]")

            risultati.append({
                "metodo": metodo,
                "status_code": response.status_code,
                "risposta": response.text[:300]
            })

        except Exception as e:
            console.print(f"[bold red]{metodo}[/bold red] → ERROR ({e})")
            risultati.append({
                "metodo": metodo,
                "status_code": "ERROR",
                "risposta": str(e)
            })

    return risultati


# ======================
#   MULTITHREAD PORT SCAN
# ======================
def scan_single_port(target_ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    result = s.connect_ex((target_ip, port))
    s.close()

    if result == 0:
        return port, "OPEN"
    else:
        return port, "CLOSED"


def port_scan(target_ip):
    console.print(Rule(f"[bold green]MULTITHREAD PORT SCAN — {target_ip}[/bold green]"))

    table = Table(title="Port Scan Results", border_style="green")
    table.add_column("Port", justify="center")
    table.add_column("State", justify="center")

    risultati = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(scan_single_port, target_ip, port): port for port in PORTS_TO_SCAN}

        for future in as_completed(futures):
            port, stato = future.result()
            color = "[bold green]OPEN[/bold green]" if stato == "OPEN" else "[bold red]CLOSED[/bold red]"
            table.add_row(str(port), color)
            risultati.append({"porta": port, "stato": stato})

    console.print(table)
    return risultati


# ======================
#       SOCKET CAPTURE
# ======================
def cattura_socket(target_ip):
    console.print(Rule("[bold green]SOCKET CAPTURE[/bold green]"))

    risultati = {
        "porta_usata": 80,
        "esito": "",
        "risposta": ""
    }

    target_port = 80

    richiesta = (
        "GET / HTTP/1.1\r\n"
        f"Host: {target_ip}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)

    try:
        console.print(f"[cyan]Connecting to {target_ip}:{target_port}...[/cyan]")
        s.connect((target_ip, target_port))
        console.print("[bold green]Connected.[/bold green]")

        s.send(richiesta.encode())
        console.print("[yellow]Payload sent.[/yellow]")

        risposta = b""

        while True:
            try:
                dati = s.recv(1024)
                if not dati:
                    break
                risposta += dati
            except socket.timeout:
                break

        header = risposta.decode(errors="ignore").split("\r\n\r\n", 1)[0]

        console.print(Panel(header, title="HTTP HEADER", border_style="green"))

        risultati["esito"] = "SUCCESS"
        risultati["risposta"] = header

    except Exception as e:
        console.print(f"[bold red]ERROR: {e}[/bold red]")
        risultati["esito"] = "ERROR"
        risultati["risposta"] = str(e)

    finally:
        s.close()
        console.print("[cyan]Socket closed.[/cyan]")

    return risultati


# ======================
#       REPORT
# ======================
def salva_report(target_ip, http=None, porte=None, socket_data=None):
    nome_file = "theta_report.txt"

    with open(nome_file, "w", encoding="utf-8") as f:
        f.write("THETA NETWORK ANALYSIS REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Target: {target_ip}\n\n")

        if http:
            f.write("HTTP TEST\n")
            f.write("-" * 30 + "\n")
            for r in http:
                f.write(f"{r['metodo']} → {r['status_code']}\n")

        if porte:
            f.write("\nPORT SCAN\n")
            f.write("-" * 30 + "\n")
            for r in porte:
                f.write(f"{r['porta']} → {r['stato']}\n")

        if socket_data:
            f.write("\nSOCKET CAPTURE\n")
            f.write("-" * 30 + "\n")
            f.write(socket_data["risposta"] + "\n")

    console.print(f"[bold green]Report saved as {nome_file}[/bold green]")


# ======================
#       MAIN
# ======================
def main():
    banner()
    target_ip = chiedi_ip()

    while True:
        scelta = menu()

        if scelta == "1":
            risultati_http = test_http(target_ip)

        elif scelta == "2":
            risultati_porte = port_scan(target_ip)

        elif scelta == "3":
            risultati_socket = cattura_socket(target_ip)

        elif scelta == "4":
            risultati_http = test_http(target_ip)
            risultati_porte = port_scan(target_ip)
            risultati_socket = cattura_socket(target_ip)

        elif scelta == "5":
            console.print("[bold magenta]Session terminated.[/bold magenta]")
            break

        else:
            console.print("[bold red]Invalid selection.[/bold red]")
            continue

        salva = console.input("\n[bold cyan]Save report? (y/n) >> [/bold cyan]").strip().lower()
        if salva == "y":
            salva_report(
                target_ip,
                http=locals().get("risultati_http"),
                porte=locals().get("risultati_porte"),
                socket_data=locals().get("risultati_socket")
            )


if __name__ == "__main__":
    main()
