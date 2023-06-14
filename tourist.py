import pytest
import requests
from datetime import datetime
import allure

base_url = "http://restapi.adequateshop.com"
random_id = datetime.now().strftime("%Y%m%d%H%M%S")


@pytest.fixture
def login_data():
    return {
        "email": "test@test.com",
        "password": "testpass"
    }


@pytest.fixture
def create_tourist():
    create_url = base_url + "/api/Tourist"
    create_payload = {
        "tourist_name": f"user{random_id}",
        "tourist_email": f"email{random_id}@email.com",
        "tourist_location": "Terra",
        "createdat": "2023-06-14T11:59:58.024Z"
    }
    response = requests.post(create_url, json=create_payload)
    tourist_id = response.json()["id"]

    yield tourist_id
    # Cleanup
    delete_url = base_url + f"/api/Tourist/{tourist_id}"
    requests.delete(delete_url)


@allure.title("Login is successful")
def test_login_ok(login_data):
    url = base_url + "/api/AuthAccount/Login"
    response = requests.post(url, json=login_data)

    assert response.status_code == 200


@allure.title("Login with invalid credentials")
def test_login_invalid_credentials():
    url = base_url + "/api/AuthAccount/Login"
    payload = {
        "email": "invalid_email",
        "password": "invalid_password"
    }
    response = requests.post(url, json=payload)

    assert response.status_code == 200
    assert response.json()["code"] == 1
    assert response.json()["message"] == "invalid username or password"
    assert response.json()["data"] is None


@allure.title("Login with empty credentials")
def test_login_empty():
    url = base_url + "/api/AuthAccount/Login"
    payload = {
        "email": "",
        "password": ""
    }
    response = requests.post(url, json=payload)

    assert response.status_code == 400
    response_json = response.json()
    assert response_json["Message"] == "The request is invalid."
    assert response_json["ModelState"]["log.email"] == ["field is required"]
    assert response_json["ModelState"]["log.password"] == ["field is required"]


@allure.title("Get Tourist by ID")
def test_get_tourist_ok(create_tourist):
    tourist_id = create_tourist
    get_url = base_url + f"/api/Tourist/{tourist_id}"
    with allure.step(f"Get tourist with ID: {tourist_id}"):
        response = requests.get(get_url)

    assert response.status_code == 200
    assert response.json()["id"] == tourist_id
    assert response.json()["tourist_name"] == f"user{random_id}"
    assert response.json()["tourist_email"] == f"email{random_id}@email.com"
    assert response.json()["tourist_location"] == "Terra"


@allure.title("Tourist not found")
def test_get_nonexistent_tourist():
    tourist_id = "nonexistent_id"
    get_url = base_url + f"/api/Tourist/{tourist_id}"
    with allure.step(f"Get tourist with ID: {tourist_id}"):
        response = requests.get(get_url)

    assert response.status_code == 400
    assert response.json()["Message"] == "The request is invalid."