import sys
import time
import os
import psutil
import socket
import requests
from rich.live import Live
from rich.table import Table
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns

from core.process_monitor import get_top_processes
from core.network_monitor import get_open_connections
from core.disk_monitor import get_disk_usage
from core.system_info import get_system_info
from core.logger import log_summary, log_cpu, log_memory, log_network

console = Console()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_cpu_monitor(live=False, cpu_threshold=50.0, filter_term=None):
    try:
        with Live(refresh_per_second=1) as live_display:
            while True:
                table = Table(title="Top CPU-consuming processes", box=box.MINIMAL_DOUBLE_HEAD)
                table.add_column("PID", style="cyan", justify="right")
                table.add_column("Process Name", style="magenta")
                table.add_column("CPU %", style="green", justify="right")
                table.add_column("Memory %", style="yellow", justify="right")

                top_cpu = get_top_processes(by="cpu", limit=20)
                high_cpu_procs = []

                if filter_term:
                    top_cpu = [p for p in top_cpu if filter_term.lower() in p['name'].lower() or filter_term == str(p['pid'])]

                for proc in top_cpu[:5]:
                    cpu_percent = proc['cpu_percent']
                    cpu_str = f"{cpu_percent:.1f}%"
                    if cpu_percent > cpu_threshold:
                        cpu_str = f"[bold red blink]{cpu_str}[/bold red blink]"
                        high_cpu_procs.append(proc)

                    table.add_row(
                        str(proc['pid']),
                        proc['name'][:30],
                        cpu_str,
                        f"{proc['memory_percent']:.1f}%"
                    )

                live_display.update(table)

                if high_cpu_procs:
                    alert_msg = "[bold red blink]⚠️ High CPU Usage Alert:[/bold red blink]\n"
                    for proc in high_cpu_procs:
                        alert_msg += f" - {proc['name']} (PID {proc['pid']}) at {proc['cpu_percent']:.1f}% CPU\n"
                    console.print(alert_msg)

                if not live:
                    break
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting CPU monitor...")

def run_network_monitor(live=False):
    try:
        with Live(refresh_per_second=1) as live_display:
            while True:
                table = Table(title="Open network connections (max 10)", box=box.MINIMAL_DOUBLE_HEAD)
                table.add_column("Local Address", style="cyan", no_wrap=True)
                table.add_column("Remote Address", style="magenta", no_wrap=True)
                table.add_column("Status", style="green")
                table.add_column("Process (PID)", style="yellow")

                connections = get_open_connections(limit=10)
                for conn in connections:
                    laddr = str(conn['laddr']) if conn['laddr'] else "—"
                    raddr = str(conn['raddr']) if conn['raddr'] else "—"
                    status = conn['status']
                    proc = f"{conn['process']} ({conn['pid']})"
                    table.add_row(laddr, raddr, status, proc)

                live_display.update(table)
                if not live:
                    break
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting network monitor...")

def run_memory_monitor(live=False, mem_threshold=50.0):
    try:
        with Live(refresh_per_second=1) as live_display:
            while True:
                table = Table(title="Top 5 Memory-consuming processes", box=box.MINIMAL_DOUBLE_HEAD)
                table.add_column("PID", style="cyan", justify="right")
                table.add_column("Process Name", style="magenta")
                table.add_column("CPU %", style="green", justify="right")
                table.add_column("Memory %", style="yellow", justify="right")

                top_mem = get_top_processes(by="memory", limit=5)
                high_mem_procs = []

                for proc in top_mem:
                    mem_percent = proc['memory_percent']
                    mem_str = f"{mem_percent:.1f}%"
                    if mem_percent > mem_threshold:
                        mem_str = f"[bold red]{mem_str}[/bold red]"
                        high_mem_procs.append(proc)

                    table.add_row(
                        str(proc['pid']),
                        proc['name'][:30],
                        f"{proc['cpu_percent']:.1f}%",
                        mem_str
                    )

                live_display.update(table)

                if high_mem_procs:
                    alert_msg = "[bold red]⚠️ High Memory Usage Alert:[/bold red]\n"
                    for proc in high_mem_procs:
                        alert_msg += f" - {proc['name']} (PID {proc['pid']}) at {proc['memory_percent']:.1f}% Memory\n"
                    console.print(alert_msg)

                if not live:
                    break
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting memory monitor...")

def run_disk_monitor(live=False):
    try:
        with Live(refresh_per_second=1) as live_display:
            while True:
                table = Table(title="Disk Usage", box=box.MINIMAL_DOUBLE_HEAD)
                table.add_column("Device", style="cyan")
                table.add_column("Mountpoint", style="magenta")
                table.add_column("FS Type", style="green")
                table.add_column("Total (GB)", justify="right")
                table.add_column("Used (GB)", justify="right")
                table.add_column("Free (GB)", justify="right")
                table.add_column("Usage %", justify="right")

                disks = get_disk_usage()
                for disk in disks:
                    total_gb = disk['total'] / (1024 ** 3)
                    used_gb = disk['used'] / (1024 ** 3)
                    free_gb = disk['free'] / (1024 ** 3)
                    percent = disk['percent']
                    table.add_row(
                        disk['device'],
                        disk['mountpoint'],
                        disk['fstype'],
                        f"{total_gb:.2f}",
                        f"{used_gb:.2f}",
                        f"{free_gb:.2f}",
                        f"{percent:.1f}%",
                    )

                live_display.update(table)

                if not live:
                    break
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting disk monitor...")

def log_disk():
    from datetime import datetime
    disks = get_disk_usage()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"logs/disk_{timestamp}.txt"
    os.makedirs("logs", exist_ok=True)

    with open(filename, "w") as f:
        f.write("Disk Usage Report\n\n")
        for disk in disks:
            total_gb = disk['total'] / (1024 ** 3)
            used_gb = disk['used'] / (1024 ** 3)
            free_gb = disk['free'] / (1024 ** 3)
            f.write(f"Device: {disk['device']}\n")
            f.write(f"Mountpoint: {disk['mountpoint']}\n")
            f.write(f"File System: {disk['fstype']}\n")
            f.write(f"Total: {total_gb:.2f} GB\n")
            f.write(f"Used: {used_gb:.2f} GB\n")
            f.write(f"Free: {free_gb:.2f} GB\n")
            f.write(f"Usage: {disk['percent']:.1f}%\n")
            f.write("-" * 30 + "\n")

    print(f"✅ Disk usage saved to {filename}")

def run_system_summary():
    info = get_system_info()
    table = Table(title="🖥️ System Summary", box=box.SIMPLE_HEAVY)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    for key, value in info.items():
        table.add_row(key, str(value))

    console.print(table)

def kill_process(pid):
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        proc.wait(timeout=3)
        console.print(f"[green]✅ Process {pid} terminated successfully.[/green]")
    except psutil.NoSuchProcess:
        console.print(f"[red]❌ No process found with PID {pid}.[/red]")
    except psutil.AccessDenied:
        console.print(f"[red]❌ Permission denied to terminate PID {pid}.[/red]")
    except psutil.TimeoutExpired:
        console.print(f"[yellow]⚠️ Process {pid} did not terminate in time. Trying kill...[/yellow]")
        try:
            proc.kill()
            console.print(f"[green]✅ Process {pid} killed successfully.[/green]")
        except Exception as e:
            console.print(f"[red]❌ Failed to kill process {pid}: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error terminating process {pid}: {e}[/red]")

def search_process(term):
    procs = get_top_processes(by="cpu", limit=100)
    matches = [p for p in procs if term.lower() in p['name'].lower() or term == str(p['pid'])]
    if not matches:
        print(f"No processes found matching '{term}'")
        return

    table = Table(title=f"Search results for '{term}'", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("PID", style="cyan", justify="right")
    table.add_column("Process Name", style="magenta")
    table.add_column("CPU %", style="green", justify="right")
    table.add_column("Memory %", style="yellow", justify="right")

    for proc in matches:
        table.add_row(str(proc['pid']), proc['name'][:30], f"{proc['cpu_percent']:.1f}%", f"{proc['memory_percent']:.1f}%")

    console.print(table)

def get_ip_info():
    try:
        ip = requests.get('https://api.ipify.org').text
        hostname = socket.gethostname()
        return f"{hostname}\nExternal IP: {ip}"
    except:
        return "IP info unavailable"

def run_all_monitors(live=False):
    try:
        with Live(refresh_per_second=1, screen=True) as live_display:
            while True:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_panel = Panel(f"[bold green]{cpu_percent}%[/bold green]", title="CPU Usage", border_style="green")

                mem = psutil.virtual_memory()
                mem_usage = f"{mem.percent}% of {mem.total // (1024 ** 3)} GB"
                mem_panel = Panel(f"[bold magenta]{mem_usage}[/bold magenta]", title="Memory Usage", border_style="magenta")

                disks = get_disk_usage()
                if disks:
                    d = disks[0]
                    disk_info = f"{d['percent']}% used on {d['mountpoint']}"
                else:
                    disk_info = "No disk data"
                disk_panel = Panel(f"[bold yellow]{disk_info}[/bold yellow]", title="Disk Usage", border_style="yellow")

                conns = get_open_connections(limit=3)
                conn_info = "\n".join(f"{c['laddr']} -> {c['raddr']} ({c['status']})" for c in conns) if conns else "No connections"
                net_panel = Panel(conn_info, title="Network Connections", border_style="cyan")

                layout = Columns([cpu_panel, mem_panel, disk_panel, net_panel])
                live_display.update(layout)

                if not live:
                    break
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting all-monitor view...")

def main():
    print("=== Smart Terminal Monitor CLI ===")
    print("Commands: monitor cpu [--live] [--filter <term>] | monitor net [--live] | monitor mem [--live] | monitor disk [--live] | kill <PID> | search <term> | exit")

    try:
        while True:
            try:
                cmd = input(">> ").strip()
                lower_cmd = cmd.lower()

                if lower_cmd.startswith("monitor cpu"):
                    live = "--live" in lower_cmd
                    filter_term = None
                    if "--filter" in lower_cmd:
                        parts = cmd.split("--filter", 1)
                        if len(parts) > 1 and parts[1].strip():
                            filter_term = parts[1].strip()
                        else:
                            print("⚠️  Please provide a filter term after '--filter'")
                            continue
                    run_cpu_monitor(live=live, filter_term=filter_term)

                elif lower_cmd.startswith("monitor net"):
                    run_network_monitor(live="--live" in lower_cmd)

                elif lower_cmd.startswith("monitor mem"):
                    run_memory_monitor(live="--live" in lower_cmd)

                elif lower_cmd.startswith("monitor disk"):
                    run_disk_monitor(live="--live" in lower_cmd)

                elif lower_cmd.startswith("monitor summary"):
                    run_system_summary()

                elif lower_cmd == "log disk":
                    log_disk()

                elif lower_cmd == "log summary":
                    print(f"✅ Summary saved to {log_summary()}")

                elif lower_cmd == "log cpu":
                    print(f"✅ CPU usage saved to {log_cpu()}")

                elif lower_cmd == "log mem":
                    print(f"✅ Memory usage saved to {log_memory()}")

                elif lower_cmd == "log net":
                    print(f"✅ Network connections saved to {log_network()}")

                elif lower_cmd.startswith("kill "):
                    parts = cmd.split()
                    if len(parts) == 2 and parts[1].isdigit():
                        kill_process(int(parts[1]))
                    else:
                        print("Usage: kill <PID>")

                elif lower_cmd.startswith("search "):
                    parts = cmd.split(" ", 1)
                    if len(parts) == 2 and parts[1].strip():
                        search_process(parts[1].strip())
                    else:
                        print("⚠️  Please provide a search term.")

                elif lower_cmd == "exit":
                    print("Goodbye!")
                    break

                elif lower_cmd.startswith("monitor all"):
                    run_all_monitors(live="--live" in cmd)

                else:
                    print("Unknown command. Try again.")

            except EOFError:
                print("\nInput ended. Exiting...")
                break

    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Exiting...")

if __name__ == "__main__":
    main()
