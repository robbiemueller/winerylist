import requests
import json

def load_config():
    """Load API key from a configuration file."""
    with open('config.json', 'r') as file:
        data = json.load(file)
        return data['GOOGLE_API_KEY']

def get_location(zip_code, api_key):
    """Get latitude and longitude from zip code."""
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {'address': zip_code, 'key': api_key}
    response = requests.get(base_url, params=params).json()
    location = response['results'][0]['geometry']['location']
    return (location['lat'], location['lng'])

def calculate_distance(origins, destinations, api_key):
    """Calculate distance between two points using the Distance Matrix API."""
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        'origins': f"{origins[0]},{origins[1]}",
        'destinations': f"{destinations[0]},{destinations[1]}",
        'key': api_key,
        'units': 'imperial'  # For miles, use 'metric' for kilometers.
    }
    response = requests.get(base_url, params=params).json()
    if response['status'] == 'OK':
        result = response['rows'][0]['elements'][0]
        if result['status'] == 'OK':
            distance = result['distance']['text']
            return distance
    return 'N/A'

def find_wineries(lat, lng, api_key):
    """Find wineries near the given latitude and longitude and sort them by distance."""
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': f'{lat},{lng}',
        'radius': 50000,  # Search within 10 kilometers
        'type': 'establishment',
        'keyword': 'winery',
        'key': api_key
    }
    response = requests.get(base_url, params=params).json()
    wineries = []
    for place in response['results']:
        name = place['name']
        address = place['vicinity']
        place_location = (place['geometry']['location']['lat'], place['geometry']['location']['lng'])
        distance = calculate_distance((lat, lng), place_location, api_key)
        wineries.append({
            'name': name,
            'address': address,
            'distance': distance
        })
    
    # Sort the wineries by distance
    wineries.sort(key=lambda x: float(x['distance'].split()[0]))
    return wineries

def main():
    api_key = load_config()
    zip_code = input("Enter your zip code: ")
    lat, lng = get_location(zip_code, api_key)
    wineries = find_wineries(lat, lng, api_key)
    if wineries:
        for winery in wineries:
            print(f"{winery['name']} - {winery['address']} - {winery['distance']}")
    else:
        print("No wineries found within the search radius.")

if __name__ == "__main__":
    main()
