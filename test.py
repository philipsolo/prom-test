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

# Set the maximum number of repositories to retrieve per request
per_page = 100

# Initialize an empty list to store all repositories
repositories = []

# Set the initial `after` cursor to start with as `None`
after_cursor = None

# Continue making requests until all repositories are retrieved
while True:
    # Make the GraphQL query to fetch repositories under the topic with pagination
    query = '''
query ($topic: String!, $label: String!, $per_page: Int!, $after_cursor: String, $folderPath: String!) {
  search(query: $topic, type: REPOSITORY, first: $per_page, after: $after_cursor) {
    pageInfo {
      hasNextPage
      endCursor
    }
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
          object(expression: $folderPath) {
            ... on Tree {
              entries {
                name
                type
                object {
                  ... on Blob {
                    oid
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

    '''

    # Set the GraphQL API endpoint
    url = 'https://api.github.com/graphql'

    # Set the request headers with the access token
    headers = {'Authorization': f'token {access_token}'}

    # Set the variables for the GraphQL query
    variables = {
        'topic': f'topic:{topic} type:REPOSITORY',
        'per_page': per_page,
        'after_cursor': after_cursor
    }

    # Send the GraphQL request
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)

    # Parse the response JSON
    data = response.json()

    # Extract the repositories from the response
    repositories += data['data']['search']['edges']

    # Check if there are more pages to retrieve
    has_next_page = data['data']['search']['pageInfo']['hasNextPage']
    if not has_next_page:
        break

    # Set the `after` cursor for the next page
    after_cursor = data['data']['search']['pageInfo']['endCursor']

# Process the retrieved repositories
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


from prometheus_client import start_http_server, Gauge, Counter, Histogram

# Define Prometheus metrics
repository_count = Gauge('repository_count', 'Total number of repositories')
commit_count = Counter('commit_count', 'Total number of commits')
commit_date_histogram = Histogram('commit_date', 'Distribution of commit dates')

# Process the retrieved repositories
for repo in repositories:
    repo_name = repo['node']['name']
    commit = repo['node']['defaultBranchRef']['target']['history']['edges'][0]['node']
    commit_oid = commit['oid']
    commit_message = commit['message']
    commit_date = commit['committedDate']
    commit_author = commit['author']['name']

    # Update metrics
    repository_count.inc()  # Increment the repository count by 1
    commit_count.inc()  # Increment the commit count by 1
    commit_date_histogram.observe(commit_date)  # Add the commit date to the histogram

    # Additional processing and logging
    print('Repository:', repo_name)
    print('Last Commit:')
    print('  - Commit ID:', commit_oid)
    print('  - Message:', commit_message)
    print('  - Date:', commit_date)
    print('  - Author:', commit_author)
    print('---')

# Start the Prometheus HTTP server
start_http_server(8000)

"""query {
  search(query: "label:<label_name> is:collaborator:"<user_id> permission:write", type: REPOSITORY) {
    nodes {
      ... on Repository {
        name
        owner {
          login
        }
      }
    }
  }
}
"""


query = """
    query ($topic: String!, $user_id: Int!) {
      search(query: "topic:$topic is:collaborator:$user_id permission:write", type: REPOSITORY) {
        nodes {
          ... on Repository {
            name
            owner {
              login
            }
          }
        }
      }
    }
"""

variables = {
    "topic": topic,
    "user_id": user_id
}

headers = {
    "Authorization": "bearer YOUR_GITHUB_ACCESS_TOKEN"
}

response = requests.post("https://api.github.com/graphql", headers=headers, json={"query": query, "variables": variables})

if response.status_code == 200:
    data = response.json()
    repos = data["data"]["search"]["nodes"]
    return repos
else:
    raise Exception("Failed to fetch repos: {}".format(response.status_code))

import requests
import json

# Your GitHub personal access token
token = "YOUR_PERSONAL_ACCESS_TOKEN"

# The username of the user whose repositories you want to fetch
username = "USERNAME"

# GraphQL query to fetch repositories where the user is a collaborator and their topics
query = """
{
  user(login: "%s") {
    repositories(first: 100) {
      nodes {
        name
        owner {
          login
        }
        repositoryTopics(first: 10) {
          nodes {
            topic {
              name
            }
          }
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
""" % username
# Define the GitHub GraphQL API URL
api_url = "https://api.github.com/graphql"

# Create a headers dictionary with your token
headers = {
    "Authorization": "Bearer " + token
}

# Send the POST request with the query
response = requests.post(api_url, json={'query': query}, headers=headers)

# Check for a successful response
if response.status_code == 200:
    data = response.json()
    repositories = data["data"]["user"]["repositoriesCollaboratedTo"]["nodes"]
    for repo in repositories:
        owner = repo["owner"]["login"]
        repo_name = repo["name"]
        topics = [topic["topic"]["name"] for topic in repo["repositoryTopics"]["nodes"]]
        print(f"Repository: {owner}/{repo_name}")
        print("Topics:", ', '.join(topics) if topics else "No topics")
else:
    print("Error: Unable to fetch repositories")

# GraphQL query to fetch repositories where the user is a collaborator with a specific topic
query = """
{
  user(login: "%s") {
    repositories(first: 100) {
      nodes {
        name
        owner {
          login
        }
        repositoryTopics(first: 10) {
          nodes {
            topic {
              name
            }
          }
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
""" % username

# Define the GitHub GraphQL API URL
api_url = "https://api.github.com/graphql"

# Create a headers dictionary with your token
headers = {
    "Authorization": "Bearer " + token
}

repositories = []

while True:
    # Send the POST request with the query
    response = requests.post(api_url, json={'query': query}, headers=headers)

    # Check for a successful response
    if response.status_code == 200:
        data = response.json()["data"]["user"]["repositories"]
        repositories += data["nodes"]

        if data["pageInfo"]["hasNextPage"]:
            # If there are more pages, update the cursor and query again
            query = query.replace('first: 100', f'first: 100, after: "{data["pageInfo"]["endCursor"]}"')
        else:
            break
    else:
        print("Error: Unable to fetch repositories")
        break

# Filter the repositories by collaborator status and topic
matching_repositories = [
    repo for repo in repositories
    if any(topic_node["topic"]["name"] == topic for topic_node in repo["repositoryTopics"]["nodes"])
       and repo["owner"]["login"] != username
]

for repo in matching_repositories:
    owner = repo["owner"]["login"]
    repo_name = repo["name"]
    print(f"Repository: {owner}/{repo_name}")
    topics = [topic_node["topic"]["name"] for topic_node in repo["repositoryTopics"]["nodes"]]
    print("Topics:", ', '.join(topics) if topics else "No topics")


if __name__ == '__main__':
    app.run()