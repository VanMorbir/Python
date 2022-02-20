import json
from typing import List

import pytest
from django.urls import reverse
from api.techapp.companies.models import Company

companies_url = reverse("companies-list")
pytestmark = pytest.mark.django_db


# ----------- Test Get Companies --------
def test_zero_companies_should_return_empty_list(client) -> None:
    response = client.get(companies_url)
    assert response.status_code == 200
    assert json.loads(response.content) == []


@pytest.fixture
def amazon() -> Company:
    return Company.objects.create(name="Amazon")


def test_one_company_should_exist(client, amazon) -> None:
    response = client.get(companies_url)
    response_content = json.loads(response.content)[0]
    assert response.status_code == 200
    assert response_content.get("name") == amazon.name
    assert response_content.get("status") == "Hiring"
    assert response_content.get("application_link") == ""
    assert response_content.get("note") == ""


# ----------- Test Post Companies ------------
def test_create_company_without_name_should_fail(client) -> None:
    response = client.post(path=companies_url)
    assert response.status_code == 400
    assert json.loads(response.content), {"name": ["This field is required."]}


def test_create_existing_company_should_fail(client):
    test = Company.objects.create(name="Apple")
    response = client.post(path=companies_url, data={"name": "Apple"})
    assert response.status_code == 400
    assert json.loads(response.content) == {"name": ["company with this name already exists."]}


def test_create_company_with_only_name_all_fields_should_be_default(client) -> None:
    response = client.post(path=companies_url, data={"name": "test company name"})
    assert response.status_code == 201
    response_content = response.json()
    assert response_content.get("name") == "test company name"
    assert response_content.get("status") == "Hiring"
    assert response_content.get("application_link") == ""
    assert response_content.get("note") == ""


# ------------------- Fixture Test -----------
@pytest.fixture
def companies(request, company) -> List[Company]:
    companies = []
    names = request.param
    for name in names:
        companies.append(company(name=name))
    return companies


@pytest.fixture()
def company(**kwargs):
    def _company_factory(**kwargs) -> Company:
        name = kwargs.pop("name", "Test Company INC")
        return Company.objects.create(name=name, **kwargs)

    return _company_factory


@pytest.mark.parametrize("companies", [["tiktok", "twitch", "test company"], ["facebook", "instagram"]], indirect=True)
def test_multiple_companies_should_succeed(client, companies) -> None:
    names = set(map(lambda x: x.name, companies))
    response = client.get(path=companies_url).json()
    assert len(names) == len(response)
    response_names = set(map(lambda company: company.get("name"), response))
    assert names == response_names
