from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from datetime import datetime
from api.routes import router
from src.database import init_db

console = Console()


@asynccontextmanager
async def lifespan(app: FastAPI):
    console.print("\n[bold magenta]" + "=" * 60 + "[/bold magenta]")
    console.print("[bold magenta]📚 Book Recommender System API[/bold magenta]".center(60))
    console.print("[bold magenta]" + "=" * 60 + "[/bold magenta]\n")

    startup_table = Table(show_header=False, box=None, padding=(0, 2))
    startup_table.add_row("[cyan]Version[/cyan]", "[bold yellow]2.0.0[/bold yellow]")
    startup_table.add_row("[cyan]Start Time[/cyan]",
                          f"[bold yellow]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/bold yellow]")
    startup_table.add_row("[cyan]Server[/cyan]", "[bold yellow]0.0.0.0:8000[/bold yellow]")
    console.print(startup_table)
    console.print()

    try:
        init_db()
        db_panel = Panel(
            "[bold green]✓ Database initialized successfully[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        console.print(db_panel)
    except Exception as e:
        db_panel = Panel(
            f"[bold red]✗ Database initialization failed: {e}[/bold red]",
            border_style="red",
            padding=(1, 2)
        )
        console.print(db_panel)

    console.print()

    endpoints_table = Table(title="🔗 Available Endpoints", show_header=False, box=None, padding=(0, 2))
    endpoints_table.add_row("[cyan]API Docs[/cyan]", "[bold green]http://localhost:8000/docs[/bold green]")
    endpoints_table.add_row("[cyan]ReDoc[/cyan]", "[bold green]http://localhost:8000/redoc[/bold green]")
    console.print(endpoints_table)

    console.print("\n[bold green]" + "=" * 60 + "[/bold green]")
    console.print("[bold green]✨ Server is ready to accept requests[/bold green]".center(60))
    console.print("[bold green]" + "=" * 60 + "[/bold green]\n")

    yield

    shutdown_panel = Panel(
        f"[bold yellow]🛑 Shutting down at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/bold yellow]",
        border_style="yellow",
        padding=(1, 2)
    )
    console.print("\n")
    console.print(shutdown_panel)
    console.print()


app = FastAPI(
    title="Book Recommender System API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    console.print("[bold cyan]🚀 Initializing server...[/bold cyan]\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
