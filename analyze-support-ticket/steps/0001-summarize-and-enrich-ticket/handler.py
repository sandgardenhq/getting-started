from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class CustomField(BaseModel):
    id: int
    value: str

class SatisfactionRating(BaseModel):
    comment: Optional[str] = None
    id: int
    score: str

class Via(BaseModel):
    channel: str

class TicketResponse(BaseModel):
    id: int
    subject: str
    raw_subject: Optional[str] = None
    description: Optional[str] = None
    status: str
    priority: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    requester_id: int
    submitter_id: int
    assignee_id: Optional[int] = None
    organization_id: Optional[int] = None
    group_id: Optional[int] = None
    collaborator_ids: List[int] = Field(default_factory=list)
    follower_ids: List[int] = Field(default_factory=list)
    email_cc_ids: List[int] = Field(default_factory=list)
    custom_fields: List[CustomField] = Field(default_factory=list)
    satisfaction_rating: Optional[SatisfactionRating] = None
    sharing_agreement_ids: List[int] = Field(default_factory=list)
    custom_status_id: Optional[int] = None
    type: Optional[str] = None
    url: Optional[str] = None
    external_id: Optional[str] = None
    via: Optional[Via] = None
    tags: List[str] = Field(default_factory=list)
    has_incidents: bool = False
    due_at: Optional[datetime] = None
    problem_id: Optional[int] = None
    from_messaging_channel: bool = False
    generated_timestamp: Optional[int] = None
    recipient: Optional[str] = None

class TicketSummaryResponse(BaseModel):
    ticket: TicketResponse
    summary: str

class TicketInput(BaseModel):
    id: int
    subject: str
    raw_subject: Optional[str] = None
    description: Optional[str] = None
    status: str
    priority: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    requester_id: int
    submitter_id: int
    assignee_id: Optional[int] = None
    organization_id: Optional[int] = None
    group_id: Optional[int] = None
    collaborator_ids: List[int] = Field(default_factory=list)
    follower_ids: List[int] = Field(default_factory=list)
    email_cc_ids: List[int] = Field(default_factory=list)
    custom_fields: List[CustomField] = Field(default_factory=list)
    satisfaction_rating: Optional[SatisfactionRating] = None
    sharing_agreement_ids: List[int] = Field(default_factory=list)
    custom_status_id: Optional[int] = None
    type: Optional[str] = None
    url: Optional[str] = None
    external_id: Optional[str] = None
    via: Optional[Via] = None
    tags: List[str] = Field(default_factory=list)
    has_incidents: bool = False
    due_at: Optional[datetime] = None
    problem_id: Optional[int] = None
    from_messaging_channel: bool = False
    generated_timestamp: Optional[int] = None
    recipient: Optional[str] = None

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
    
    # Return validated response
    return TicketSummaryResponse(
        ticket=TicketResponse(
            id=ticket.id,
            subject=ticket.subject,
            description=ticket.description,
            status=ticket.status,
            priority=ticket.priority,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            requester_id=ticket.requester_id,
            assignee_id=ticket.assignee_id
        ),
        summary=summary
    ).model_dump()
