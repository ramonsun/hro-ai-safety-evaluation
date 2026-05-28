import json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from classifier.classify import classify_log
from scorer.hro_scorer import score_log
from reports.exporter import export as export_results
from reports.session_analysis import analyze_session
from generator.generate import generate_logs

console = Console()


def _analyze_file(log_file: Path) -> dict:
    log = json.loads(log_file.read_text())
    console.print(f"\n[bold cyan]Analyzing:[/bold cyan] {log_file.name}")

    with console.status("Classifying..."):
        classification = classify_log(log)

    if classification.get("source") == "prefilter":
        console.print(f"[bold magenta][prefilter][/bold magenta] Rule-based match → "
                      f"{classification['category']} (LLM skipped)")

    with console.status("Scoring near-miss..."):
        score = score_log(log, classification)

    console.print(Panel(
        f"[bold]Category:[/bold]   {classification['category']}\n"
        f"[bold]Confidence:[/bold] {classification['confidence']}\n"
        f"[bold]Reasoning:[/bold]  {classification['reasoning']}",
        title="RCM Classification", border_style="blue",
    ))

    dim_table = Table(box=box.SIMPLE)
    dim_table.add_column("Dimension", style="bold")
    dim_table.add_column("Score", justify="center")
    dim_table.add_row("Severity",      str(score["severity"]))
    dim_table.add_row("Detectability", str(score["detectability"]))
    sig = score.get("hro_signal_strength", 0)
    sig_color = "red" if sig >= 7 else "yellow" if sig >= 4 else "green"
    dim_table.add_row("[bold]HRO Signal Strength[/bold]",
                      f"[bold][{sig_color}]{sig}[/{sig_color}][/bold]")
    console.print(Panel(dim_table, title="HRO Scores", border_style="yellow"))

    flags = ", ".join(score["hro_flags"]) or "none"
    console.print(Panel(
        f"[bold]HRO Flags:[/bold]       {flags}\n"
        f"[bold]Recommendation:[/bold]  {score['recommendation']}",
        title="HRO Analysis", border_style="red",
    ))

    return {**classification, **score}


def _print_summary(results: list[dict]) -> None:
    table = Table(title="Summary — All Logs", box=box.ROUNDED)
    table.add_column("Log ID", style="bold")
    table.add_column("Category")
    table.add_column("Confidence")
    table.add_column("Near-Miss", justify="center")
    table.add_column("Signal", justify="center")
    table.add_column("HRO Flags")

    for r in results:
        sig = r.get("hro_signal_strength", 0)
        sig_color = "red" if sig >= 7 else "yellow" if sig >= 4 else "green"
        table.add_row(
            r.get("log_id", "?"),
            r.get("category", "?"),
            r.get("confidence", "?"),
            "yes" if r.get("is_near_miss") else "no",
            f"[{sig_color}]{sig}[/{sig_color}]",
            ", ".join(r.get("hro_flags", [])) or "none",
        )

    console.print("\n", table)


def _print_session(summary: dict) -> None:
    table = Table(title="Session Analysis", box=box.ROUNDED)
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Total logs", str(summary["total_logs"]))
    table.add_row("Near-misses", str(summary["near_miss_count"]))
    table.add_row("Near-miss rate (per 100)", str(summary["near_miss_rate_per_100"]))
    table.add_row("Top failure mode", summary.get("top_failure_mode") or "—")
    table.add_row("Avg Signal Strength", str(summary["avg_rpn"]))
    table.add_row("Max Signal Strength", str(summary["max_rpn"]))
    console.print("\n", table)

    dist = summary.get("mode_distribution", {})
    if dist:
        d_table = Table(title="Mode Distribution", box=box.SIMPLE)
        d_table.add_column("Mode")
        d_table.add_column("Count", justify="center")
        for mode, count in sorted(dist.items(), key=lambda x: -x[1]):
            d_table.add_row(mode, str(count))
        console.print(d_table)


@click.group()
def cli():
    """HRO AI Safety Evaluation — classify and score AI agent logs."""


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--export", "fmt", type=click.Choice(["json", "csv"]),
              default=None, help="Export results to reports/")
@click.option("--session", is_flag=True,
              help="Print session-level analysis and export as JSON to reports/")
def analyze(path, fmt, session):
    """Classify agent logs and score near-misses."""
    path = Path(path)
    log_files = sorted(path.glob("*.json")) if path.is_dir() else [path]

    if not log_files:
        console.print("[red]No JSON log files found.[/red]")
        return

    results = [_analyze_file(f) for f in log_files]

    if len(results) > 1:
        _print_summary(results)

    if session:
        summary = analyze_session(results)
        _print_session(summary)
        import json as _json
        from datetime import datetime
        out = Path("reports") / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        out.write_text(_json.dumps(summary, indent=2))
        console.print(f"\n[green]Session report:[/green] {out}")

    if fmt:
        out = export_results(results, fmt)
        console.print(f"\n[green]Exported:[/green] {out}")


@cli.command()
@click.option("-n", default=3, show_default=True,
              help="Number of logs to generate (max 6).")
@click.option("--save", is_flag=True,
              help="Save generated logs to data/sample_logs/")
def generate(n, save):
    """Generate synthetic AI agent logs using Claude."""
    n = min(n, 6)
    console.print(f"[bold cyan]Generating {n} synthetic log(s)...[/bold cyan]")

    with console.status("Calling Claude..."):
        logs = generate_logs(n)

    for log in logs:
        console.print_json(json.dumps(log))

    if save:
        out_dir = Path("data/sample_logs")
        for log in logs:
            out = out_dir / f"{log['log_id']}.json"
            out.write_text(json.dumps(log, indent=2))
        console.print(f"\n[green]Saved {len(logs)} log(s) to {out_dir}/[/green]")


if __name__ == "__main__":
    cli()
