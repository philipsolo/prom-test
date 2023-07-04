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

    # Perform the search based on the target (topic)
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

    # Perform the query based on the target (topic)
    count = get_repositories_with_topic(target)

    # Return the query result in the expected format
    response = [
        {
            'target': target,
            'datapoints': [
                [count, int(time.time()) * 1000]  # Assuming current timestamp with the count as the value
            ]
        }
    ]
    return jsonify(response)


@app.route('/annotations', methods=['POST'])
def annotations():
    # Parse the annotations request from Grafana
    req_data = request.get_json()

    # Perform the annotations operation
    annotations = []
    for annotation in req_data:
        target = annotation['target']
        count = get_repositories_with_topic(target)
        annotations.append({
            'annotation': annotation['annotation'],
            'time': annotation['time'],
            'title': f'Repositories with topic "{target}"',
            'text': f'Total count: {count}'
        })

    # Return the annotations in the expected format
    return jsonify(annotations)


def search_repositories(topic):
    # Perform the search operation based on the topic
    # Customize this logic as per your requirements
    headers = {
        'Authorization': f'Token {GITHUB_TOKEN}'
    }
    params = {
        'q': f'org:{ORGANIZATION} topic:"{topic}"'
    }
    url = f'{GITHUB_API_BASE_URL}/search/repositories'
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    repositories = [repo['name'] for repo in data['items']]
    return repositories


def get_repositories_with_topic(topic):
    # Get the count of repositories with the specified topic
    # Customize this logic as per your requirements
    headers = {
        'Authorization': f'Token {GITHUB_TOKEN}'
    }
    params = {
        'q': f'org:{ORGANIZATION} topic:"{topic}"'
    }
    url = f'{GITHUB_API_BASE_URL}/search/repositories'
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    count = data['total_count']
    return count


import requests

# Set your GitHub personal access token
access_token = '<YOUR_ACCESS_TOKEN>'

# Set the specific topic you want to query
topic = '<TOPIC>'

# Make the GraphQL query to fetch repositories under the topic
query = '''
{
  search(query: "topic:{}", type: REPOSITORY, first: 100) {
    edges {
      node {
        ... on Repository {
          name
          defaultBranchRef {
            name
            target {
              ... on Commit {
                history(first: 1) {
                  edges {
                    node {
                      oid
                      message
                      committedDate
                      author {
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
'''.format(topic)

# Set the GraphQL API endpoint
url = 'https://api.github.com/graphql'

# Set the request headers with the access token
headers = {'Authorization': f'token {access_token}'}

# Send the GraphQL request
response = requests.post(url, json={'query': query}, headers=headers)

# Parse the response JSON
data = response.json()

# Extract the repository and commit information
repositories = data['data']['search']['edges']
for repo in repositories:
    repo_name = repo['node']['name']
    commit = repo['node']['defaultBranchRef']['target']['history']['edges'][0]['node']
    commit_oid = commit['oid']
    commit_message = commit['message']
    commit_date = commit['committedDate']
    commit_author = commit['author']['name']

    print('Repository:', repo_name)
    print('Last Commit:')
    print('  - Commit ID:', commit_oid)
    print('  - Message:', commit_message)
    print('  - Date:', commit_date)
    print('  - Author:', commit_author)
    print('---')

if __name__ == '__main__':
    app.run()