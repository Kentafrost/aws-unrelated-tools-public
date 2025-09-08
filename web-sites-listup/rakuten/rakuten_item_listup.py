import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import csv

# Disable SSL warnings for debugging (optional)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://rakuten_webservice-rakuten-marketplace-product-search-v1.p.rapidapi.com/services/api/Product/Search/20170426"

# Add query parameters for the search
params = {
    'keyword': 'モデルガン',  # Model gun keyword
    'format': 'json',
    'elements': 'productName,productPrice,productUrl,imageUrl',
    'page': '1',
    'hits': '30'  # Number of results
}

headers = {
	"x-rapidapi-key": "b36cb36eedmsh0785bc594a50608p17069djsn6f651a5811e5",
	"x-rapidapi-host": "rakuten_webservice-rakuten-marketplace-product-search-v1.p.rapidapi.com"
}

# Create session with retry strategy and SSL configuration
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(f'{current_dir}/results', "rakuten_products.csv")
if not os.path.exists(f'{current_dir}/results'):
    os.makedirs(f'{current_dir}/results')


def list_up(result):
    csv_data = []
    print(result.get('products', []))

    # Display first few products
    for i, product in enumerate(result.get('products', [])[:3]):
        name = product.get('productName', 'N/A')
        price = product.get('productPrice', 'N/A')
        url = product.get('productUrl', 'N/A')
        
        csv_data.append([name, price, url])

    # Write to CSV file
    with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Price', 'URL'])
        writer.writerows(csv_data)

    print(f"✅ {len(csv_data)} products listed up successfully!")

# Method 1: Try with verify=False (bypasses SSL verification)
try:
    response = session.get(url, headers=headers, params=params, verify=False, timeout=30)
    print("✅ SSL verification bypassed - Response received!")
    if response.status_code == 200:
        result = response.json()
        list_up(result)
    else:
        print("Response Text:", response.text)
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
    
    # Method 2: Try with different URL (direct RapidAPI endpoint)  
    try:
        print("\n🔄 Trying alternative approach...")
        alt_url = "https://rakuten-web-service.p.rapidapi.com/services/api/Product/Search/20170426"
        alt_headers = {
            "X-RapidAPI-Key": "b36cb36eedmsh0785bc594a50608p17069djsn6f651a5811e5",
            "X-RapidAPI-Host": "rakuten-web-service.p.rapidapi.com"
        }
        
        response = session.get(alt_url, headers=alt_headers, params=params, verify=False, timeout=30)
        print("✅ Alternative URL worked!")
        print("Status Code:", response.status_code)
        if response.status_code == 200:
            result = response.json()
            list_up(result)
        else:
            print("Response Text:", response.text)
            
    except requests.exceptions.RequestException as e2:
        print(f"❌ Alternative method also failed: {e2}")
        print("\n💡 Solutions to try:")
        print("1. Check if your RapidAPI subscription is active")
        print("2. Verify the API endpoint URL in RapidAPI dashboard") 
        print("3. Update your API key if needed")
        print("4. Try using curl or Postman to test the endpoint directly")