import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# GitHub API configuration
GITHUB_API_BASE_URL = 'https://api.github.com'
ORGANIZATION = 'your-organization'
GITHUB_TOKEN = 'your-github-token'


@app.route('/search', methods=['POST'])
def search():
    # Parse the search request from Grafana
    req_data = request.get_json()
    target = req_data['target']

    # Perform the search based on the target (label)
    results = search_repositories(target)

    # Return the search results in the expected format
    response = []
    for result in results:
        response.append({
            'text': result,
            'value': result
        })
    return jsonify(response)


@app.route('/query', methods=['POST'])
def query():
    # Parse the query request from Grafana
    req_data = request.get_json()
    target = req_data['targets'][0]['target']

    # Perform the query based on the target (label)
    count = get_repositories_with_label(target)

    # Return the query result in the expected format
    response = [[1, count]]  # Assuming a single timestamp with the count as the value
    return jsonify(response)


def search_repositories(label):
    # Perform the search operation based on the label
    # Customize this logic as per your requirements
    headers = {
        'Authorization': f'Token {GITHUB_TOKEN}'
    }
    params = {
        'q': f'org:{ORGANIZATION} label:"{label}"'
    }
    url = f'{GITHUB_API_BASE_URL}/search/repositories'
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    repositories = [repo['name'] for repo in data['items']]
    return repositories


def get_repositories_with_label(label):
    # Get the count of repositories with the specified label
    # Customize this logic as per your requirements
    headers = {
        'Authorization': f'Token {GITHUB_TOKEN}'
    }
    params = {
        'q': f'org:{ORGANIZATION} label:"{label}"'
    }
    url = f'{GITHUB_API_BASE_URL}/search/repositories'
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    count = data['total_count']
    return count


if __name__ == '__main__':
    app.run()