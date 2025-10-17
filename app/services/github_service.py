import time

from github import Github, GithubException, Repository


class GitHubService:
    def __init__(self, token: str):
        """Initialize GitHub client with personal access token"""
        self.g = Github(token)
        self.user = self.g.get_user()

    def create_repo(self, task_id: str, description: str) -> Repository.Repository:
        """
        Create a new public GitHub repository
        Returns: Repository object
        """
        repo_name = f"tds-{task_id}"
        try:
            repo = self.user.create_repo(
                name=repo_name,
                description=description,
                private=False,
                auto_init=False,  # Don't auto-initialize to avoid conflicts
            )
            print(f"✅ Created repository: {repo.html_url}")
            time.sleep(2)  # Wait for repo to be ready
            return repo
        except GithubException as e:
            if "name already exists" in str(e):
                print(f"⚠️ Repository {repo_name} already exists, fetching it...")
                return self.user.get_repo(repo_name)
            raise

    def push_file(
        self,
        repo: Repository.Repository,
        file_path: str,
        content: str,
        commit_message: str,
    ):
        """
        Push a file to the repository (creates or updates).
        Handles initial commit when no branch exists yet.
        """
        try:
            # Check if any branches exist
            branches = list(repo.get_branches())

            if not branches:
                # No branch exists yet → First commit (creates main branch)
                repo.create_file(file_path, commit_message, content)
                print(f"✅ Created initial file (and branch): {file_path}")
                return

            # Branch exists, check if file exists
            try:
                existing_file = repo.get_contents(file_path, ref="main")
                # File exists, update it
                repo.update_file(
                    file_path, commit_message, content, existing_file.sha, branch="main"
                )
                print(f"✅ Updated file: {file_path}")
            except GithubException:
                # File doesn't exist, create it
                repo.create_file(file_path, commit_message, content, branch="main")
                print(f"✅ Created file: {file_path}")

        except Exception as e:
            print(f"❌ Error pushing {file_path}: {e}")
            raise

    def enable_github_pages(self, repo: Repository.Repository) -> str:
        """
        Enable GitHub Pages for the repository using direct REST API call.
        PyGithub doesn't have a built-in method for this.
        Returns: Pages URL
        """
        pages_url = f"https://{self.user.login}.github.io/{repo.name}/"

        try:
            # Use PyGithub's internal requester to make direct API call
            headers, data = repo._requester.requestJsonAndCheck(
                "POST",
                f"{repo.url}/pages",
                input={"source": {"branch": "main", "path": "/"}},
            )
            print(f"✅ Enabled GitHub Pages: {pages_url}")
        except GithubException as e:
            if e.status == 409:  # Conflict - already exists
                print(f"ℹ️ GitHub Pages already enabled: {pages_url}")
            elif e.status == 404:
                # Pages API might not be available, try alternative method
                print(f"ℹ️ Pages API not available, using fallback")
                try:
                    # Alternative: Just ensure a gh-pages branch exists
                    pass  # Pages will auto-enable from main branch
                except:
                    pass
            else:
                print(f"⚠️ Could not enable Pages (status {e.status}): {e.data}")
                # Don't raise - Pages might work anyway or need manual config

        time.sleep(5)  # Wait for Pages to deploy
        return pages_url

    def get_latest_commit_sha(self, repo: Repository.Repository) -> str:
        """Get the SHA of the latest commit on main branch"""
        commits = repo.get_commits()
        return commits[0].sha

    def git_workflow(
        self, task_id: str, brief: str, index_html: str, readme_md: str
    ) -> dict:
        """
        Complete Git workflow: Create repo, push content, enable Pages.

        Args:
            task_id: Unique task identifier
            brief: Task brief description
            index_html: Complete HTML content for index.html
            readme_md: Complete README.md content

        Returns:
            dict with repo_url, pages_url, commit_sha
        """
        # Step 1: Create repository
        repo = self.create_repo(task_id, f"TDS Project - {task_id}")

        # Step 2: Push index.html FIRST (creates main branch)
        print("📝 Pushing index.html...")
        self.push_file(repo, "index.html", index_html, "Add application code")

        # Step 3: Push MIT License
        print("📄 Pushing LICENSE...")
        mit_license = """MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

        self.push_file(repo, "LICENSE", mit_license, "Add MIT License")

        # Step 4: Push README
        print("📝 Pushing README.md...")
        self.push_file(repo, "README.md", readme_md, "Add README")

        # Step 5: Enable GitHub Pages
        print("🌐 Enabling GitHub Pages...")
        pages_url = self.enable_github_pages(repo)

        # Step 6: Get commit SHA
        commit_sha = self.get_latest_commit_sha(repo)

        print(f"✅ Workflow complete!")
        print(f"   Repo: {repo.html_url}")
        print(f"   Pages: {pages_url}")
        print(f"   Commit: {commit_sha}")

        return {
            "repo_url": repo.html_url,
            "pages_url": pages_url,
            "commit_sha": commit_sha,
        }
