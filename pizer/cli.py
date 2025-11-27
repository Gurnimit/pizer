import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from .stream_reader import ZipStreamReader
from .file_parser import FileParser
from .inspector import FileInspector
from rich.prompt import Prompt
import os
import sys

app = typer.Typer(invoke_without_command=True)
console = Console()

def print_banner():
    banner = r"""
[bold cyan]
  _______
 |__   __|
 |  | |  |___  ___ _ __
 |  | |  |__  / / _ \ '__|
 |__| |__| / / |  __/ |
          /___| \___|_|
[/bold cyan]
[bold white]   CYBER DEFENCE & RECOVERY TOOL[/bold white]
    """
    rprint(Panel(banner, border_style="cyan", title="[bold green]πzer[/bold green]", subtitle="[italic]v1.0.1[/italic]", expand=False))

@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """
    πzer: A tool for inspecting and cleaning ZIP/RAR files.
    """
    if ctx.invoked_subcommand is None:
        print_banner()
        while True:
            console.print("\n[bold cyan]Select an option:[/bold cyan]")
            console.print("1. [green]Inspect File[/green]")
            console.print("2. [green]Recover Password (Dictionary)[/green]")
            console.print("3. [green]Recover Password (Brute Force)[/green]")
            console.print("4. [red]Exit[/red]")
            
            choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4"], default="1")
            
            if choice == "1":
                file_path = Prompt.ask("Enter path to ZIP/RAR file")
                # Remove quotes if user pasted path with quotes
                file_path = file_path.strip('"\'')
                inspect(file_path)
            elif choice == "2":
                recover()
            elif choice == "3":
                file_path = Prompt.ask("Enter path to ZIP file")
                file_path = file_path.strip('"\'')
                max_len = int(Prompt.ask("Max Length (0 for unlimited)", default="0"))
                recover_brute(file_path, max_length=max_len)
            elif choice == "4":
                console.print("[bold green]Goodbye![/bold green]")
                break
@app.command()
def recover():
    """
    Launch the password recovery tool (Dictionary Attack).
    """
    print_banner()
    from .recovery.runner import Initiate
    Initiate()

@app.command()
def recover_brute(
    zip_file: str = typer.Argument(..., help="Path to the zip file"),
    max_length: int = typer.Option(0, help="Maximum password length (0 for unlimited)"),
    use_lower: bool = typer.Option(True, help="Use lowercase letters"),
    use_upper: bool = typer.Option(True, help="Use uppercase letters"),
    use_digits: bool = typer.Option(True, help="Use digits"),
    use_symbols: bool = typer.Option(False, help="Use symbols")
):
    """
    Recover password using Brute Force attack.
    """
    print_banner()
    from .recovery.runner import ZipRip
    
    ripper = ZipRip()
    
    if not os.path.exists(zip_file):
        console.print(f"[bold red]Error:[/bold red] File not found: {zip_file}")
        raise typer.Exit(code=1)
        
    ripper.ZipFile = zip_file
    ripper.AttackMode = "bruteforce"
    ripper.BruteForceConfig = {
        "max_length": max_length,
        "use_lower": use_lower,
        "use_upper": use_upper,
        "use_digits": use_digits,
        "use_symbols": use_symbols
    }
    
    # Manually trigger the process since we set properties directly
    ripper.SetZipFileDirectory()
    ripper.SetPasswords()
    ripper.CrackPassword()
    ripper.DisplayResults()
@app.command()
def browse(archive_path: str, password: str = None):
    """
    List files in a ZIP archive using stream reader.
    """
    print_banner()
    try:
        reader = ZipStreamReader(archive_path, password=password)
        files = reader.list_files()
        
        table = Table(title=f"Contents of {os.path.basename(archive_path)}")
        table.add_column("Filename", style="cyan")
        
        for f in files:
            table.add_row(f)
            
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def inspect(file_path: str):
    """
    Inspect a ZIP or RAR file without extracting.
    """
    print_banner()
    try:
        files = FileInspector.inspect(file_path)
        
        table = Table(title=f"Inspection of {os.path.basename(file_path)}")
        table.add_column("Filename", style="cyan")
        table.add_column("Size (bytes)", justify="right", style="magenta")
        
        for name, size in files:
            table.add_row(name, str(size))
            
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def clean(archive_path: str):
    """
    Extract archive, remove junk files, and delete original archive.
    """
    print_banner()
    
    if not os.path.exists(archive_path):
        console.print(f"[bold red]Error:[/bold red] File not found: {archive_path}")
        return

    confirm = typer.confirm(f"This will extract {archive_path}, remove junk files, and DELETE the original archive. Continue?")
    if not confirm:
        console.print("Operation cancelled.")
        return

    try:
        from .cleaner import ArchiveCleaner
        with console.status("[bold green]Cleaning and extracting...[/bold green]"):
            output_dir = ArchiveCleaner.clean_and_extract(archive_path)
            
        console.print(f"[bold green]SUCCESS![/bold green]")
        console.print(f"Extracted and cleaned to: [bold cyan]{output_dir}[/bold cyan]")
        console.print("Original archive deleted.")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    app()