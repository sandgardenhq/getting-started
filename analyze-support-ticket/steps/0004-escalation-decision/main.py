from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from slack_sdk.webhook import WebhookClient
from datetime import datetime, timezone

class EscalationCriteria(BaseModel):
    should_escalate: bool
    reasons: List[str]
    recommended_actions: List[str]
    priority_level: str  # critical, high, medium, low
    response_sla: str  # immediate, 4 hours, 24 hours, etc.

class EscalationResponse(BaseModel):
    ticket: dict
    summary: str
    sentiment: dict
    risk_assessment: dict
    account: Optional[Dict] = None
    escalation: EscalationCriteria
    notification_sent: bool = False

class TicketInput(BaseModel):
    ticket: dict
    summary: str
    sentiment: dict
    risk_assessment: dict
    account: Optional[Dict] = None

def format_notification(ticket: dict, account: Optional[Dict], risk_assessment: dict, escalation: EscalationCriteria) -> str:
    """Format the Slack notification message."""
    account_info = account or {}
    risk_level = risk_assessment.get('risk_level', 'Unknown').upper()
    priority_score = risk_assessment.get('priority_score', 0)
    
    # Calculate duration since ticket creation
    created_at = datetime.fromisoformat(ticket.get('created_at', '').replace('Z', '+00:00'))
    duration = datetime.now(timezone.utc) - created_at
    duration_hours = duration.total_seconds() / 3600
    duration_str = f"{int(duration_hours)}+ hours" if duration_hours >= 1 else f"{int(duration.total_seconds() / 60)} minutes"
    
    # Truncate description and add ellipsis if needed
    description = ticket.get('description', 'No description')
    if len(description) > 100:
        description = description[:97] + "..."
    
    return f"""🚨 {escalation.priority_level.upper()} TICKET - IMMEDIATE ACTION REQUIRED

Customer: {account_info.get('name', 'Unknown')}
Revenue Impact: ${account_info.get('acv', 0):,} ARR
Churn Risk: {risk_level} {'🔥' if risk_level == 'HIGH' else '⚠️'}

Issue: {ticket.get('subject', 'No subject')}
Duration: {duration_str}
Impact: {description}
Context: Priority Score {priority_score}/100
Urgency: {escalation.response_sla}

AI Analysis: {', '.join(escalation.reasons)}

View in Zendesk: {ticket.get('url', '[No URL]')}
Escalate to On-Call: [Click to Page]"""

async def handler(input, sandgarden, runtime_context):
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
    llm = sandgarden.connectors['escalation-analyzer-model']
    prompt = sandgarden.prompts('assess-escalation')
    
    # Prepare content for analysis
    analysis_content = f"""
Ticket Summary:
{ticket_data.summary}

Risk Assessment:
- Risk Level: {ticket_data.risk_assessment.get('risk_level', 'Unknown')}
- Priority Score: {ticket_data.risk_assessment.get('priority_score', 0)}/100
- Risk Factors: {', '.join(ticket_data.risk_assessment.get('risk_factors', {}).get('technical_factors', []))}
- Recommendations: {', '.join(ticket_data.risk_assessment.get('recommendations', []))}

Account Impact:
{f'''- Annual Value: ${ticket_data.account['acv']:,}
- Tier: {ticket_data.account['tier']}
- Support Level: {ticket_data.account['support_level']}
- Critical Systems: {', '.join(ticket_data.account['critical_systems'])}''' if ticket_data.account else '- No account information available'}

Sentiment Analysis:
- Overall: {ticket_data.sentiment.get('sentiment', 'Unknown')}
- Urgency: {ticket_data.sentiment.get('urgency_level', 'Unknown')}
- Key Indicators: {', '.join(ticket_data.sentiment.get('emotion_indicators', []))}
"""
    
    # Get structured escalation assessment from LLM
    escalation_criteria = await llm.beta.chat.completions.parse(
        prompt=prompt,
        messages=[{"role": "user", "content": analysis_content}],
        response_format=EscalationCriteria
    )
    
    # Send notification if escalation is needed
    notification_sent = False
    if escalation_criteria.should_escalate:
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
    return EscalationResponse(
        ticket=ticket_data.ticket,
        summary=ticket_data.summary,
        sentiment=ticket_data.sentiment,
        risk_assessment=ticket_data.risk_assessment,
        account=ticket_data.account,
        escalation=escalation_criteria,
        notification_sent=notification_sent
    ).model_dump(mode='json')
