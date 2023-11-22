from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def fetch_all_contributors(contributors_url):
    contributors = []
    page = 1

    while True:
        params = {'page': page}
        response = requests.get(contributors_url, params=params)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

        page_contributors = response.json()
        contributors.extend(page_contributors)

        # Check for the presence of a 'Link' header indicating the next page
        link_header = response.headers.get('Link', '')
        if 'rel="next"' not in link_header:
            break  # Break if there is no next page

        page += 1

    return contributors

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get GitHub username and repository from the form
        username = request.form.get('username')
        repository = request.form.get('repository')

        if not username or not repository:
            return render_template('index.html', error="Please provide both 'username' and 'repository'.")

        # Fetch repository information using GitHub API
        repo_url = f'https://api.github.com/repos/{username}/{repository}'
        contributors_url = f'{repo_url}/contributors'

        try:
            # Get repository info to check if it's private
            repo_info = requests.get(repo_url).json()
            is_private = repo_info.get('private', False)

            # Fetch all contributors using GitHub API (including private if applicable)
            contributors = fetch_all_contributors(contributors_url)

            contributor_count = len(contributors)

        except requests.RequestException as e:
            return render_template('index.html', error=str(e))

        # Return HTML template with contributor information
        return render_template('index.html', contributor_count=contributor_count, contributors=contributors)

    # If it's a GET request, simply render the form
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
