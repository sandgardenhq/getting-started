from datetime import datetime, timezone
from pydantic import BaseModel
from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket

class TicketInput(BaseModel):
    last_run_time: datetime | None = None
    zendesk_subdomain: str
    zendesk_email: str
    zendesk_token: str

def handler(input, sandgarden, runtime_context):
    """
    Summarize ticket content and enrich with relevant metadata
    """
    # Parse input
    ticket_input = TicketInput(**input)
    
    # Initialize Zendesk client
    credentials = {
        'email': ticket_input.zendesk_email,
        'token': ticket_input.zendesk_token,
        'subdomain': ticket_input.zendesk_subdomain
    }
    zendesk = Zenpy(**credentials)
    
    # Get tickets created or updated since last run
    query_time = ticket_input.last_run_time or datetime.now(timezone.utc)
    new_tickets = zendesk.search(
        type='ticket',
        created_greater_than=query_time.isoformat()
    )
    
    # Process each ticket
    processed_tickets = []
    for ticket in new_tickets:
        ticket_data = {
            'id': ticket.id,
            'subject': ticket.subject,
            'description': ticket.description,
            'status': ticket.status,
            'priority': ticket.priority,
            'created_at': ticket.created_at,
            'updated_at': ticket.updated_at,
            'requester_id': ticket.requester_id,
            'assignee_id': ticket.assignee_id if hasattr(ticket, 'assignee_id') else None
        }
        processed_tickets.append(ticket_data)
    
    return {
        'tickets': processed_tickets,
        'last_run_time': datetime.now(timezone.utc).isoformat()
    }
