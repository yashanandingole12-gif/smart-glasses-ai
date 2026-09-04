import pytest
from backend.app.services.entity_resolver import (
    EntityResolver,
    Contact,
    ResolutionStatus
)

@pytest.fixture
def custom_resolver():
    contacts = [
        Contact(name="Rahul Sharma", phone="+919876543210"),
        Contact(name="Rahul Verma", phone="+919876543219"),
        Contact(name="Sneha Patil", phone="+919876543211"),
        Contact(name="Vikram Singh", phone="+919876543214")
    ]
    return EntityResolver(contacts=contacts)

def test_high_confidence_exact_resolution(custom_resolver):
    """High confidence query should automatically resolve to unique contact."""
    res = custom_resolver.resolve_contact("Sneha Patil")
    assert res.status == ResolutionStatus.RESOLVED
    assert res.contact.name == "Sneha Patil"
    assert res.contact.phone == "+919876543211"
    assert res.confidence == 1.0

def test_name_normalization_with_honorifics(custom_resolver):
    """Query with honorifics like 'Sneha ji' or 'Sneha didi' should resolve to Sneha Patil."""
    res = custom_resolver.resolve_contact("Sneha ji")
    assert res.status == ResolutionStatus.RESOLVED
    assert res.contact.name == "Sneha Patil"

def test_ambiguous_multiple_contact_matches(custom_resolver):
    """Query matching multiple contacts (e.g. two Rahuls) must return AMBIGUOUS status."""
    res = custom_resolver.resolve_contact("Rahul")
    assert res.status == ResolutionStatus.AMBIGUOUS
    assert len(res.candidates) == 2
    assert "Rahul Sharma" in res.clarification_prompt
    assert "Rahul Verma" in res.clarification_prompt

def test_low_confidence_contact_not_found(custom_resolver):
    """Query with no close matches should return NOT_FOUND safely."""
    res = custom_resolver.resolve_contact("Zack Snyder")
    assert res.status == ResolutionStatus.NOT_FOUND
    assert res.contact is None
    assert "couldn't find" in res.clarification_prompt.lower()
