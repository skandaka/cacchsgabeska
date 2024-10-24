# scraper.py
import requests
from bs4 import BeautifulSoup
import re
import concurrent.futures
import logging
from fake_useragent import UserAgent
from urllib.parse import urlparse
import tldextract

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
ua = UserAgent()


def get_page_content(url, timeout=10):
    headers = {'User-Agent': ua.random}
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {str(e)}")
        return None


def extract_emails(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return [email for email in emails if not email.lower().endswith(('.png', '.jpg', '.gif', '.jpeg', '.bmp'))]


def extract_business_name(soup, url):
    candidates = [
        soup.title.string if soup.title else None,
        soup.find('meta', property='og:title')['content'] if soup.find('meta', property='og:title') else None,
        soup.find('h1').text if soup.find('h1') else None,
    ]
    for candidate in candidates:
        if candidate:
            return candidate.strip().split('|')[0].strip()
    return tldextract.extract(url).domain.capitalize()


def extract_extra_info(soup, url):
    info = {}

    # Try to find a description
    description = soup.find('meta', attrs={'name': 'description'})
    if description:
        info['description'] = description['content']

    # Try to find keywords
    keywords = soup.find('meta', attrs={'name': 'keywords'})
    if keywords:
        info['keywords'] = keywords['content']

    # Try to find social media links
    social_media = []
    for link in soup.find_all('a', href=True):
        if any(sm in link['href'] for sm in ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com']):
            social_media.append(link['href'])
    if social_media:
        info['social_media'] = social_media

    # Try to find a contact page
    contact_link = soup.find('a', string=re.compile(r'contact', re.I))
    if contact_link and contact_link.has_attr('href'):
        info['contact_page'] = contact_link['href']

    return info


def scrape_website(url, advanced=False):
    content = get_page_content(url)
    if not content:
        return url, "Business Name Not Found", "Email Not Found", {}

    soup = BeautifulSoup(content, 'html.parser')
    business_name = extract_business_name(soup, url)
    emails = extract_emails(content)
    extra_info = extract_extra_info(soup, url)

    if advanced:
        # Implement additional advanced scraping logic here
        pass
    email = emails[0] if emails else "Email Not Found"
    logging.info(f"Scraped {url}: Business Name: {business_name}, Email: {email}")
    return url, business_name, email, extra_info

def simple_scrape_websites(urls):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda url: scrape_website(url, advanced=False), urls))
    return [result for result in results if result[2] != "Email Not Found"]

def advanced_scrape_websites(urls):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda url: scrape_website(url, advanced=True), urls))
    return [result for result in results if result[2] != "Email Not Found"]

if __name__ == "__main__":
    test_urls = ["https://example.com", "https://example.org"]
    print("Simple scraping results:")
    print(simple_scrape_websites(test_urls))
    print("\nAdvanced scraping results:")
    print(advanced_scrape_websites(test_urls))