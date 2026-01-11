"""
JPMC Financial Research Agent System - DEMO VERSION
Production-quality multi-agent architecture for financial research
(This demo version uses simulated LLM responses for demonstration)
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent roles in the system"""
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    COMPLIANCE = "compliance"
    ORCHESTRATOR = "orchestrator"


@dataclass
class AgentAction:
    """Data class for tracking agent actions (audit trail)"""
    timestamp: str
    agent_role: str
    action_type: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    tokens_used: int
    cost_usd: float
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AuditTrail:
    """Manages audit trail for all agent actions"""
    
    def __init__(self):
        self.actions: List[AgentAction] = []
        self.total_cost = 0.0
        self.total_tokens = 0
    
    def log_action(self, action: AgentAction):
        """Log an agent action"""
        self.actions.append(action)
        self.total_cost += action.cost_usd
        self.total_tokens += action.tokens_used
        logger.info(f"Agent action logged: {action.agent_role} - {action.action_type}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all actions"""
        return {
            "total_actions": len(self.actions),
            "total_cost_usd": round(self.total_cost, 4),
            "total_tokens": self.total_tokens,
            "actions_by_agent": {
                role.value: len([a for a in self.actions if a.agent_role == role.value])
                for role in AgentRole
            },
            "success_rate": round(
                len([a for a in self.actions if a.success]) / len(self.actions) * 100, 2
            ) if self.actions else 0
        }
    
    def export_to_file(self, filepath: str):
        """Export audit trail to JSON file"""
        with open(filepath, 'w') as f:
            json.dump({
                "summary": self.get_summary(),
                "actions": [a.to_dict() for a in self.actions]
            }, f, indent=2)
        logger.info(f"Audit trail exported to {filepath}")


class ComplianceCheck:
    """Handles compliance validation for agent outputs"""
    
    # Simulated regulatory requirements
    RESTRICTED_KEYWORDS = [
        "insider trading", "market manipulation", "money laundering",
        "guaranteed returns", "risk-free investment"
    ]
    
    @staticmethod
    def validate_output(output: str) -> tuple[bool, Optional[str]]:
        """
        Validate agent output for compliance
        Returns: (is_compliant, risk_message)
        """
        output_lower = output.lower()
        
        # Check for restricted keywords
        for keyword in ComplianceCheck.RESTRICTED_KEYWORDS:
            if keyword in output_lower:
                return False, f"Output contains restricted keyword: '{keyword}'"
        
        # Check for potential financial advice (without disclaimers)
        advice_indicators = ["you should", "i recommend", "best investment"]
        has_advice = any(ind in output_lower for ind in advice_indicators)
        has_disclaimer = "not financial advice" in output_lower or "for informational purposes" in output_lower
        
        if has_advice and not has_disclaimer:
            return False, "Output appears to provide financial advice without disclaimer"
        
        return True, None
    
    @staticmethod
    def add_disclaimers(output: str) -> str:
        """Add regulatory disclaimers to output"""
        disclaimer = "\n\n--- DISCLAIMER ---\nThis information is for educational and informational purposes only. It does not constitute financial advice. Please consult with a qualified financial professional before making investment decisions."
        return output + disclaimer


class MockLLM:
    """Mock LLM for demo purposes"""
    
    @staticmethod
    def generate_research(company_name: str) -> str:
        """Generate simulated research summary"""
        return f"""
COMPANY RESEARCH: {company_name}

Company Overview:
{company_name} is a leading company in its sector with significant market presence. The company has demonstrated consistent performance over recent quarters.

Recent Financial Performance:
- Revenue growth of 15% year-over-year
- Strong profit margins maintained at industry-leading levels
- Successful expansion into new markets
- Positive cash flow generation

Recent Developments:
- Launched new product line in Q4
- Announced strategic partnership with major industry player
- Expanded operations to three new regions
- Received positive analyst ratings from major investment firms

Market Position:
{company_name} maintains a competitive position with strong brand recognition and customer loyalty. The company's market share has been growing steadily, supported by innovation and operational excellence.
"""
    
    @staticmethod
    def generate_analysis(company_name: str, research: str) -> str:
        """Generate simulated financial analysis"""
        return f"""
INVESTMENT ANALYSIS: {company_name}

Key Strengths:
1. Strong Market Position: Leading player with established brand and customer base
2. Revenue Growth: Consistent double-digit growth trajectory
3. Financial Health: Strong balance sheet with healthy cash reserves
4. Innovation Pipeline: Continued investment in R&D and new products

Key Risks:
1. Market Competition: Intensifying competition from new entrants
2. Economic Sensitivity: Performance tied to broader economic conditions
3. Regulatory Environment: Potential regulatory changes could impact operations
4. Operational Complexity: Scale brings increased complexity in management

Market Opportunities:
- Expansion into emerging markets
- Digital transformation initiatives
- Strategic acquisitions in adjacent markets
- Product line extensions

Threats:
- Disruptive technologies from competitors
- Economic downturn risks
- Supply chain vulnerabilities
- Changing consumer preferences

Investment Considerations:
Based on the available information, {company_name} demonstrates several positive indicators including strong financial performance, market leadership, and growth trajectory. However, investors should carefully consider the identified risks and conduct thorough due diligence. Diversification remains important, and this analysis should be one input among many in investment decision-making.

Note: This analysis is based on publicly available information and should not be the sole basis for investment decisions.
"""


class ResearchAgent:
    """Agent specialized in research and information gathering"""
    
    def __init__(self, audit_trail: AuditTrail):
        self.audit_trail = audit_trail
        self.llm = MockLLM()
    
    def research_company(self, company_name: str) -> str:
        """Research a company"""
        start_time = datetime.now()
        
        try:
            logger.info(f"Research Agent: Gathering information on {company_name}...")
            
            # Generate research using mock LLM
            output = self.llm.generate_research(company_name)
            
            # Log action
            action = AgentAction(
                timestamp=datetime.now().isoformat(),
                agent_role=AgentRole.RESEARCHER.value,
                action_type="company_research",
                input_data={"company_name": company_name},
                output_data={"summary": output[:200] + "..."},
                tokens_used=len(output.split()),
                cost_usd=0.002,
                success=True
            )
            self.audit_trail.log_action(action)
            
            return output
            
        except Exception as e:
            logger.error(f"Research agent error: {str(e)}")
            action = AgentAction(
                timestamp=datetime.now().isoformat(),
                agent_role=AgentRole.RESEARCHER.value,
                action_type="company_research",
                input_data={"company_name": company_name},
                output_data={},
                tokens_used=0,
                cost_usd=0.0,
                success=False,
                error_message=str(e)
            )
            self.audit_trail.log_action(action)
            return f"Error during research: {str(e)}"


class AnalysisAgent:
    """Agent specialized in financial analysis"""
    
    def __init__(self, audit_trail: AuditTrail):
        self.audit_trail = audit_trail
        self.llm = MockLLM()
    
    def analyze_investment_potential(self, research_summary: str, company_name: str) -> str:
        """Analyze investment potential based on research"""
        
        try:
            logger.info(f"Analysis Agent: Evaluating investment potential for {company_name}...")
            
            # Generate analysis using mock LLM
            output = self.llm.generate_analysis(company_name, research_summary)
            
            # Log action
            action = AgentAction(
                timestamp=datetime.now().isoformat(),
                agent_role=AgentRole.ANALYST.value,
                action_type="investment_analysis",
                input_data={"company_name": company_name},
                output_data={"analysis": output[:200] + "..."},
                tokens_used=len(output.split()),
                cost_usd=0.003,
                success=True
            )
            self.audit_trail.log_action(action)
            
            return output
            
        except Exception as e:
            logger.error(f"Analysis agent error: {str(e)}")
            action = AgentAction(
                timestamp=datetime.now().isoformat(),
                agent_role=AgentRole.ANALYST.value,
                action_type="investment_analysis",
                input_data={"company_name": company_name},
                output_data={},
                tokens_used=0,
                cost_usd=0.0,
                success=False,
                error_message=str(e)
            )
            self.audit_trail.log_action(action)
            return f"Error during analysis: {str(e)}"


class ComplianceAgent:
    """Agent specialized in compliance checking"""
    
    def __init__(self, audit_trail: AuditTrail):
        self.audit_trail = audit_trail
    
    def review_output(self, content: str, content_type: str) -> Dict[str, Any]:
        """Review content for compliance"""
        
        try:
            logger.info(f"Compliance Agent: Reviewing {content_type} for regulatory compliance...")
            
            # Validate compliance
            is_compliant, risk_message = ComplianceCheck.validate_output(content)
            
            # Add disclaimers if compliant
            if is_compliant:
                final_content = ComplianceCheck.add_disclaimers(content)
                result = {
                    "compliant": True,
                    "risk_message": None,
                    "final_content": final_content
                }
            else:
                result = {
                    "compliant": False,
                    "risk_message": risk_message,
                    "final_content": None
                }
            
            # Log action
            action = AgentAction(
                timestamp=datetime.now().isoformat(),
                agent_role=AgentRole.COMPLIANCE.value,
                action_type="compliance_review",
                input_data={"content_type": content_type},
                output_data={"compliant": is_compliant, "risk_message": risk_message},
                tokens_used=0,
                cost_usd=0.0,
                success=True
            )
            self.audit_trail.log_action(action)
            
            return result
            
        except Exception as e:
            logger.error(f"Compliance agent error: {str(e)}")
            action = AgentAction(
                timestamp=datetime.now().isoformat(),
                agent_role=AgentRole.COMPLIANCE.value,
                action_type="compliance_review",
                input_data={"content_type": content_type},
                output_data={},
                tokens_used=0,
                cost_usd=0.0,
                success=False,
                error_message=str(e)
            )
            self.audit_trail.log_action(action)
            return {
                "compliant": False,
                "risk_message": f"Compliance check error: {str(e)}",
                "final_content": None
            }


class AgentOrchestrator:
    """Orchestrates multi-agent workflow"""
    
    def __init__(self):
        self.audit_trail = AuditTrail()
        
        # Initialize agents
        self.researcher = ResearchAgent(self.audit_trail)
        self.analyst = AnalysisAgent(self.audit_trail)
        self.compliance = ComplianceAgent(self.audit_trail)
    
    def research_investment(self, company_name: str) -> Dict[str, Any]:
        """
        Complete workflow: Research → Analyze → Compliance Check
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting investment research workflow for: {company_name}")
        logger.info(f"{'='*60}\n")
        
        # Step 1: Research
        logger.info("STEP 1: Research Agent - Gathering Information")
        logger.info("-" * 60)
        research_summary = self.researcher.research_company(company_name)
        
        if "Error" in research_summary:
            return {
                "success": False,
                "error": research_summary,
                "audit_summary": self.audit_trail.get_summary()
            }
        
        # Step 2: Analysis
        logger.info("\nSTEP 2: Analysis Agent - Evaluating Investment Potential")
        logger.info("-" * 60)
        analysis_result = self.analyst.analyze_investment_potential(research_summary, company_name)
        
        if "Error" in analysis_result:
            return {
                "success": False,
                "error": analysis_result,
                "audit_summary": self.audit_trail.get_summary()
            }
        
        # Step 3: Compliance Review
        logger.info("\nSTEP 3: Compliance Agent - Reviewing Output")
        logger.info("-" * 60)
        compliance_result = self.compliance.review_output(
            content=f"{research_summary}\n\n{analysis_result}",
            content_type="investment_research"
        )
        
        if not compliance_result["compliant"]:
            return {
                "success": False,
                "error": f"Compliance check failed: {compliance_result['risk_message']}",
                "audit_summary": self.audit_trail.get_summary()
            }
        
        # Success
        logger.info("\n" + "="*60)
        logger.info("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        logger.info("="*60 + "\n")
        
        return {
            "success": True,
            "company_name": company_name,
            "research_summary": research_summary,
            "analysis": analysis_result,
            "final_output": compliance_result["final_content"],
            "audit_summary": self.audit_trail.get_summary()
        }
    
    def export_audit_trail(self, filepath: str):
        """Export complete audit trail"""
        self.audit_trail.export_to_file(filepath)


def demo_agent_system():
    """Demo the agent system"""
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Run investment research workflow
    print("\n" + "="*70)
    print("JPMC FINANCIAL RESEARCH AGENT SYSTEM - DEMO")
    print("Production-Quality Multi-Agent Architecture")
    print("="*70 + "\n")
    
    company = "Google"

    print(f"🔍 Researching: {company}")
    print("-" * 70)
    
    result = orchestrator.research_investment(company)
    
    if result["success"]:
        print("\n" + "="*70)
        print("✅ RESEARCH COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")
        
        print("📊 AUDIT SUMMARY:")
        print("-" * 70)
        audit_summary = result["audit_summary"]
        print(f"Total Agent Actions: {audit_summary['total_actions']}")
        print(f"Total Cost: ${audit_summary['total_cost_usd']}")
        print(f"Total Tokens: {audit_summary['total_tokens']:,}")
        print(f"Success Rate: {audit_summary['success_rate']}%")
        print(f"\nActions by Agent:")
        for agent, count in audit_summary['actions_by_agent'].items():
            print(f"  - {agent.title()}: {count} actions")
        
        print("\n" + "="*70)
        print("📄 FINAL OUTPUT (with compliance disclaimers):")
        print("="*70 + "\n")
        print(result["final_output"])
        
        # Export audit trail
        audit_file = "audit_trail.json"
        orchestrator.export_audit_trail(audit_file)
        print("\n" + "="*70)
        print(f"💾 Full audit trail exported to: {audit_file}")
        print("="*70 + "\n")
        
        return True
    else:
        print("\n❌ RESEARCH FAILED")
        print(f"Error: {result['error']}")
        return False


if __name__ == "__main__":
    success = demo_agent_system()
    exit(0 if success else 1)
