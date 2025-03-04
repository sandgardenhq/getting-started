from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import json

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

class TicketInput(BaseModel):
    ticket: Ticket
    summary: str

def handler(input, sandgarden):
    """
    Analyze customer sentiment from support ticket content.

    This handler processes a support ticket to:
    1. Extract customer communication tone and emotion
    2. Identify key sentiment indicators
    3. Assess urgency and satisfaction levels
    4. Highlight important phrases indicating customer state

    Args:
        input: Dict containing ticket data and summary
        sandgarden: SandGarden context with connectors and prompts
        runtime_context: Runtime execution context

    Returns:
        Dict containing sentiment analysis results including:
        - Overall sentiment classification
        - Confidence score
        - Key emotional indicators
        - Urgency assessment
    """
    # Parse input
    ticket_data = TicketInput(**input)
    
    # Load accounts data
    with open('accounts.json') as f:
        accounts_data = json.load(f)
    
    # Find matching account
    account = None
    org_name = ticket_data.ticket.get('organization')
    if org_name:
        account = next(
            (Account(**acc) for acc in accounts_data['accounts'] 
             if acc['name'] == org_name),
            None
        )
    
    # Get LLM client and prompt
    llm = sandgarden.get_connector('ticket-summarizer-model')
    prompt = sandgarden.get_prompt('analyze-ticket-sentiment')

    # Prepare content for analysis
    # TODO: make account info optional
    analysis_content = f"""
Ticket Content:
{ticket_data.ticket.get('description', 'No description provided')}

Summary:
{ticket_data.summary}

Additional Context:
- Priority: {ticket_data.ticket.get('priority', 'Not set')}
- Status: {ticket_data.ticket.get('status', 'Unknown')}
- Tags: {', '.join(ticket_data.ticket.get('tags', []))}

Account Information:
- Name: {account.name if account else 'Unknown'}
- Tier: {account.tier if account else 'Unknown'}
- Support Level: {account.support_level if account else 'Unknown'}
- Industry: {account.industry if account else 'Unknown'}
- Annual Contract Value: ${f"{account.acv:,}" if account else 'Unknown'}
- Critical Systems: {', '.join(account.critical_systems) if account else 'Unknown'}
- Region: {account.region if account else 'Unknown'}
"""
    
    # Get structured sentiment analysis from LLM
    sentiment_data = llm.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": analysis_content}
        ],
        response_format=SentimentAnalysis
    ).choices[0].message.parsed
    
    # Return validated response with JSON serialization
    return sandgarden.out(TicketSentimentResponse(
        ticket=ticket_data.ticket,
        analysis=sentiment_data,  # Already a SentimentAnalysis instance
        account=account
    ))
