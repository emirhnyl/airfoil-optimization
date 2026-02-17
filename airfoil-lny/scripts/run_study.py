from pathlib import Path
import typer
from airfoil_lny.core.optimization.study import run_study

app = typer.Typer(add_completion=False)

@app.command()
def main(config: str = typer.Option(..., help="Path to YAML config")):
    run_study(Path(config))

if __name__ == "__main__":
    app()
