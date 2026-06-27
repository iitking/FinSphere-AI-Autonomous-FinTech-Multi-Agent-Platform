"""
FinSphere AI - Interactive Command-Line Interface (CLI).
Allows terminal execution of autonomous agents, pipelines, and full demonstrations.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agents.orchestrator import Orchestrator
from core.config import settings

console = Console()


async def run_query(query: str, pipeline: list[str] | None = None):
    orch = Orchestrator()
    with console.status(f"[bold cyan]FinSphere AI is thinking...[/bold cyan]"):
        if pipeline:
            results = await orch.run_pipeline(query, pipeline)
            for resp in results:
                print_response(resp)
        else:
            resp = await orch.route(query)
            print_response(resp)


async def run_analyze(ticker: str, timeframe: str = "1Y"):
    orch = Orchestrator()
    with console.status(f"[bold cyan]Analyzing equity fundamentals for {ticker}...[/bold cyan]"):
        agent = orch.agents["financial_analysis"]
        query = f"Analyze {ticker} fundamentals over {timeframe}."
        resp = await agent.run(query)
        print_response(resp)


async def run_risk(asset: str, profile: str = "moderate"):
    orch = Orchestrator()
    with console.status(f"[bold cyan]Evaluating 5-dimension risk for {asset}...[/bold cyan]"):
        agent = orch.agents["risk_assessment"]
        query = f"Conduct risk assessment on {asset} for {profile} risk profile."
        resp = await agent.run(query)
        print_response(resp)


async def run_portfolio(capital: float, risk: str = "moderate", years: int = 5):
    orch = Orchestrator()
    with console.status(f"[bold cyan]Synthesizing optimal MPT portfolio...[/bold cyan]"):
        agent = orch.agents["portfolio"]
        query = f"Build optimized portfolio for ₹{capital:,.0f} with {risk} risk over {years} years."
        resp = await agent.run(query)
        print_response(resp)


async def run_fraud():
    orch = Orchestrator()
    sample_txns = [
        {"transaction_id": "TXN_IND_001", "amount_inr": 185000, "merchant": "Jewellery Retail", "location": "Delhi, India", "user_id": "U1", "channel": "UPI"},
        {"transaction_id": "TXN_IND_002", "amount_inr": 9950, "merchant": "Digital Services", "location": "Bengaluru, India", "user_id": "U1", "channel": "UPI"},
        {"transaction_id": "TXN_IND_003", "amount_inr": 62000, "merchant": "Crypto Exchange", "location": "London, UK", "user_id": "U1", "channel": "CARD"},
    ]
    with console.status("[bold cyan]Scanning transaction batch for fraud vectors...[/bold cyan]"):
        agent = orch.agents["fraud_detection"]
        query = f"Analyze transactions:\n{json.dumps(sample_txns, indent=2)}"
        resp = await agent.run(query, {"transactions": sample_txns})
        print_response(resp)


async def run_compliance(text: str):
    orch = Orchestrator()
    with console.status("[bold cyan]Conducting regulatory compliance audit...[/bold cyan]"):
        agent = orch.agents["compliance"]
        resp = await agent.run(text)
        print_response(resp)


async def run_demo():
    console.print(Panel.fit("[bold green]FinSphere AI Autonomous Multi-Agent Demonstration[/bold green]\n"
                            "Running end-to-end simulation across all 5 intelligence agents."))
    orch = Orchestrator()

    # 1. Routing
    console.print("\n[bold yellow]Step 1: Smart Routing & Financial Analysis[/bold yellow]")
    r1 = await orch.route("Analyze HDFC Bank fundamental multiples and loan growth.")
    print_response(r1)

    # 2. Risk Assessment
    console.print("\n[bold yellow]Step 2: Risk Assessment[/bold yellow]")
    r2 = await orch.agents["risk_assessment"].run("Assess downside volatility of high yield corporate bonds.")
    print_response(r2)

    # 3. Portfolio
    console.print("\n[bold yellow]Step 3: Portfolio Optimization[/bold yellow]")
    r3 = await orch.agents["portfolio"].run("Allocate ₹25,00,000 for balanced Indian investor.")
    print_response(r3)

    # 4. Fraud Detection
    console.print("\n[bold yellow]Step 4: Fraud Detection Heuristics + LLM[/bold yellow]")
    await run_fraud()

    # 5. Regulatory Compliance
    console.print("\n[bold yellow]Step 5: Compliance Audit (DPDP & RBI)[/bold yellow]")
    r5 = await orch.agents["compliance"].run("Customer onboarding consent form without opt-out for marketing.")
    print_response(r5)


def print_response(resp):
    agent_title = resp.agent.replace("_", " ").upper()
    console.print(Panel(
        f"[bold]{resp.output}[/bold]\n\n"
        f"[dim]Elapsed: {resp.elapsed_s}s | Success: {resp.success} | PII Flags: {resp.guardrail_flags}[/dim]",
        title=f"🤖 [bold cyan]{agent_title}[/bold cyan]",
        border_style="green" if resp.success else "red",
    ))

    if resp.metadata:
        table = Table(title="Structured Metadata & Tool Outputs", show_header=True, header_style="bold magenta")
        table.add_column("Key", style="dim", width=24)
        table.add_column("Value")
        for k, v in resp.metadata.items():
            val_str = json.dumps(v, indent=2) if isinstance(v, (dict, list)) else str(v)
            table.add_row(k, val_str)
        console.print(table)


def print_config():
    table = Table(title=f"⚙️ {settings.app_name} Runtime Parameters", show_header=True, header_style="bold cyan")
    table.add_column("Parameter Category")
    table.add_column("Configuration Value")

    table.add_row("Execution Mode", "Simulation (Offline Mock)" if settings.is_simulation_mode else "Live Claude API")
    table.add_row("Active Model", settings.model)
    table.add_row("Base Currency & FX", f"{settings.base_currency} (USD/INR @ {settings.usd_to_inr_rate})")
    table.add_row("Indian Capital Gains Tax", f"STCG: {settings.stcg_tax_rate*100}% | LTCG: {settings.ltcg_tax_rate*100}%")
    table.add_row("Fraud Threshold (INR)", f"₹{settings.high_amount_threshold_inr:,.0f}")
    table.add_row("Risk Weights (M/C/L/R/O)", f"{settings.market_risk_weight}/{settings.credit_risk_weight}/{settings.liquidity_risk_weight}/{settings.regulatory_risk_weight}/{settings.operational_risk_weight}")
    table.add_row("Max Input / Output", f"{settings.max_input_length} / {settings.max_output_length} chars")
    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="FinSphere AI CLI")
    subparsers = parser.add_subparsers(dest="command")

    # query
    p_query = subparsers.add_parser("query", help="Execute smart query or pipeline")
    p_query.add_argument("query", type=str, help="Financial query")
    p_query.add_argument("--pipeline", nargs="+", help="Sequential agent pipeline")

    # analyze
    p_ana = subparsers.add_parser("analyze", help="Equity research")
    p_ana.add_argument("--ticker", type=str, required=True, help="Stock ticker (e.g. HDFCBANK)")
    p_ana.add_argument("--timeframe", type=str, default="1Y")

    # risk
    p_risk = subparsers.add_parser("risk", help="Risk scoring")
    p_risk.add_argument("--asset", type=str, required=True, help="Asset description")
    p_risk.add_argument("--profile", type=str, default="moderate")

    # portfolio
    p_port = subparsers.add_parser("portfolio", help="Portfolio allocation")
    p_port.add_argument("--capital", type=float, default=1000000)
    p_port.add_argument("--risk", type=str, default="moderate")
    p_port.add_argument("--years", type=int, default=5)

    # fraud
    subparsers.add_parser("fraud", help="Scan sample transactions for fraud")

    # compliance
    p_comp = subparsers.add_parser("compliance", help="Regulatory audit")
    p_comp.add_argument("--text", type=str, required=True, help="Text to audit")

    # demo
    subparsers.add_parser("demo", help="Run automated multi-agent demo")

    # config
    subparsers.add_parser("config", help="View active parameters")

    args = parser.parse_args()

    if args.command == "query":
        asyncio.run(run_query(args.query, args.pipeline))
    elif args.command == "analyze":
        asyncio.run(run_analyze(args.ticker, args.timeframe))
    elif args.command == "risk":
        asyncio.run(run_risk(args.asset, args.profile))
    elif args.command == "portfolio":
        asyncio.run(run_portfolio(args.capital, args.risk, args.years))
    elif args.command == "fraud":
        asyncio.run(run_fraud())
    elif args.command == "compliance":
        asyncio.run(run_compliance(args.text))
    elif args.command == "demo":
        asyncio.run(run_demo())
    elif args.command == "config":
        print_config()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
