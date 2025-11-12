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

    def _normalize_mcp_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize MCP config by removing double-wrapped mcpServers structure
        
        Handles two cases:
        1. Correct format: {"command": "...", "args": [...]}
        2. Double-wrapped format: {"mcpServers": {"server_name": {"command": "...", "args": [...]}}}
        
        Args:
            config_data: Raw config data that might have outer wrapper
            
        Returns:
            Normalized config with only the inner server configuration
        """
        if not config_data:
            return config_data
            
        # Check if config has outer mcpServers wrapper
        if "mcpServers" in config_data:
            # Extract the first (and should be only) server config from mcpServers
            mcp_servers = config_data["mcpServers"]
            if isinstance(mcp_servers, dict) and len(mcp_servers) > 0:
                # Get the first server config (the actual MCP server configuration)
                first_server_key = next(iter(mcp_servers))
                return mcp_servers[first_server_key]
        
        # Config is already in correct format
        return config_data

    async def search_servers(self, query: str, max_pages: int = 3) -> List[Dict[str, Any]]:
        """
        Search for MCP servers on mcp.so with pagination support using direct HTML parsing

        Args:
            query: Search query string
            max_pages: Maximum number of pages to fetch (default: 3, to get ~30 results)

        Returns:
            List of MCP server results with name, description, url, avatar, and config
        """
        all_results = []
        seen_servers = set()  # Track unique servers by URL

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                # Fetch multiple pages
                for page_num in range(1, max_pages + 1):
                    search_url = f"{self.BASE_URL}/explore?q={query}&page={page_num}"

                    try:
                        response = await client.get(search_url)
                        response.raise_for_status()
                    except Exception as e:
                        print(f"Failed to fetch page {page_num}: {e}")
                        break

                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Find all server link cards - they have href="/server/..."
                    server_links = soup.find_all('a', href=re.compile(r'^/server/[\w\.-]+'))
                    
                    page_results_count = 0

                    for link in server_links:
                        href = link.get('href', '')
                        if not href or href.startswith('/server/submit'):
                            continue

                        # Skip duplicates
                        if href in seen_servers:
                            continue
                        seen_servers.add(href)

                        # Parse server info from card
                        parts = href.strip('/').split('/')
                        if len(parts) < 2:
                            continue

                        slug = parts[1]
                        author_name = parts[2] if len(parts) > 2 else None

                        # Get title from h3 within the link
                        h3 = link.find('h3')
                        title = h3.get_text(strip=True) if h3 else slug.replace('-', ' ').title()

                        # Get description from p within the link
                        desc_elem = link.find('p')
                        description = desc_elem.get_text(strip=True) if desc_elem else f"MCP server: {slug}"

                        # Look for avatar image
                        avatar_url = None
                        img = link.find('img')
                        if img:
                            avatar_url = img.get('src')
                            # Convert relative URLs to absolute
                            if avatar_url and avatar_url.startswith('/'):
                                avatar_url = f"{self.BASE_URL}{avatar_url}"

                        # Try to find GitHub URL (we'll do this in enrichment phase)
                        github_url = None

                        # Construct full URL
                        full_url = f"{self.BASE_URL}{href}"

                        all_results.append({
                            "name": slug,
                            "title": title,
                            "description": description,
                            "url": full_url,
                            "mcp_url": href,
                            "avatar_url": avatar_url,
                            "author_name": author_name,
                            "github_url": github_url
                        })
                        
                        page_results_count += 1

                    print(f"Page {page_num}: Found {page_results_count} servers")

                    # If no results on this page, stop pagination
                    if page_results_count == 0:
                        print(f"No results on page {page_num}, stopping pagination")
                        break

            print(f"Total servers found across all pages: {len(all_results)}")

            # Enrich results with GitHub avatars by fetching detail pages
            enriched_results = []
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as enrich_client:
                # Enrich up to 30 results for better coverage
                for result in all_results[:30]:
                    try:
                        # If no avatar_url, try to get it from detail page
                        if not result.get('avatar_url'):
                            detail_response = await enrich_client.get(result['url'])
                            detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

                            # Find GitHub link on detail page
                            github_links = detail_soup.find_all('a', href=re.compile(r'github\.com/[^/]+/[^/]+'))
                            for gh_link in github_links:
                                gh_url = gh_link.get('href')
                                # Skip issue tracker, discussion, pulls, and mcp.so repo links
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

            # Normalize config to remove double-wrapped mcpServers structure
            normalized_config = self._normalize_mcp_config(config) if config else None

            return {
                "description": description,
                "config": normalized_config,
                "github_url": github_url,
                "avatar_url": avatar_url
            }

        except Exception as e:
            print(f"Error fetching server config from {server_url}: {e}")
            return {}
