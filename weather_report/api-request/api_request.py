import requests

# api_url = "http://api.weatherstack.com/current?access_key=c212c361303fc100bf1eb60efada4691&query=New York"
api_url = ""
def fetch_data():
    try:
        print(f"Fetching weather result")
        response = requests.get(api_url)
        response.raise_for_status()
        print(f"Response fetched successfully", response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching data: {e}")
        raise

fetch_data()        