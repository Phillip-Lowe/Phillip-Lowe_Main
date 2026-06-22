from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict, field_validator
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, Text, DateTime, ForeignKey, JSON, text, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy.sql import func
from typing import Optional, List
from datetime import datetime, date as dt_date
import json

# Database configuration
DATABASE_URL = "postgresql://systack:systackpass@postgres:5432/crm"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================================
# SQLAlchemy Models
# ============================================================================

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    website = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    leads = relationship("Lead", back_populates="client", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="client", cascade="all, delete-orphan")


class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    source = Column(String(100))
    status = Column(String(50), default="new")
    notes = Column(Text)
    score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    client = relationship("Client", back_populates="leads")
    contacts = relationship("Contact", back_populates="lead", cascade="all, delete-orphan")


class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    role = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    lead = relationship("Lead", back_populates="contacts")


class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    invoice_number = Column(String(100), nullable=False, unique=True)
    total = Column(Numeric(12, 2), nullable=False, default=0.00)
    date = Column(Date, nullable=False, server_default=func.current_date())
    vendor = Column(String(255))
    line_items = Column(JSON, default=list)
    status = Column(String(50), default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    client = relationship("Client", back_populates="invoices")


# ============================================================================
# Pydantic Models
# ============================================================================

# --- Clients ---
class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)

class ClientResponse(ClientBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


# --- Leads ---
class LeadBase(BaseModel):
    client_id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field("new", max_length=50)
    notes: Optional[str] = None
    score: Optional[int] = Field(0, ge=0, le=100)

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    client_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    score: Optional[int] = Field(None, ge=0, le=100)

class LeadResponse(LeadBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class LeadUpsert(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    score: Optional[int] = Field(None, ge=0, le=100)

class LeadUpsertResponse(BaseModel):
    action: str
    lead_id: int
    lead: LeadResponse


# --- Contacts ---
class ContactBase(BaseModel):
    lead_id: int
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, max_length=100)

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    lead_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, max_length=100)

class ContactResponse(ContactBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


# --- Invoices ---
class InvoiceLineItem(BaseModel):
    description: str
    quantity: int = Field(..., ge=0)
    unit_price: float = Field(..., ge=0)
    amount: Optional[float] = None

class InvoiceBase(BaseModel):
    client_id: Optional[int] = None
    invoice_number: str = Field(..., min_length=1, max_length=100)
    total: float = Field(..., ge=0)
    date: Optional[str] = None
    vendor: Optional[str] = Field(None, max_length=255)
    line_items: List[InvoiceLineItem] = Field(default_factory=list)
    status: Optional[str] = Field("draft", max_length=50)

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    client_id: Optional[int] = None
    invoice_number: Optional[str] = Field(None, min_length=1, max_length=100)
    total: Optional[float] = Field(None, ge=0)
    date: Optional[str] = None
    vendor: Optional[str] = Field(None, max_length=255)
    line_items: Optional[List[InvoiceLineItem]] = None
    status: Optional[str] = Field(None, max_length=50)

class InvoiceResponse(InvoiceBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime
    
    @field_validator('date', mode='before')
    @classmethod
    def validate_date(cls, v):
        if v is None:
            return None
        if isinstance(v, dt_date):
            return v.isoformat()
        return v


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Systack CRM API",
    description="FastAPI CRUD backend for Systack automation agency CRM",
    version="1.0.0"
)

# Dependency: DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# Health Check
# ============================================================================

@app.get("/")
def read_root():
    return {"message": "Systack API is running"}

@app.get("/health")
def health_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database unhealthy: {str(e)}")


# ============================================================================
# Clients CRUD
# ============================================================================

@app.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@app.get("/clients", response_model=List[ClientResponse])
def list_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Client).offset(skip).limit(limit).all()

@app.get("/clients/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client

@app.put("/clients/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, client_update: ClientUpdate, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    
    update_data = client_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    return client

@app.delete("/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    db.delete(client)
    db.commit()
    return None


# ============================================================================
# Leads CRUD
# ============================================================================

@app.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    if lead.client_id:
        client = db.query(Client).filter(Client.id == lead.client_id).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced client not found")
    db_lead = Lead(**lead.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

@app.get("/leads", response_model=List[LeadResponse])
def list_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Lead).offset(skip).limit(limit).all()

@app.get("/leads/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead

@app.put("/leads/{lead_id}", response_model=LeadResponse)
def update_lead(lead_id: int, lead_update: LeadUpdate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    
    update_data = lead_update.model_dump(exclude_unset=True)
    if "client_id" in update_data and update_data["client_id"] is not None:
        client = db.query(Client).filter(Client.id == update_data["client_id"]).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced client not found")
    
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    db.commit()
    db.refresh(lead)
    return lead

@app.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    db.delete(lead)
    db.commit()
    return None


# ============================================================================
# Leads Upsert (Webhook)
# ============================================================================

@app.post("/webhook/leads/upsert", response_model=LeadUpsertResponse, status_code=status.HTTP_200_OK)
def upsert_lead(payload: LeadUpsert, db: Session = Depends(get_db)):
    """
    Upsert a lead by email. Creates if not found, updates if exists.
    """
    lead = db.query(Lead).filter(Lead.email == payload.email).first()
    
    if lead:
        # UPDATE existing lead
        if payload.name is not None:
            lead.name = payload.name
        if payload.phone is not None:
            lead.phone = payload.phone
        if payload.source is not None:
            lead.source = payload.source
        if payload.score is not None:
            lead.score = payload.score
        if payload.notes is not None:
            if lead.notes:
                lead.notes = f"{lead.notes}\n\n{payload.notes}"
            else:
                lead.notes = payload.notes
        
        db.commit()
        db.refresh(lead)
        return LeadUpsertResponse(action="updated", lead_id=lead.id, lead=LeadResponse.model_validate(lead))
    else:
        # CREATE new lead
        db_lead = Lead(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            source=payload.source,
            notes=payload.notes,
            score=payload.score if payload.score is not None else 0,
            status="new"
        )
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
        return LeadUpsertResponse(action="created", lead_id=db_lead.id, lead=LeadResponse.model_validate(db_lead))


# ============================================================================
# Contacts CRUD
# ============================================================================

@app.post("/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == contact.lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced lead not found")
    db_contact = Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.get("/contacts", response_model=List[ContactResponse])
def list_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Contact).offset(skip).limit(limit).all()

@app.get("/contacts/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, contact_update: ContactUpdate, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    
    update_data = contact_update.model_dump(exclude_unset=True)
    if "lead_id" in update_data and update_data["lead_id"] is not None:
        lead = db.query(Lead).filter(Lead.id == update_data["lead_id"]).first()
        if not lead:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced lead not found")
    
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    db.commit()
    db.refresh(contact)
    return contact

@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return None


# ============================================================================
# Invoices CRUD
# ============================================================================

@app.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    if invoice.client_id:
        client = db.query(Client).filter(Client.id == invoice.client_id).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced client not found")
    
    # Check unique invoice_number
    existing = db.query(Invoice).filter(Invoice.invoice_number == invoice.invoice_number).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invoice number already exists")
    
    db_invoice = Invoice(
        client_id=invoice.client_id,
        invoice_number=invoice.invoice_number,
        total=invoice.total,
        date=invoice.date,
        vendor=invoice.vendor,
        line_items=[item.model_dump() for item in invoice.line_items],
        status=invoice.status
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

@app.get("/invoices", response_model=List[InvoiceResponse])
def list_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Invoice).offset(skip).limit(limit).all()

@app.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice

@app.put("/invoices/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(invoice_id: int, invoice_update: InvoiceUpdate, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    
    update_data = invoice_update.model_dump(exclude_unset=True)
    
    if "client_id" in update_data and update_data["client_id"] is not None:
        client = db.query(Client).filter(Client.id == update_data["client_id"]).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced client not found")
    
    if "invoice_number" in update_data and update_data["invoice_number"] is not None:
        existing = db.query(Invoice).filter(
            Invoice.invoice_number == update_data["invoice_number"],
            Invoice.id != invoice_id
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invoice number already exists")
    
    if "line_items" in update_data and update_data["line_items"] is not None:
        update_data["line_items"] = [item.model_dump() for item in update_data["line_items"]]
    
    for field, value in update_data.items():
        setattr(invoice, field, value)
    
    db.commit()
    db.refresh(invoice)
    return invoice

@app.delete("/invoices/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    db.delete(invoice)
    db.commit()
    return None
