"""
MCP Search Service - Search for MCP servers from mcp.so
"""
import httpx
from typing import List, Dict, Any
import re
import json
from bs4 import BeautifulSoup


class MCPSearchService:
    """Service for searching MCP servers from mcp.so"""

    BASE_URL = "https://mcp.so"

    async def search_servers(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for MCP servers on mcp.so by parsing embedded JSON data

        Args:
            query: Search query string

        Returns:
            List of MCP server results with name, description, url, avatar, and config
        """
        try:
            # Search on mcp.so/explore with query parameter (RSC endpoint)
            search_url = f"{self.BASE_URL}/explore?q={query}"

            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(search_url)
                response.raise_for_status()

            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract server data from Next.js RSC (React Server Components) payload
            results = []
            script_tags = soup.find_all('script')

            for script in script_tags:
                if not script.string or 'self.__next_f' not in script.string:
                    continue

                # Look for server objects in the JSON data
                # Pattern: server data contains slug, name, description, avatar_url, etc.
                try:
                    # Find server data patterns in the embedded JSON
                    # Look for slug that matches query
                    server_data_pattern = r'\{[^{}]*?"slug"\s*:\s*"([^"]*' + re.escape(query.lower()) + r'[^"]*)"[^{}]*?\}'
                    matches = re.finditer(server_data_pattern, script.string, re.IGNORECASE)

                    for match in matches:
                        server_json = match.group(0)
                        try:
                            # Try to extract fields from the JSON-like string
                            slug_match = re.search(r'"slug"\s*:\s*"([^"]+)"', server_json)
                            name_match = re.search(r'"name"\s*:\s*"([^"]+)"', server_json)
                            desc_match = re.search(r'"description"\s*:\s*"([^"]+)"', server_json)
                            avatar_match = re.search(r'"avatar_url"\s*:\s*"([^"]+)"', server_json)
                            author_match = re.search(r'"author_name"\s*:\s*"([^"]+)"', server_json)
                            github_match = re.search(r'"github_url"\s*:\s*"([^"]+)"', server_json)

                            if slug_match:
                                slug = slug_match.group(1)
                                name = name_match.group(1) if name_match else slug.replace('-', ' ').title()
                                # Clean up name - remove duplicate "C" prefix artifacts from parsing
                                if name.startswith('C') and len(name) > 1 and name[1].isupper():
                                    name = name[1:]
                                description = desc_match.group(1) if desc_match else f"MCP server for {slug}"
                                avatar_url = avatar_match.group(1) if avatar_match else None
                                author_name = author_match.group(1) if author_match else None
                                github_url = github_match.group(1) if github_match else None

                                # Build GitHub avatar URL from github_url or author_name
                                if not avatar_url and github_url:
                                    # Extract GitHub username from URL: https://github.com/username/repo
                                    github_user_match = re.search(r'github\.com/([^/]+)', github_url)
                                    if github_user_match:
                                        github_username = github_user_match.group(1)
                                        avatar_url = f"https://avatars.githubusercontent.com/{github_username}"

                                # Construct URL
                                if author_name:
                                    url = f"{self.BASE_URL}/server/{slug}/{author_name}"
                                    mcp_url = f"/server/{slug}/{author_name}"
                                else:
                                    url = f"{self.BASE_URL}/server/{slug}"
                                    mcp_url = f"/server/{slug}"

                                results.append({
                                    "name": slug,
                                    "title": name,
                                    "description": description,
                                    "url": url,
                                    "mcp_url": mcp_url,
                                    "avatar_url": avatar_url,
                                    "author_name": author_name,
                                    "github_url": github_url
                                })
                        except:
                            continue

                    # If we found matches with the query, don't need to continue
                    if results:
                        break

                except Exception as e:
                    continue

            # If no specific results found, fall back to general server list
            if not results:
                server_links = soup.find_all('a', href=re.compile(r'/server/[\w-]+'))
                seen_servers = set()

                for link in server_links[:20]:
                    href = link.get('href', '')
                    if not href:
                        continue

                    parts = href.strip('/').split('/')
                    if len(parts) >= 2 and parts[0] == 'server':
                        server_name = parts[1]

                        # Filter by query
                        if query.lower() not in server_name.lower():
                            continue

                        if server_name in seen_servers:
                            continue
                        seen_servers.add(server_name)

                        # Try to get clean title from the card
                        title = server_name.replace('-', ' ').title()
                        description = f"MCP server: {server_name}"

                        # Try to find h2 or h3 with actual title in parent card
                        card = link.find_parent(['div', 'article'])
                        if card:
                            h2 = card.find(['h2', 'h3'])
                            if h2:
                                title = h2.get_text(strip=True)

                            # Try to find description in card
                            desc_elem = card.find('p')
                            if desc_elem:
                                description = desc_elem.get_text(strip=True)

                        # Try to find avatar near the link
                        avatar_url = None
                        github_url = None
                        card = link.find_parent(['div', 'article'])
                        if card:
                            img = card.find('img')
                            if img:
                                avatar_url = img.get('src')
                                # Convert relative URLs to absolute
                                if avatar_url and avatar_url.startswith('/'):
                                    avatar_url = f"{self.BASE_URL}{avatar_url}"

                            # Try to find GitHub link
                            github_link = card.find('a', href=re.compile(r'github\.com'))
                            if github_link:
                                github_url = github_link.get('href')
                                # Extract GitHub avatar if no avatar found
                                if not avatar_url:
                                    github_user_match = re.search(r'github\.com/([^/]+)', github_url)
                                    if github_user_match:
                                        github_username = github_user_match.group(1)
                                        avatar_url = f"https://avatars.githubusercontent.com/{github_username}"

                        results.append({
                            "name": server_name,
                            "title": title,
                            "description": description,
                            "url": f"{self.BASE_URL}{href}",
                            "mcp_url": href,
                            "avatar_url": avatar_url,
                            "author_name": parts[2] if len(parts) > 2 else None,
                            "github_url": github_url
                        })

            # Enrich results with GitHub avatars by fetching detail pages
            enriched_results = []
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as enrich_client:
                for result in results[:10]:  # Limit to first 10 to avoid too many requests
                    try:
                        # If no avatar_url, try to get it from detail page
                        if not result.get('avatar_url'):
                            detail_response = await enrich_client.get(result['url'])
                            detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

                            # Find GitHub link on detail page (skip issue trackers and mcp.so links)
                            github_links = detail_soup.find_all('a', href=re.compile(r'github\.com/[^/]+/[^/]+'))
                            for gh_link in github_links:
                                gh_url = gh_link.get('href')
                                # Skip issue tracker, discussion, pulls, and chatmcp/mcpso links
                                if any(skip in gh_url for skip in ['/issues', '/pulls', '/discussions', 'chatmcp/mcpso']):
                                    continue
                                # Found valid repository link
                                result['github_url'] = gh_url
                                # Extract GitHub username for avatar
                                github_user_match = re.search(r'github\.com/([^/]+)', gh_url)
                                if github_user_match:
                                    github_username = github_user_match.group(1)
                                    result['avatar_url'] = f"https://avatars.githubusercontent.com/{github_username}"
                                break

                        enriched_results.append(result)
                    except Exception as e:
                        # If enrichment fails, still include the result
                        enriched_results.append(result)
                        continue

            return enriched_results

        except Exception as e:
            print(f"Error searching mcp.so: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def get_server_config(self, server_url: str) -> Dict[str, Any]:
        """
        Fetch detailed configuration for a specific MCP server

        Args:
            server_url: Full URL to the server page on mcp.so

        Returns:
            Dict with server details and configuration
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(server_url)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for JSON configuration blocks
            config = None
            code_blocks = soup.find_all('code')

            for code in code_blocks:
                text = code.get_text()
                # Try to find JSON config with "command" field
                if '"command"' in text or '"npx"' in text:
                    try:
                        # Extract JSON from code block
                        json_match = re.search(r'\{[^}]*"command"[^}]*\}', text, re.DOTALL)
                        if json_match:
                            config = json.loads(json_match.group())
                            break
                    except:
                        continue

            # If no config found, try to extract from pre tags
            if not config:
                pre_tags = soup.find_all('pre')
                for pre in pre_tags:
                    text = pre.get_text()
                    if 'npx' in text or 'command' in text:
                        try:
                            # Try to parse as JSON
                            config = json.loads(text)
                            if 'command' in config:
                                break
                        except:
                            # Try to extract npx command
                            npx_match = re.search(r'npx\s+(-y\s+)?(@[\w-]+/[\w-]+|[\w-]+)', text)
                            if npx_match:
                                package = npx_match.group(2) or npx_match.group(1)
                                config = {
                                    "command": "npx",
                                    "args": ["-y", package]
                                }
                                break

            # Get description
            description = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')

            # Get GitHub link and avatar (skip issue trackers and mcp.so links)
            github_url = None
            avatar_url = None
            github_links = soup.find_all('a', href=re.compile(r'github\.com'))
            for link in github_links:
                href = link.get('href', '')
                # Skip issue trackers, discussions, pulls, and chatmcp/mcpso links
                if any(skip in href for skip in ['/issues', '/pulls', '/discussions', 'chatmcp/mcpso']):
                    continue
                # Found a valid repository link
                github_url = href
                # Extract GitHub username and build avatar URL
                github_user_match = re.search(r'github\.com/([^/]+)', github_url)
                if github_user_match:
                    github_username = github_user_match.group(1)
                    avatar_url = f"https://avatars.githubusercontent.com/{github_username}"
                break

            return {
                "description": description,
                "config": config,
                "github_url": github_url,
                "avatar_url": avatar_url
            }

        except Exception as e:
            print(f"Error fetching server config from {server_url}: {e}")
            return {}
