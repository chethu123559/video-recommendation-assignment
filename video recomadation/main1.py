import requests
import json

# Base URL and Authorization header
BASE_URL = "https://api.socialverseapp.com"
TOKEN = "flic_6e2d8d25dc29a4ddd382c2383a903cf4a688d1a117f6eb43b35a1e7fadbb84b8"
HEADERS = {
    "Flic-Token": TOKEN
}

# Helper function to fetch paginated data
def fetch_paginated_data(endpoint, params):
    all_data = []
    page = 1
    while True:
        params['page'] = page  # Set the page number dynamically
        response = requests.get(endpoint, headers=HEADERS, params=params)

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response for page {page}: {data}")  # Debugging line
                
                # Check if 'users' or 'posts' key exists and add the respective data to the list
                if 'users' in data:
                    all_data.extend(data['users'])
                elif 'posts' in data:
                    all_data.extend(data['posts'])
                else:
                    print("No relevant data ('users' or 'posts') in response:", data)
                    break

                # Check for the next page; assume 'next_page' is a key in the API response
                if 'next_page' in data and data['next_page']:
                    page += 1
                else:
                    break
            except ValueError:
                print(f"Failed to decode JSON response: {response.text}")
                break
        else:
            print(f"Failed to fetch data from {endpoint}, status code: {response.status_code}")
            break
    return all_data

# Example: Fetching all viewed posts
viewed_posts_params = {
    "page_size": 1000,
    "resonance_algorithm": "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
}
viewed_posts = fetch_paginated_data(f"{BASE_URL}/posts/view", viewed_posts_params)

# Example: Fetching all liked posts
liked_posts_params = {
    "page_size": 1000,
    "resonance_algorithm": "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
}
liked_posts = fetch_paginated_data(f"{BASE_URL}/posts/like", liked_posts_params)

# Example: Fetching all inspired posts
inspired_posts_params = {
    "page_size": 1000,
    "resonance_algorithm": "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
}
inspired_posts = fetch_paginated_data(f"{BASE_URL}/posts/inspire", inspired_posts_params)

# Example: Fetching all rated posts
rated_posts_params = {
    "page_size": 1000,
    "resonance_algorithm": "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
}
rated_posts = fetch_paginated_data(f"{BASE_URL}/posts/rating", rated_posts_params)

# Example: Fetching all posts
posts_params = {
    "page_size": 1000
}
all_posts = fetch_paginated_data(f"{BASE_URL}/posts/summary/get", posts_params)

# Example: Fetching all users
users_params = {
    "page_size": 1000  # Adjust as needed
}
all_users = fetch_paginated_data(f"{BASE_URL}/users/get_all", users_params)

# Debug: Check if data was fetched for users
print(f"Fetched all users: {len(all_users)} users found.")

# Save data to a JSON file
def save_data_to_json(filename, data):
    if data:  # Check if data is not empty
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {filename}")
    else:
        print(f"No data to save for {filename}")

# Save all fetched data to separate JSON files
save_data_to_json('viewed_posts.json', viewed_posts)
save_data_to_json('liked_posts.json', liked_posts)
save_data_to_json('inspired_posts.json', inspired_posts)
save_data_to_json('rated_posts.json', rated_posts)
save_data_to_json('all_posts.json', all_posts)
save_data_to_json('all_users.json', all_users)

print("Data fetching and saving process completed.")
