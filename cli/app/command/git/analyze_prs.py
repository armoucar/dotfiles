#!/usr/bin/env python3

import base64
import click
import json
import os
import subprocess
import threading
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta


@click.command(name="analyze-prs")
@click.option(
    "--start-date",
    default="2025-01-01",
    help="Start date for PR analysis (YYYY-MM-DD format)",
)
@click.option(
    "--end-date",
    default="2025-07-04",
    help="End date for PR analysis (YYYY-MM-DD format)",
)
@click.option(
    "--author",
    default="@me",
    help="GitHub username to analyze PRs for (default: @me for current user)",
)
@click.option(
    "--max-workers",
    default=20,
    help="Maximum number of parallel workers for fetching PR details",
)
@click.option(
    "--detail",
    is_flag=True,
    help="Include README.md content and descriptions for all PRs",
)
def analyze_prs(start_date: str, end_date: str, author: str, max_workers: int, detail: bool):
    """Analyze merged pull requests and provide detailed statistics about contributions.

    This command fetches all merged PRs for a specific date range and provides:
    - PR size analysis (number of files changed)
    - Lines of code statistics
    - Repository grouping
    - Timeline analysis
    - Significant changes identification with full descriptions
    - Markdown report saved to ./tmp directory

    Use --detail to include README.md content and descriptions for all PRs.

    Requires GitHub CLI (gh) to be installed and authenticated.
    """
    # Thread-safe progress counter
    progress_lock = threading.Lock()
    progress_counter = 0

    def run_gh_command(cmd):
        """Run a GitHub CLI command and return the output"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            click.echo(f"Error running command: {cmd}", err=True)
            click.echo(f"Error: {e.stderr}", err=True)
            return None

    def get_pr_list_for_date_range(start_date, end_date):
        """Fetch PRs for a specific date range"""
        cmd = f"gh search prs --author {author} --state closed --merged --merged-at {start_date}..{end_date} --limit 1000 --json number,title,repository,closedAt,url"
        click.echo(f"Fetching PRs for {start_date} to {end_date}...")
        output = run_gh_command(cmd)
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                click.echo(f"Failed to parse JSON from PR search for {start_date} to {end_date}", err=True)
                return []
        return []

    def split_date_range(start_date, end_date, chunk_months=2):
        """Split a date range into smaller chunks for pagination"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        ranges = []
        current = start

        while current < end:
            # Calculate next chunk end using day-based approach to avoid month arithmetic issues
            if chunk_months:
                # Approximate months as 30 days for simplicity
                chunk_days = chunk_months * 30
                next_end = current + timedelta(days=chunk_days)
            else:
                next_end = end

            chunk_end = min(next_end, end)

            ranges.append((current.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d")))
            current = chunk_end + timedelta(days=1)

        return ranges

    def get_pr_list():
        """Fetch the complete list of PRs using pagination if necessary"""
        click.echo("Fetching PR list with pagination support...")

        # First, try to get all PRs in one query
        all_prs = get_pr_list_for_date_range(start_date, end_date)

        # If we get exactly 1000 results, we might have hit the limit
        if len(all_prs) == 1000:
            click.echo("⚠️  Hit the 1000 result limit. Implementing date-based pagination...")

            # Split the date range into smaller chunks
            date_ranges = split_date_range(start_date, end_date, chunk_months=1)

            all_prs = []
            for range_start, range_end in date_ranges:
                chunk_prs = get_pr_list_for_date_range(range_start, range_end)
                all_prs.extend(chunk_prs)

                # If any chunk still hits 1000, warn about potential missing data
                if len(chunk_prs) == 1000:
                    click.echo(f"⚠️  WARNING: Hit limit for {range_start} to {range_end}. Some PRs might be missing.")

            # Remove duplicates (in case of overlapping date ranges)
            seen = set()
            unique_prs = []
            for pr in all_prs:
                pr_id = f"{pr['repository']['nameWithOwner']}-{pr['number']}"
                if pr_id not in seen:
                    seen.add(pr_id)
                    unique_prs.append(pr)

            all_prs = unique_prs
            click.echo(f"✅ Fetched {len(all_prs)} unique PRs using pagination")
        else:
            click.echo(f"✅ Fetched {len(all_prs)} PRs (no pagination needed)")

        return all_prs

    def get_pr_details(repo_name, pr_number):
        """Get detailed information about a PR including files changed and description"""
        cmd = f"gh pr view {pr_number} --repo {repo_name} --json additions,deletions,changedFiles,body"
        output = run_gh_command(cmd)
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                click.echo(f"Failed to parse JSON for PR {pr_number} in {repo_name}", err=True)
                return None
        return None

    def fetch_pr_info(pr, total_prs):
        """Fetch detailed information for a single PR (for parallel processing)"""
        nonlocal progress_counter

        details = get_pr_details(pr["repository"]["nameWithOwner"], pr["number"])

        pr_info = {
            "number": pr["number"],
            "title": pr["title"],
            "repository": pr["repository"]["name"],
            "repo_full_name": pr["repository"]["nameWithOwner"],
            "closed_at": pr["closedAt"],
            "url": pr["url"],
            "files_changed": details.get("changedFiles", 0) if details else 0,
            "additions": details.get("additions", 0) if details else 0,
            "deletions": details.get("deletions", 0) if details else 0,
            "body": details.get("body", "") if details else "",
        }

        # Update progress counter thread-safely
        with progress_lock:
            progress_counter += 1
            if progress_counter % 10 == 0 or progress_counter == total_prs:
                click.echo(f"✅ Processed {progress_counter}/{total_prs} PRs ({progress_counter / total_prs * 100:.1f}%)")

        return pr_info

    # Fetch PR list dynamically with pagination support
    base_data = get_pr_list()

    if not base_data:
        click.echo("No PRs found or failed to fetch PR list.")
        return

    click.echo(f"Found {len(base_data)} PRs. Fetching detailed information using parallel processing...")

    # Reset progress counter
    progress_counter = 0

    # Use ThreadPoolExecutor for parallel processing
    detailed_prs = []
    actual_max_workers = min(max_workers, len(base_data))  # Limit concurrent requests to avoid rate limiting

    with ThreadPoolExecutor(max_workers=actual_max_workers) as executor:
        # Submit all tasks
        future_to_pr = {executor.submit(fetch_pr_info, pr, len(base_data)): pr for pr in base_data}

        # Collect results as they complete
        for future in as_completed(future_to_pr):
            try:
                pr_info = future.result()
                detailed_prs.append(pr_info)
            except Exception as e:
                pr = future_to_pr[future]
                click.echo(f"❌ Error processing PR #{pr['number']}: {e}", err=True)

    click.echo(f"🎉 Completed processing {len(detailed_prs)} PRs in parallel!")

    # Sort by closed date (newest first)
    detailed_prs.sort(key=lambda x: x["closed_at"], reverse=True)

    # Print detailed list in markdown format
    click.echo("\n" + "=" * 80)
    click.echo("DETAILED PR ANALYSIS")
    click.echo("=" * 80)

    for pr in detailed_prs:
        date_str = datetime.fromisoformat(pr["closed_at"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        lines_changed = pr["additions"] + pr["deletions"]

        click.echo(f"\n- **PR #{pr['number']}** ({pr['repository']}) - {date_str}")
        click.echo(f"  - **Title:** {pr['title']}")
        click.echo(f"  - **Files changed:** {pr['files_changed']}")
        click.echo(f"  - **Lines changed:** {lines_changed}")
        click.echo(f"  - **URL:** [{pr['url']}]({pr['url']})")
        click.echo()

    # Generate statistics
    click.echo("\n" + "=" * 80)
    click.echo("AGGREGATED STATISTICS")
    click.echo("=" * 80)

    # PRs per repository
    repo_counts = Counter(pr["repository"] for pr in detailed_prs)
    click.echo(f"\n📊 PRs per Repository ({len(detailed_prs)} total PRs):")
    for repo, count in repo_counts.most_common():
        click.echo(f"   {repo:<30} {count:>3} PRs")

    # Significant changes analysis
    significant_prs = [pr for pr in detailed_prs if pr["files_changed"] > 5]
    click.echo(f"\n🔥 Significant PRs (>5 files changed): {len(significant_prs)}")

    significant_changes_md = ""
    if significant_prs:
        click.echo("\n📋 Top 10 Most Significant Changes (with descriptions):")
        click.echo("=" * 100)
        significant_changes_md = "\n## 🔥 Most Significant Changes (>5 files changed)\n\n"

        for i, pr in enumerate(sorted(significant_prs, key=lambda x: x["files_changed"], reverse=True)[:10], 1):
            click.echo(f"\n{i}. PR #{pr['number']} ({pr['repository']}) - {pr['files_changed']} files changed")
            click.echo(f"   📝 Title: {pr['title']}")
            click.echo(f"   🔗 URL: {pr['url']}")

            # Add to markdown
            significant_changes_md += f"### {i}. PR #{pr['number']} ({pr['repository']}) - {pr['files_changed']} files changed\n\n"
            significant_changes_md += f"**Title:** {pr['title']}\n\n"
            significant_changes_md += f"**URL:** [{pr['url']}]({pr['url']})\n\n"

            # Format and display PR body/description
            body = pr.get("body", "").strip()
            if body:
                # Clean up the description - remove excessive newlines and format nicely
                body_lines = [line.strip() for line in body.split("\n") if line.strip()]
                if body_lines:
                    click.echo("   📄 Description:")
                    significant_changes_md += "**Description:**\n\n"

                    for line in body_lines:
                        click.echo(f"      {line}")
                        significant_changes_md += f"{line}\n\n"
            else:
                click.echo("   📄 Description: (No description provided)")
                significant_changes_md += "**Description:** (No description provided)\n\n"

            click.echo("-" * 80)
            significant_changes_md += "---\n\n"

    # Size distribution
    small_prs = len([pr for pr in detailed_prs if pr["files_changed"] <= 2])
    medium_prs = len([pr for pr in detailed_prs if 3 <= pr["files_changed"] <= 5])
    large_prs = len([pr for pr in detailed_prs if pr["files_changed"] > 5])

    click.echo("\n📈 PR Size Distribution:")
    click.echo(f"   Small (≤2 files):  {small_prs:>3} PRs ({small_prs / len(detailed_prs) * 100:.1f}%)")
    click.echo(f"   Medium (3-5 files): {medium_prs:>3} PRs ({medium_prs / len(detailed_prs) * 100:.1f}%)")
    click.echo(f"   Large (>5 files):   {large_prs:>3} PRs ({large_prs / len(detailed_prs) * 100:.1f}%)")

    # Lines of code statistics
    total_additions = sum(pr["additions"] for pr in detailed_prs)
    total_deletions = sum(pr["deletions"] for pr in detailed_prs)

    click.echo("\n📝 Code Changes Summary:")
    click.echo(f"   Total lines added:   {total_additions:>6}")
    click.echo(f"   Total lines deleted: {total_deletions:>6}")
    click.echo(f"   Net change:          {total_additions - total_deletions:>6}")

    # Timeline analysis
    click.echo("\n📅 Timeline Analysis:")
    monthly_counts = defaultdict(int)
    for pr in detailed_prs:
        month = datetime.fromisoformat(pr["closed_at"].replace("Z", "+00:00")).strftime("%Y-%m")
        monthly_counts[month] += 1

    for month in sorted(monthly_counts.keys()):
        click.echo(f"   {month}: {monthly_counts[month]:>2} PRs")

    # Generate and save markdown report
    _save_markdown_report(detailed_prs, repo_counts, significant_changes_md, small_prs, medium_prs, large_prs,
                         total_additions, total_deletions, monthly_counts, start_date, end_date, author, detail)


def _get_readme_content(repo_full_name):
    """Fetch README.md content from a repository"""
    # Try multiple approaches to get README content

    # Approach 1: Try to get README via gh repo view
    cmd = f"gh repo view {repo_full_name} --json readme"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        if result.stdout:
            data = json.loads(result.stdout)
            readme_data = data.get("readme")
            if readme_data and readme_data.get("text"):
                return readme_data.get("text")
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        pass

    # Approach 2: Try to get README directly via gh api
    cmd = f"gh api repos/{repo_full_name}/readme"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        if result.stdout.strip():
            data = json.loads(result.stdout)
            content = data.get("content", "")
            if content:
                # Decode base64 content
                try:
                    decoded = base64.b64decode(content).decode('utf-8')
                    return decoded
                except Exception:
                    pass
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        pass

    # Approach 3: Try alternative README files
    readme_files = ["README.md", "README.rst", "README.txt", "README", "readme.md", "readme.rst", "readme.txt", "readme"]

    for readme_file in readme_files:
        cmd = f"gh api repos/{repo_full_name}/contents/{readme_file}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            if result.stdout.strip():
                data = json.loads(result.stdout)
                content = data.get("content", "")
                if content:
                    try:
                        decoded = base64.b64decode(content).decode('utf-8')
                        return decoded
                    except Exception:
                        continue
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            continue

    return ""


def _save_markdown_report(detailed_prs, repo_counts, significant_changes_md, small_prs, medium_prs, large_prs,
                         total_additions, total_deletions, monthly_counts, start_date, end_date, author, detail: bool):
    """Save the analysis report to a markdown file"""
    # Create tmp directory if it doesn't exist
    tmp_dir = "./tmp"
    os.makedirs(tmp_dir, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pr_analysis_{author.replace('@', '').replace('-', '_')}_{timestamp}.md"
    filepath = os.path.join(tmp_dir, filename)

    # Start with basic info
    markdown_content = f"""# GitHub PR Analysis Report

**Author:** {author}
**Period:** {start_date} to {end_date}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total PRs:** {len(detailed_prs)}

"""

    # Add README content for each repository at the beginning (only if detail flag is set)
    if detail:
        click.echo("📚 Fetching README.md content for repositories...")
        unique_repos = set()
        for pr in detailed_prs:
            unique_repos.add(pr["repo_full_name"])

        for repo_full_name in sorted(unique_repos):
            click.echo(f"   Fetching README for {repo_full_name}...")
            readme_content = _get_readme_content(repo_full_name)

            markdown_content += f"<{repo_full_name}/README.md>\n"
            if readme_content:
                markdown_content += readme_content
                click.echo(f"   ✅ README found ({len(readme_content)} chars)")
            else:
                markdown_content += "(No README.md found or content unavailable)"
                click.echo(f"   ❌ No README found")
            markdown_content += f"\n</{repo_full_name}/README.md>\n\n"

    # Add analysis sections
    markdown_content += f"""## 📊 PRs per Repository

| Repository | Count |
|------------|-------|
"""

    for repo, count in repo_counts.most_common():
        markdown_content += f"| {repo} | {count} |\n"

    markdown_content += f"""
## 📈 PR Size Distribution

- **Small (≤2 files):** {small_prs} PRs ({small_prs / len(detailed_prs) * 100:.1f}%)
- **Medium (3-5 files):** {medium_prs} PRs ({medium_prs / len(detailed_prs) * 100:.1f}%)
- **Large (>5 files):** {large_prs} PRs ({large_prs / len(detailed_prs) * 100:.1f}%)

## 📝 Code Changes Summary

- **Total lines added:** {total_additions:,}
- **Total lines deleted:** {total_deletions:,}
- **Net change:** {total_additions - total_deletions:,}

## 📅 Timeline Analysis

| Month | PRs |
|-------|-----|
"""

    for month in sorted(monthly_counts.keys()):
        markdown_content += f"| {month} | {monthly_counts[month]} |\n"

    # Add significant changes section
    markdown_content += significant_changes_md

    # Add detailed PR list (with or without descriptions based on detail flag)
    if detail:
        markdown_content += "\n## 📋 All PRs (Detailed List with Descriptions)\n\n"
    else:
        markdown_content += "\n## 📋 All PRs (Detailed List)\n\n"

    for pr in detailed_prs:
        date_str = datetime.fromisoformat(pr["closed_at"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        lines_changed = pr["additions"] + pr["deletions"]

        markdown_content += f"### PR #{pr['number']} ({pr['repository']}) - {date_str}\n\n"
        markdown_content += f"**Title:** {pr['title']}\n\n"
        markdown_content += f"**Files changed:** {pr['files_changed']}\n\n"
        markdown_content += f"**Lines changed:** {lines_changed:,}\n\n"
        markdown_content += f"**URL:** [{pr['url']}]({pr['url']})\n\n"

        # Add PR description only if detail flag is set
        if detail:
            body = pr.get("body", "").strip()
            if body:
                markdown_content += "**Description:**\n\n"
                # Clean up the description - remove excessive newlines and format nicely
                body_lines = [line.strip() for line in body.split("\n") if line.strip()]
                if body_lines:
                    for line in body_lines:
                        markdown_content += f"{line}\n\n"
            else:
                markdown_content += "**Description:** (No description provided)\n\n"

        markdown_content += "---\n\n"

    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    click.echo(f"\n💾 Analysis saved to: {filepath}")
    if detail:
        click.echo(f"📄 Report contains {len(detailed_prs)} PRs with detailed information")
        unique_repos = set(pr["repo_full_name"] for pr in detailed_prs)
        click.echo(f"📚 README.md content included for {len(unique_repos)} repositories")
    else:
        click.echo(f"📄 Report contains {len(detailed_prs)} PRs with basic information")
        click.echo("💡 Use --detail flag to include README content and PR descriptions")
