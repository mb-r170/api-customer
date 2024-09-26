import requests

def test_get_wrong_table(base_url):
    table_name = "wrong_table"
    response = requests.get(f"{base_url}/api/v1/stats/{table_name}")
    assert response.status_code == 404, f"Response text: {response.text}"

def test_number_of_customers(base_url):
    table_name = "customers"
    response = requests.get(f"{base_url}/api/v1/stats/{table_name}")
    assert response.status_code == 200, f"Response text: {response.text}"
    assert response.json()["rows"] > 0, f"Response text: {response.text}"