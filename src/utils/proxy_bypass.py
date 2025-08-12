"""
Proxy rotation bypass for YouTube
"""
import random
import requests
import time

class ProxyBypass:
    def __init__(self):
        # Free proxy sources (for demo - in production use paid proxies)
        self.free_proxy_sources = [
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
        ]
        self.working_proxies = []
        self.last_proxy_refresh = 0
    
    def get_free_proxies(self):
        """Get free proxies (for demo purposes)"""
        proxies = []
        
        # Note: Free proxies are unreliable and often blocked
        # This is just for demonstration
        demo_proxies = [
            # These are example formats - real implementation would fetch from APIs
            {'http': 'http://proxy1.example.com:8080'},
            {'http': 'http://proxy2.example.com:3128'},
        ]
        
        return demo_proxies
    
    def test_proxy(self, proxy):
        """Test if a proxy is working"""
        try:
            response = requests.get(
                'https://httpbin.org/ip', 
                proxies=proxy, 
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def get_working_proxy(self):
        """Get a working proxy"""
        # Refresh proxy list every hour
        if time.time() - self.last_proxy_refresh > 3600:
            self.refresh_proxies()
        
        if self.working_proxies:
            return random.choice(self.working_proxies)
        
        return None
    
    def refresh_proxies(self):
        """Refresh the list of working proxies"""
        print("🔄 Refreshing proxy list...")
        
        all_proxies = self.get_free_proxies()
        self.working_proxies = []
        
        for proxy in all_proxies[:5]:  # Test only first 5 to save time
            if self.test_proxy(proxy):
                self.working_proxies.append(proxy)
        
        self.last_proxy_refresh = time.time()
        print(f"✅ Found {len(self.working_proxies)} working proxies")
    
    def get_proxy_opts(self, base_opts):
        """Add proxy to yt-dlp options"""
        proxy = self.get_working_proxy()
        
        if proxy and 'http' in proxy:
            base_opts['proxy'] = proxy['http']
            print(f"🌐 Using proxy: {proxy['http']}")
        
        return base_opts