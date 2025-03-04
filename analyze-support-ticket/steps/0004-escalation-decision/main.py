from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from slack_sdk.webhook import WebhookClient
from datetime import datetime, timezone

class Account(BaseModel):
    id: str
    name: str
    acv: int
    tier: str
    industry: str
    support_level: str
    critical_systems: List[str]
    region: str

class SentimentAnalysis(BaseModel):
    sentiment: str  # positive, negative, neutral
    confidence: float
    key_phrases: List[str]
    emotion_indicators: List[str]
    urgency_level: str  # high, medium, low
    satisfaction_indicators: List[str]
    
class Ticket(BaseModel):
    id: int
    email: str
    subject: str
    description: Optional[str] = None
    status: str
    priority: Optional[str] = None
    updated_at: str
    organization: Optional[str] = None
    organization_details: Optional[str] = None
    organization_notes: Optional[str] = None
    url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
class TicketSentimentResponse(BaseModel):
    ticket: Ticket
    analysis: SentimentAnalysis
    account: Optional[Account] = None
    
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
    ticket: Ticket
    summary: str
    sentiment: SentimentAnalysis
    account: Optional[Account] = None
    risk_assessment: ChurnRiskAssessment

class EscalationCriteria(BaseModel):
    should_escalate: bool
    reasons: List[str]
    recommended_actions: List[str]
    priority_level: str  # critical, high, medium, low
    response_sla: str  # immediate, 4 hours, 24 hours, etc.

class EscalationResponse(BaseModel):
    ticket: Ticket
    summary: str
    sentiment: SentimentAnalysis
    risk_assessment: ChurnRiskAssessment
    account: Optional[Account] = None
    escalation: EscalationCriteria
    notification_sent: bool = False

class TicketInput(BaseModel):
    ticket: dict

def format_notification(ticket: dict, account: Optional[Dict], risk_assessment: dict, escalation: EscalationCriteria) -> str:
    """Format the Slack notification message."""
    account_info = account or {}
    risk_level = risk_assessment.risk_level.upper()
    priority_score = risk_assessment.priority_score
    
    # Calculate duration since ticket creation
    created_at = datetime.fromisoformat(ticket.created_at.replace('Z', '+00:00'))
    duration = datetime.now(timezone.utc) - created_at
    duration_hours = duration.total_seconds() / 3600
    duration_str = f"{int(duration_hours)}+ hours" if duration_hours >= 1 else f"{int(duration.total_seconds() / 60)} minutes"
    
    # Truncate description and add ellipsis if needed
    description = ticket.description
    if len(description) > 100:
        description = description[:97] + "..."
    
    return f"""🚨 {escalation.priority_level.upper()} TICKET - IMMEDIATE ACTION REQUIRED

Customer: {account_info.name}
Revenue Impact: ${account_info.acv:,} ARR
Churn Risk: {risk_level} {'🔥' if risk_level == 'HIGH' else '⚠️'}

Issue: {ticket.subject}
Duration: {duration_str}
Impact: {description}
Context: Priority Score {priority_score}/100
Urgency: {escalation.response_sla}

AI Analysis: {', '.join(escalation.reasons)}

View in Zendesk: {ticket.get('url', '[No URL]')}
Escalate to On-Call: [Click to Page]"""

# TODO: verify pydoc for all handlers
def handler(input, sandgarden):
    """
    Determine if a ticket requires escalation based on churn risk and business impact.
    
    This handler:
    1. Evaluates ticket severity and churn risk
    2. Determines if technical escalation is needed
    3. Sends notifications for critical issues
    4. Recommends specific response actions
    
    Args:
        input: Dict containing ticket, summary, sentiment, and risk assessment
        sandgarden: SandGarden context with connectors and prompts
        runtime_context: Runtime execution context
    
    Returns:
        Dict containing all previous analysis plus:
        - Escalation decision and criteria
        - Notification status
    """
    # Parse input
    ticket_data = TicketInput(**input)
    
    # Get LLM client and prompt
    llm = sandgarden.get_connector('ticket-summarizer-model')
    prompt = sandgarden.get_prompt('assess-escalation')
    
    # Prepare content for analysis
    analysis_content = f"""
Ticket Summary:
{ticket_data.summary}

Risk Assessment:
- Risk Level: {ticket_data.risk_assessment.risk_level}
- Priority Score: {ticket_data.risk_assessment.priority_score}/100
- Risk Factors: {', '.join(ticket_data.risk_assessment.risk_factors.technical_factors)}
- Recommendations: {', '.join(ticket_data.risk_assessment.recommendations)}

Account Impact:
{f'''- Annual Value: ${ticket_data.account.acv:,}
- Tier: {ticket_data.account.tier}
- Support Level: {ticket_data.account.support_level}
- Critical Systems: {', '.join(ticket_data.account.critical_systems)}''' if ticket_data.account else '- No account information available'}

Sentiment Analysis:
- Overall: {ticket_data.sentiment.sentiment}
- Urgency: {ticket_data.sentiment.urgency_level}
- Key Indicators: {', '.join(ticket_data.sentiment.emotion_indicators)}
"""
    
    # Get structured escalation assessment from LLM
    escalation_criteria = llm.beta.chat.completions.parse(
        prompt=prompt,
        messages=[{"role": "user", "content": analysis_content}],
        response_format=EscalationCriteria
    ).choices[0].message.parsed
    
    # Send notification if escalation is needed
    notification_sent = False
    if escalation_criteria.should_escalate:
        # FIXME: hallucinations
        webhook_url = sandgarden.secrets['slack_webhook_url']
        webhook = WebhookClient(webhook_url)
        
        message = format_notification(
            ticket_data.ticket,
            ticket_data.account,
            ticket_data.risk_assessment,
            escalation_criteria
        )
        
        response = webhook.send(text=message)
        notification_sent = response.status_code == 200
    
    # Return complete analysis with escalation decision
    return sandgarden.out(EscalationResponse(
        ticket=ticket_data.ticket,
        summary=ticket_data.summary,
        sentiment=ticket_data.sentiment,
        risk_assessment=ticket_data.risk_assessment,
        account=ticket_data.account,
        escalation=escalation_criteria,
        notification_sent=notification_sent
    ))
