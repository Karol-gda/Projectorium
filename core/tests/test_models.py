import pytest
from django.contrib.auth.models import User
from projekty.models import Project

@pytest.mark.django_db
def test_create_project():
    user = User.objects.create(username="testuser")
    project = Project.objects.create(
        internal_number="ABC123",
        title="Testowy projekt",
        principal_investigator=user,
        pi_email="pi@example.com",
        pi_phone="123456789",
        project_type="IND",
        project_leader="Dr. Test",
        funding_agency="NCN",
        call_name="Konkurs 2025",
        funding_decision_date="2025-01-01",
        funding_number="NCN-001",
        agreement_number="AG-001",
        agreement_sign_date="2025-01-15",
        start_date="2025-02-01T00:00:00Z",
        end_date="2026-02-01T00:00:00Z",
        executing_unit="Jednostka A",
        budget_total=100000.00,
        project_support=user
    )
    assert Project.objects.count() == 1
    assert project.title == "Testowy projekt"
