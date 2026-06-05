"""
Offline Simulation and Mock Engine.
Enables full end-to-end testing, CLI usage, and Web UI demonstration
without requiring an active Anthropic API key.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List
from core.config import settings


class MockMessageBlock:
    def __init__(self, block_type: str, text: str = "", tool_name: str = "", tool_input: dict = None, tool_id: str = "mock_call_001"):
        self.type = block_type
        self.text = text
        self.name = tool_name
        self.input = tool_input or {}
        self.id = tool_id


class MockClaudeResponse:
    def __init__(self, content: List[Any]):
        self.content = content


class MockEngine:
    """Simulates realistic Claude multi-agent responses with tool execution."""

    @staticmethod
    def generate_response(agent_name: str, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]] | None = None) -> MockClaudeResponse:
        user_text = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                content = m.get("content")
                if isinstance(content, str):
                    user_text = content
                    break
                elif isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "tool_result":
                            pass
                        elif isinstance(part, dict) and "text" in part:
                            user_text = part["text"]
                    if user_text:
                        break

        # Check if this is a tool return follow-up
        is_followup = any(
            isinstance(m.get("content"), list) and any(isinstance(p, dict) and p.get("type") == "tool_result" for p in m["content"])
            for m in messages
        )

        if is_followup:
            return MockEngine._handle_followup(agent_name, user_text)

        if agent_name == "financial_analysis":
            return MockEngine._mock_financial_analysis(user_text)
        elif agent_name == "risk_assessment":
            return MockEngine._mock_risk_assessment(user_text)
        elif agent_name == "portfolio":
            return MockEngine._mock_portfolio(user_text)
        elif agent_name == "fraud_detection":
            return MockEngine._mock_fraud_detection(user_text)
        elif agent_name == "compliance":
            return MockEngine._mock_compliance(user_text)
        else:
            return MockClaudeResponse([
                MockMessageBlock("text", f"Synthesized analysis for query: {user_text[:100]}")
            ])

    @staticmethod
    def _handle_followup(agent_name: str, query: str) -> MockClaudeResponse:
        narratives = {
            "financial_analysis": (
                "### Detailed Financial & Fundamental Synthesis\n\n"
                "• **Valuation Multiples**: The entity trades at reasonable historical valuation relative to 5-year averages.\n"
                "• **Profitability Profile**: Sustained ROE (>16%) with robust operational leverage.\n"
                "• **Indian Macro Environment**: Beneficiary of domestic capex cycle and RBI interest rate stability.\n"
                "• **Bear Considerations**: Margin pressure from raw material inflation or higher deposit cost repricing.\n\n"
                "**Conclusion:** Fundamentals remain solid with long-term compounding potential."
            ),
            "risk_assessment": (
                "### Risk Assessment Executive Summary\n\n"
                "• **Primary Vulnerability**: Market volatility and liquidity compression during sector rotations.\n"
                "• **Regulatory Scrutiny**: High adherence required under latest RBI & SEBI circulars.\n"
                "• **Mitigation Roadmap**: Implement stop-loss triggers, hedge via index options, and stagger entry."
            ),
            "portfolio": (
                "### Portfolio Strategy & Execution Guidelines\n\n"
                "• **Asset Allocation Rationale**: Balances growth through Indian equities while anchoring capital preservation in G-Secs and Sovereign Gold.\n"
                "• **Tax Efficiency**: Formulated taking into account STCG (20%) and LTCG (12.5%) under recent Indian tax laws.\n"
                "• **Rebalancing Action**: Review quarterly to realign drifting weights back to target."
            ),
            "fraud_detection": (
                "### Fraud Investigation & Anomaly Report\n\n"
                "• **Behavioral Flags**: Multi-channel transaction burst detected with geographic inconsistency.\n"
                "• **Action Enforced**: Elevated transaction hold applied on suspicious units; 2FA challenge triggered.\n"
                "• **Audit Trail**: Recorded under internal AML tracking for potential STR filing."
            ),
            "compliance": (
                "### Regulatory Compliance Audit Findings\n\n"
                "• **Framework Alignment**: Evaluated against RBI Digital Lending Master Direction, SEBI LODR, and DPDP Act 2023.\n"
                "• **Risk Areas**: Consent architecture requires explicit, granular opt-in mechanisms.\n"
                "• **Remediation**: Update customer notice and establish 72-hour regulatory reporting SLA."
            ),
        }
        text = narratives.get(agent_name, "Analysis complete.")
        return MockClaudeResponse([MockMessageBlock("text", text)])

    @staticmethod
    def _mock_financial_analysis(text: str) -> MockClaudeResponse:
        ticker = "HDFCBANK"
        for t in ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "TATAMOTORS", "SBIN", "NVDA", "AAPL"]:
            if t.lower() in text.lower():
                ticker = t
                break

        metrics = {
            "pe_ratio": 19.8,
            "revenue_growth": 14.5,
            "profit_margin": 22.4,
            "debt_to_equity": 0.85,
            "analyst_rating": "buy",
            "key_risks": [
                "Net interest margin (NIM) compression",
                "Asset quality slippages in unsecured retail book",
                "Foreign institutional investor (FII) volatility",
            ],
            "key_catalysts": [
                "Branch network expansion and deposit mobilization",
                "Digital lending penetration through UPI and credit lines",
                "Favorable Indian credit cycle and GDP growth",
            ],
        }

        tool_block = MockMessageBlock(
            block_type="tool_use",
            tool_name="extract_financial_metrics",
            tool_input=metrics,
            tool_id="call_metrics_001",
        )
        text_block = MockMessageBlock(
            block_type="text",
            text=f"### Fundamental Analysis Report for {ticker}\n\n"
                 f"Evaluating fundamental performance, operational margins, and Indian market macroeconomic catalysts for **{ticker}**."
        )
        return MockClaudeResponse([text_block, tool_block])

    @staticmethod
    def _mock_risk_assessment(text: str) -> MockClaudeResponse:
        market_score = 42.0
        credit_score = 25.0
        liquidity_score = 30.0
        reg_score = 35.0
        op_score = 20.0

        overall = (
            market_score * settings.market_risk_weight +
            credit_score * settings.credit_risk_weight +
            liquidity_score * settings.liquidity_risk_weight +
            reg_score * settings.regulatory_risk_weight +
            op_score * settings.operational_risk_weight
        )

        risk_level = "low"
        if overall > settings.risk_high_cutoff:
            risk_level = "critical"
        elif overall > settings.risk_medium_cutoff:
            risk_level = "high"
        elif overall > settings.risk_low_cutoff:
            risk_level = "medium"

        risk_data = {
            "overall_score": round(overall, 1),
            "risk_level": risk_level,
            "market_risk": market_score,
            "credit_risk": credit_score,
            "liquidity_risk": liquidity_score,
            "regulatory_risk": reg_score,
            "operational_risk": op_score,
            "top_risk_factors": [
                "Domestic interest rate fluctuation risks",
                "Currency volatility against USD",
                "Regulatory compliance tightening by RBI / SEBI",
            ],
            "mitigants": [
                "Hedging via derivative instruments",
                "Strict counterparty exposure limits",
                "Continuous automated compliance scanning",
            ],
        }

        tool_block = MockMessageBlock(
            block_type="tool_use",
            tool_name="score_risk",
            tool_input=risk_data,
            tool_id="call_risk_001",
        )
        text_block = MockMessageBlock(
            block_type="text",
            text="### Multi-Dimensional Risk Assessment\n\n"
                 "Synthesizing market, credit, liquidity, and statutory exposures under Indian financial regulations."
        )
        return MockClaudeResponse([text_block, tool_block])

    @staticmethod
    def _mock_portfolio(text: str) -> MockClaudeResponse:
        is_aggressive = "aggressive" in text.lower()
        is_conservative = "conservative" in text.lower()

        if is_aggressive:
            allocations = [
                {"asset": "Nifty 50 Large Cap Index", "weight_pct": 45.0, "rationale": "Core compounding in India's top 50 blue-chips"},
                {"asset": "Nifty Midcap 150 Index", "weight_pct": 25.0, "rationale": "High alpha growth in emerging market leaders"},
                {"asset": "US Tech / Nasdaq 100 FoF", "weight_pct": 15.0, "rationale": "Geographic diversification within RBI LRS limits"},
                {"asset": "Sovereign Gold Bonds / Gold ETF", "weight_pct": 10.0, "rationale": "Inflation hedge and currency depreciation buffer"},
                {"asset": "Liquid & Short Duration Debt Funds", "weight_pct": 5.0, "rationale": "Liquidity buffer for opportunistic deployment"},
            ]
            exp_return = 14.2
            sharpe = 1.38
        elif is_conservative:
            allocations = [
                {"asset": "Government Securities (G-Sec 10Y)", "weight_pct": 40.0, "rationale": "Sovereign guaranteed fixed income yield"},
                {"asset": "Corporate AAA Bond Funds", "weight_pct": 25.0, "rationale": "High quality debt accrual"},
                {"asset": "Nifty 50 Equal Weight Index", "weight_pct": 20.0, "rationale": "Conservative equity participation in large caps"},
                {"asset": "Sovereign Gold Bonds / Gold ETF", "weight_pct": 10.0, "rationale": "Store of value and hedge"},
                {"asset": "Overnight & Liquid Funds", "weight_pct": 5.0, "rationale": "Immediate cash flow and emergency liquidity"},
            ]
            exp_return = 8.8
            sharpe = 1.65
        else:
            allocations = [
                {"asset": "Nifty 50 Large Cap Index", "weight_pct": 35.0, "rationale": "Foundational domestic equity backbone"},
                {"asset": "Nifty Next 50 / Midcap Index", "weight_pct": 15.0, "rationale": "High-growth potential mid-caps"},
                {"asset": "Target Maturity Debt / G-Sec Funds", "weight_pct": 25.0, "rationale": "Predictable risk-free accrual yield"},
                {"asset": "Sovereign Gold Bonds (SGB)", "weight_pct": 10.0, "rationale": "Sovereign backed bullion with 2.5% annual interest"},
                {"asset": "Global Diversified ETF (US/Europe)", "weight_pct": 10.0, "rationale": "International exposure within LRS quota"},
                {"asset": "Indian REITs & InvITs", "weight_pct": 5.0, "rationale": "Commercial real estate cash yield & dividend stream"},
            ]
            exp_return = 11.8
            sharpe = 1.45

        alloc_data = {
            "allocations": allocations,
            "expected_portfolio_return": exp_return,
            "estimated_sharpe": sharpe,
            "rebalance_frequency": "quarterly",
        }

        tool_block = MockMessageBlock(
            block_type="tool_use",
            tool_name="suggest_allocation",
            tool_input=alloc_data,
            tool_id="call_portfolio_001",
        )
        text_block = MockMessageBlock(
            block_type="text",
            text="### Optimized Asset Allocation Strategy\n\n"
                 "Modern Portfolio Theory allocation tailored for Indian taxation and market liquidity."
        )
        return MockClaudeResponse([text_block, tool_block])

    @staticmethod
    def _mock_fraud_detection(text: str) -> MockClaudeResponse:
        results = [
            {
                "transaction_id": "TXN_IND_8901",
                "fraud_score": 88.0,
                "is_flagged": True,
                "fraud_type": "geo_impossible_velocity",
                "reason": "Transaction initiated from Mumbai, India, followed 14 minutes later from Lagos, Nigeria.",
            },
            {
                "transaction_id": "TXN_IND_8902",
                "fraud_score": 12.0,
                "is_flagged": False,
                "fraud_type": "none",
                "reason": "Standard domestic merchant transaction matching historical consumer habits.",
            },
            {
                "transaction_id": "TXN_IND_8903",
                "fraud_score": 74.0,
                "is_flagged": True,
                "fraud_type": "smurfing_structuring",
                "reason": "Repeated UPI split-payments of ₹9,990 deliberately staying below the ₹10,000 threshold.",
            },
        ]
        actions = [
            "Immediate block on TXN_IND_8901 and initiate account temporary freeze.",
            "Flag user account for mandatory biometric re-verification under RBI KYC directions.",
            "Queue structured transactions for PMLA Suspicious Transaction Reporting (STR).",
        ]

        tool_block = MockMessageBlock(
            block_type="tool_use",
            tool_name="flag_transactions",
            tool_input={"results": results, "recommended_actions": actions},
            tool_id="call_fraud_001",
        )
        text_block = MockMessageBlock(
            block_type="text",
            text="### Autonomous Fraud Detection & Anomaly Screening\n\n"
                 "Evaluating transaction patterns across UPI, IMPS, and card gateways."
        )
        return MockClaudeResponse([text_block, tool_block])

    @staticmethod
    def _mock_compliance(text: str) -> MockClaudeResponse:
        has_issue = any(w in text.lower() for w in ["unlicensed", "cash", "crypto", "anonymous", "offshore", "bypass"])
        violations = []
        if has_issue:
            violations = [
                {
                    "regulation": "PMLA 2002 Section 12",
                    "description": "Lack of verified beneficial ownership documentation for high-volume transactions.",
                    "severity": "major",
                },
                {
                    "regulation": "RBI Digital Lending Master Direction 2022",
                    "description": "Direct borrower-to-RE disbursement requirement bypassed via intermediary escrow.",
                    "severity": "critical",
                },
            ]
            compliant = False
            kyc_status = "review_required"
        else:
            violations = []
            compliant = True
            kyc_status = "clear"

        comp_data = {
            "overall_compliant": compliant,
            "violations": violations,
            "recommendations": [
                "Ensure end-to-end data localization in compliance with RBI storage circular and DPDP Act 2023.",
                "Implement strict automated STR screening before onboarding Category-A merchant partners.",
                "Maintain audit trails for 5 years as mandated under Prevention of Money Laundering rules.",
            ],
            "kyc_aml_status": kyc_status,
        }

        tool_block = MockMessageBlock(
            block_type="tool_use",
            tool_name="compliance_check",
            tool_input=comp_data,
            tool_id="call_comp_001",
        )
        text_block = MockMessageBlock(
            block_type="text",
            text="### Indian Regulatory Compliance & Audit Assessment\n\n"
                 "Reviewing regulatory posture against RBI, SEBI, PMLA, and DPDP Act statutory requirements."
        )
        return MockClaudeResponse([text_block, tool_block])
