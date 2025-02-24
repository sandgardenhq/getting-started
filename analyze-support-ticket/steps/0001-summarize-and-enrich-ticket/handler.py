from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TicketInput(BaseModel):
    id: int
    subject: str
    description: Optional[str] = None
    status: str
    priority: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    requester_id: int
    assignee_id: Optional[int] = None

async def handler(input, sandgarden, runtime_context):
    """
    Summarize ticket content and enrich with relevant metadata
    """
    # Parse input
    ticket = TicketInput(**input)
    
    # Get LLM client and prompt
    llm = sandgarden.connectors['ticket-summarizer-model']
    prompt = sandgarden.prompts('summarize-ticket')
    
    # Prepare ticket content for summarization
    ticket_content = f"Subject: {ticket.subject}\n\nDescription: {ticket.description or 'No description provided'}"
    
    # Get summary from LLM
    response = await llm.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": ticket_content}
        ]
    )
    summary = response.choices[0].message.content
    
    # Process the ticket
    ticket_data = {
        'id': ticket.id,
        'subject': ticket.subject,
        'description': ticket.description,
        'status': ticket.status,
        'priority': ticket.priority,
        'created_at': ticket.created_at.isoformat(),
        'updated_at': ticket.updated_at.isoformat(),
        'requester_id': ticket.requester_id,
        'assignee_id': ticket.assignee_id,
        'summary': summary
    }
    
    return ticket_data
