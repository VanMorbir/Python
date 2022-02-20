import json

import pytest
from django.test import Client
from django.urls import reverse
from django.test import TestCase
from api.techapp.companies.models import Company


@pytest.mark.django_db
class BasicCompanyAPITestCase(TestCase):
    def setup(self):
        self.url = reverse("companies-list")
        self.client = Client()

    def tearDown(self) -> None:
        pass


class TestGetCompanies(BasicCompanyAPITestCase):

    def test_zero_companies_should_return_empty_list(self) -> None:
        companies_url = reverse("companies-list")
        response = self.client.get(companies_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])

    def test_one_company_should_exist(self) -> None:
        test_company = Company.objects.create(name="Amazon")
        companies_url = reverse("companies-list")
        response = self.client.get(companies_url)
        response_content = json.loads(response.content)[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content.get("name"), test_company.name)
        self.assertEqual(response_content.get("status"), "Hiring")
        self.assertEqual(response_content.get("application_link"), "")
        self.assertEqual(response_content.get("note"), "")
        test_company.delete()


class TestPostCompanies(BasicCompanyAPITestCase):
    def test_create_company_without_name_should_fail(self) -> None:
        companies_url = reverse("companies-list")
        response = self.client.post(path=companies_url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {"name": ["This field is required."]})

    def test_create_existing_company_should_fail(self):
        test = Company.objects.create(name="Apple")
        companies_url = reverse("companies-list")
        response = self.client.post(path=companies_url, data={"name":"Apple"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {"name": ["company with this name already exists."]})

    def test_create_company_with_only_name_all_fields_should_be_default(self) -> None:
        companies_url = reverse("companies-list")
        response = self.client.post(path=companies_url, data={"name": "test company name"})
        self.assertEqual(response.status_code, 201)
        response_content = response.json()
        self.assertEqual(response_content.get("name"), "test company name")
        self.assertEqual(response_content.get("status"), "Hiring")
        self.assertEqual(response_content.get("application_link"), "")
        self.assertEqual(response_content.get("note"), "")

