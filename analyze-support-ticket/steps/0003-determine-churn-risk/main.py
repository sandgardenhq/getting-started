from pydantic import BaseModel

def handler(input, sandgarden, runtime_context):
    """
    Calculate customer churn risk based on sentiment and history
    """
    # TODO: Implement churn risk analysis
    pass
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class ChurnRiskFactors(BaseModel):
    sentiment_indicators: List[str]
    technical_factors: List[str]
    account_factors: List[str]
    historical_factors: List[str]

class ChurnRiskAssessment(BaseModel):
    risk_level: str  # high, medium, low
    confidence: float
    risk_factors: ChurnRiskFactors
    recommendations: List[str]
    priority_score: int  # 1-100

class ChurnRiskResponse(BaseModel):
    ticket: dict
    summary: str
    sentiment: dict
    account: Optional[Dict] = None
    risk_assessment: ChurnRiskAssessment

class TicketInput(BaseModel):
    ticket: dict
    summary: str
    analysis: dict
    account: Optional[Dict] = None

async def handler(input, sandgarden, runtime_context):
    """
    Assess the risk of customer churn based on ticket content and sentiment.

    This handler analyzes multiple factors to determine churn risk:
    1. Current ticket severity and sentiment
    2. Account characteristics (size, tier, history)
    3. Technical impact and affected systems
    4. Historical patterns and satisfaction indicators

    Args:
        input: Dict containing ticket, summary, sentiment analysis, and account data
        sandgarden: SandGarden context with connectors and prompts
        runtime_context: Runtime execution context

    Returns:
        Dict containing all previous analysis plus:
        - Churn risk assessment
        - Contributing factors
        - Recommendations
    """
    # Parse input
    ticket_data = TicketInput(**input)
    
    # Get LLM client and prompt
    llm = sandgarden.connectors['churn-analyzer-model']
    prompt = sandgarden.prompts('assess-churn-risk')
    
    # Prepare content for analysis
    analysis_content = f"""
Ticket Summary:
{ticket_data.summary}

Sentiment Analysis:
- Overall Sentiment: {ticket_data.analysis.get('sentiment', 'Unknown')}
- Confidence: {ticket_data.analysis.get('confidence', 0.0)}
- Urgency Level: {ticket_data.analysis.get('urgency_level', 'Unknown')}
- Key Phrases: {', '.join(ticket_data.analysis.get('key_phrases', []))}
- Emotion Indicators: {', '.join(ticket_data.analysis.get('emotion_indicators', []))}
- Satisfaction Indicators: {', '.join(ticket_data.analysis.get('satisfaction_indicators', []))}

Account Information:
{f'''- Name: {ticket_data.account['name']}
- Annual Contract Value: ${ticket_data.account['acv']:,}
- Tier: {ticket_data.account['tier']}
- Support Level: {ticket_data.account['support_level']}
- Industry: {ticket_data.account['industry']}
- Critical Systems: {', '.join(ticket_data.account['critical_systems'])}
- Region: {ticket_data.account['region']}''' if ticket_data.account else '- No account information available'}

Ticket Details:
- Priority: {ticket_data.ticket.get('priority', 'Unknown')}
- Status: {ticket_data.ticket.get('status', 'Unknown')}
- Tags: {', '.join(ticket_data.ticket.get('tags', []))}
"""
    
    # Get structured churn risk assessment from LLM
    risk_assessment = await llm.beta.chat.completions.parse(
        prompt=prompt,
        messages=[{"role": "user", "content": analysis_content}],
        response_format=ChurnRiskAssessment
    )
    
    # Return all data plus risk assessment
    return ChurnRiskResponse(
        ticket=ticket_data.ticket,
        summary=ticket_data.summary,
        sentiment=ticket_data.analysis,
        account=ticket_data.account,
        risk_assessment=risk_assessment
    ).model_dump(mode='json')
