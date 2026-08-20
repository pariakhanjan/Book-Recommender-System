from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
import logging

custom_theme = Theme({
    "info": "bold cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "success": "bold green",
    "debug": "dim white",
    "critical": "bold magenta",
})

console = Console(theme=custom_theme)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        logger.handlers.clear()

    rich_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=False,
        markup=True
    )

    formatter = logging.Formatter(
        "[bold blue]%(asctime)s[/] - [bold %(name)s] - [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    rich_handler.setFormatter(formatter)

    logger.addHandler(rich_handler)
    return logger


def print_success(message: str):
    console.print(f"[bold green]✅ {message}[/]")


def print_error(message: str):
    console.print(f"[bold red]❌ {message}[/]")


def print_warning(message: str):
    console.print(f"[bold yellow]⚠️  {message}[/]")


def print_info(message: str):
    console.print(f"[bold cyan]ℹ️  {message}[/]")


def print_header(message: str):
    console.print(f"\n[bold magenta]{'=' * 60}[/]")
    console.print(f"[bold magenta]{message.center(60)}[/]")
    console.print(f"[bold magenta]{'=' * 60}[/]\n")
