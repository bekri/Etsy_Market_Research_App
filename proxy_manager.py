"""
Proxy Manager for handling free proxy sources
"""

import requests
import random
import time
from typing import List, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ProxyManager:
    def __init__(self):
        self.proxies: List[dict] = []
        self.last_update = None
        self.update_interval = 300  # 5 minutes
        self.proxy_sources = [
            self._get_proxyscrape_proxies,
            self._get_geonode_proxies,
            self._get_hidemy_proxies
        ]
    
    def _get_proxyscrape_proxies(self) -> List[dict]:
        """Get proxies from ProxyScrape"""
        try:
            url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                proxies = []
                for line in response.text.strip().split('\n'):
                    if ':' in line:
                        host, port = line.strip().split(':')
                        proxies.append({
                            'http': f'http://{host}:{port}',
                            'https': f'http://{host}:{port}'
                        })
                return proxies
        except Exception as e:
            logger.error(f"Error fetching ProxyScrape proxies: {str(e)}")
        return []

    def _get_geonode_proxies(self) -> List[dict]:
        """Get proxies from Geonode"""
        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=100&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                proxies = []
                for proxy in data.get('data', []):
                    if proxy.get('ip') and proxy.get('port'):
                        proxies.append({
                            'http': f"http://{proxy['ip']}:{proxy['port']}",
                            'https': f"http://{proxy['ip']}:{proxy['port']}"
                        })
                return proxies
        except Exception as e:
            logger.error(f"Error fetching Geonode proxies: {str(e)}")
        return []

    def _get_hidemy_proxies(self) -> List[dict]:
        """Get proxies from HideMyName"""
        try:
            url = "https://hidemy.name/en/proxy-list/?type=s&anon=1"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Basic parsing of the HTML table
                proxies = []
                for line in response.text.split('\n'):
                    if '<td>' in line and ':' in line:
                        parts = line.split('<td>')
                        for part in parts:
                            if ':' in part and part[0].isdigit():
                                ip_port = part.split('</td>')[0].strip()
                                if ':' in ip_port:
                                    host, port = ip_port.split(':')
                                    proxies.append({
                                        'http': f'http://{host}:{port}',
                                        'https': f'http://{host}:{port}'
                                    })
                return proxies
        except Exception as e:
            logger.error(f"Error fetching HideMyName proxies: {str(e)}")
        return []

    def update_proxies(self) -> None:
        """Update the proxy list from all sources"""
        if (self.last_update and 
            datetime.now() - self.last_update < timedelta(seconds=self.update_interval)):
            return

        all_proxies = []
        for source in self.proxy_sources:
            try:
                proxies = source()
                all_proxies.extend(proxies)
            except Exception as e:
                logger.error(f"Error updating proxies from source: {str(e)}")

        # Remove duplicates
        unique_proxies = []
        seen = set()
        for proxy in all_proxies:
            proxy_key = f"{proxy['http']}"
            if proxy_key not in seen:
                seen.add(proxy_key)
                unique_proxies.append(proxy)

        self.proxies = unique_proxies
        self.last_update = datetime.now()
        logger.info(f"Updated proxy list with {len(self.proxies)} proxies")

    def get_proxy(self) -> Optional[dict]:
        """Get a random proxy from the list"""
        if not self.proxies or (
            self.last_update and 
            datetime.now() - self.last_update > timedelta(seconds=self.update_interval)
        ):
            self.update_proxies()
        
        return random.choice(self.proxies) if self.proxies else None

    def test_proxy(self, proxy: dict) -> bool:
        """Test if a proxy is working"""
        try:
            test_url = "https://www.etsy.com"
            response = requests.get(
                test_url,
                proxies=proxy,
                timeout=10,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            )
            return response.status_code == 200
        except:
            return False 