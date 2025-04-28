import os
import requests
import csv

TOKEN = os.environ.get("GITHUB_TOKEN")

url = "https://api.github.com/search/repositories"

queries = [
    "energy measure is:public archived:false",
    "power measure is:public archived:false"
]

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

all_repos = []
seen_repos = set() 
per_page = 100

for query_text in queries:
    page = 1

    while True:
        print(f"Searching for '{query_text}' on page {page}...")

        params = {
            "q": query_text,
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Error ({response.status_code}):", response.json())
            break

        data = response.json()

        if "items" not in data:
            print("Error: item not found. API response:", data)
            break

        for repo in data["items"]:
            repo_full_name = repo["full_name"]
            if repo_full_name not in seen_repos:
                repo["query"] = query_text
                all_repos.append(repo)
                seen_repos.add(repo_full_name) 
            else:
                print(f"Skipping duplicate repo: {repo_full_name}")

        if len(data["items"]) < per_page:
            break

        page += 1

if all_repos:
    os.makedirs("all_repos", exist_ok=True)
    with open("all_repos/repos_energyTools.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "query", "url", "repo_name", "description", "topics",
            "created_at", "updated_at", "size", "stars", "watchers",
            "language", "forks", "open_issues"
        ])

        for repo in all_repos:
            writer.writerow([
                repo.get("query", ""),
                repo["html_url"],
                repo["full_name"],
                repo["description"],
                ",".join(repo.get("topics", [])),
                repo["created_at"],
                repo["updated_at"],
                repo["size"],
                repo["stargazers_count"],
                repo["watchers_count"],
                repo["language"],
                repo["forks"],
                repo["open_issues"]
            ])

    print(f"CSV has been created with {len(all_repos)} unique repositories!")
else:
    print("Nothing found.")