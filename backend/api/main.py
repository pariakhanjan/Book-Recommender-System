from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from rich.console import Console
from api.routes import router
from src.database import init_db

console = Console()


@asynccontextmanager
async def lifespan(app: FastAPI):
    console.print("\n[bold magenta]" + "=" * 60 + "[/bold magenta]")
    console.print("[bold magenta]  Starting Book Recommender API...[/bold magenta]".center(60))
    console.print("[bold magenta]" + "=" * 60 + "[/bold magenta]\n")

    try:
        init_db()
        console.print("[bold green]Database initialized successfully[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Database initialization failed: {e}[/bold red]")

    yield

    console.print("\n[bold yellow]Shutting down Book Recommender API...[/bold yellow]\n")


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

    console.print("[bold cyan]Server starting on http://0.0.0.0:8000[/bold cyan]")
    console.print("[bold green]API Docs available at: http://localhost:8000/docs[/bold green]\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
