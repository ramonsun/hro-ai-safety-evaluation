import json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from classifier.classify import classify_log
from scorer.hro_scorer import score_log

console = Console()


@click.command()
@click.argument("path", type=click.Path(exists=True))
def analyze(path):
    """Classify AI agent logs and score near-misses using HRO framework."""
    path = Path(path)
    log_files = sorted(path.glob("*.json")) if path.is_dir() else [path]

    if not log_files:
        console.print("[red]No JSON log files found.[/red]")
        return

    for log_file in log_files:
        log = json.loads(log_file.read_text())
        console.print(f"\n[bold cyan]Analyzing:[/bold cyan] {log_file.name}")

        with console.status("Classifying..."):
            classification = classify_log(log)

        with console.status("Scoring near-miss..."):
            score = score_log(log, classification)

        console.print(Panel(
            f"[bold]Category:[/bold]   {classification['category']}\n"
            f"[bold]Confidence:[/bold] {classification['confidence']}\n"
            f"[bold]Reasoning:[/bold]  {classification['reasoning']}",
            title="RCM Classification", border_style="blue",
        ))

        table = Table(box=box.SIMPLE)
        table.add_column("Dimension", style="bold")
        table.add_column("Score", justify="center")
        table.add_row("Severity",       str(score["severity"]))
        table.add_row("Detectability",  str(score["detectability"]))
        table.add_row("Recoverability", str(score["recoverability"]))
        table.add_row("[bold]Near-Miss Score[/bold]",
                      f"[bold]{score['near_miss_score']}[/bold]")
        console.print(Panel(table, title="HRO Scores", border_style="yellow"))

        flags = ", ".join(score["hro_flags"]) or "none"
        console.print(Panel(
            f"[bold]HRO Flags:[/bold]       {flags}\n"
            f"[bold]Recommendation:[/bold]  {score['recommendation']}",
            title="HRO Analysis", border_style="red",
        ))


if __name__ == "__main__":
    analyze()
