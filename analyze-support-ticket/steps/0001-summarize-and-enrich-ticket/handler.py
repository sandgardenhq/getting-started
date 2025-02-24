from pydantic import BaseModel
from datetime import datetime

class TicketInput(BaseModel):
    id: int
    subject: str
    description: str | None
    status: str
    priority: str | None
    created_at: datetime
    updated_at: datetime
    requester_id: int
    assignee_id: int | None

def handler(input, sandgarden, runtime_context):
    """
    Summarize ticket content and enrich with relevant metadata
    """
    # Parse input
    ticket = TicketInput(**input)
    
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
        'assignee_id': ticket.assignee_id
    }
    
    return ticket_data
