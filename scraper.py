#!/usr/bin/env python3
"""
Specialized Zepto Brand Page Product Scraper

This script is specifically designed to scrape the Lay's brand page from Zepto
based on the actual page structure observed.
"""

import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import logging
from urllib.parse import urljoin
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZeptoLaysScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def set_location(self, latitude: str, longitude: str):
        """Set location cookies for the session"""
        self.session.cookies.update({
            'lat': latitude,
            'lng': longitude
        })
        logger.info(f"Location set to lat: {latitude}, lng: {longitude}")
    
    def get_page_content(self, url: str) -> BeautifulSoup:
        """Fetch and parse the page content"""
        try:
            logger.info(f"Fetching page: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except requests.RequestException as e:
            logger.error(f"Error fetching page: {e}")
            return None
    
    def extract_products_from_content(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract products by parsing the page content based on observed structure"""
        products = []
        
        # First try HTML structure extraction (more reliable)
        html_products = self._extract_from_html_structure(soup)
        if html_products:
            logger.info(f"Found {len(html_products)} products from HTML structure")
            return html_products
        
        # Fallback to text-based extraction
        page_text = soup.get_text()
        lines = [line.strip() for line in page_text.split('\n') if line.strip()]
        
        # Find product lines - they contain Lay's and prices
        product_lines = []
        for i, line in enumerate(lines):
            if 'Lay\'s' in line and '₹' in line:
                product_lines.append((i, line))
        
        logger.info(f"Found {len(product_lines)} product lines from text content")
        
        # Process each product line
        for position, (line_num, line) in enumerate(product_lines, 1):
            product = self._parse_product_line(line, position)
            if product['name'] and product['selling_price']:
                products.append(product)
        
        return products
    
    def _parse_product_line(self, line: str, position: int) -> Dict:
        """Parse a single product line"""
        product = {
            'name': '',
            'image_url': '',
            'product_id': '',
            'stock_availability': True,
            'sponsored': False,
            'mrp': '',
            'selling_price': '',
            'position': position
        }
        
        # Extract product name (everything before the first price)
        price_match = re.search(r'₹', line)
        if price_match:
            product['name'] = line[:price_match.start()].strip()
        
        # Extract product ID from line if it contains pvid pattern
        pvid_match = re.search(r'/pvid/([a-f0-9-]+)', line)
        if pvid_match:
            product['product_id'] = pvid_match.group(1)
        
        # Extract prices
        prices = re.findall(r'₹(\d+)', line)
        if prices:
            prices = [int(p) for p in prices]
            prices.sort()
            
            if len(prices) >= 2:
                product['selling_price'] = str(prices[0])
                product['mrp'] = str(prices[1])
            else:
                product['selling_price'] = str(prices[0])
        
        # Check for stock availability
        if 'sold out' in line.lower() or 'unavailable' in line.lower():
            product['stock_availability'] = False
        
        # Check for sponsored content
        if 'sponsored' in line.lower() or 'ad' in line.lower():
            product['sponsored'] = True
        
        return product
    
    def _extract_from_html_structure(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract products from HTML structure using specific CSS classes"""
        products = []
        
        # Find all product containers - look for divs with image and ADD button
        product_containers = soup.find_all('div', class_=lambda x: x and 'c8QQnr' in x and 'cCX8Kb' in x)
        
        logger.info(f"Found {len(product_containers)} product containers")
        
        # Also look for price containers to match with products
        price_containers = soup.find_all('div', class_=lambda x: x and 'cLeSKJ' in x and 'cJbxmR' in x)
        logger.info(f"Found {len(price_containers)} price containers")
        
        for position, container in enumerate(product_containers, 1):
            product = self._extract_product_from_container(container, position, price_containers)
            if product['name'] and product['selling_price'] and len(product['name']) < 200:  # Filter out invalid long names
                products.append(product)
        
        return products
    
    def _extract_product_from_container(self, container, position: int, price_containers=None) -> Dict:
        """Extract product data from a single container element"""
        product = {
            'name': '',
            'image_url': '',
            'product_id': '',
            'stock_availability': True,
            'sponsored': False,
            'mrp': '',
            'selling_price': '',
            'position': position
        }
        
        # Extract product ID from parent <a> tag href attribute
        parent_a = container.find_parent('a')
        if parent_a and parent_a.get('href'):
            href = parent_a.get('href')
            # Extract product ID from href after "pvid/"
            pvid_match = re.search(r'/pvid/([a-f0-9-]+)', href)
            if pvid_match:
                product['product_id'] = pvid_match.group(1)
        
        # Extract product name from image alt/title attribute (more reliable)
        img_elem = container.find('img')
        if img_elem:
            product['name'] = img_elem.get('alt', '') or img_elem.get('title', '')
            
            # Extract image URL
            img_src = img_elem.get('src')
            if img_src:
                product['image_url'] = urljoin('https://www.zeptonow.com', img_src)
        
        # If no name from image, try to extract from container text
        if not product['name']:
            container_text = container.get_text()
            lines = [line.strip() for line in container_text.split('\n') if line.strip()]
            
            # Find the product name (look for Lay's products, but filter out very long text)
            for line in lines:
                if (line.startswith('Lay\'s') and 
                    len(line) > len(product['name']) and 
                    len(line) < 200):  # Filter out very long text
                    product['name'] = line
        
        # Extract prices - try to find matching price container
        if price_containers and position <= len(price_containers):
            price_container = price_containers[position - 1]
            
            # Extract selling price (first price)
            selling_price_elem = price_container.find('p', class_=lambda x: x and 'cGFDG0' in x and 'cB6nZL' in x)
            if selling_price_elem:
                selling_price_text = selling_price_elem.get_text(strip=True)
                price_match = re.search(r'₹(\d+)', selling_price_text)
                if price_match:
                    product['selling_price'] = price_match.group(1)
            
            # Extract MRP (second price)
            mrp_elem = price_container.find('p', class_=lambda x: x and 'cFLlze' in x)
            if mrp_elem:
                mrp_text = mrp_elem.get_text(strip=True)
                price_match = re.search(r'₹(\d+)', mrp_text)
                if price_match:
                    product['mrp'] = price_match.group(1)
        
        # Fallback: look for price container within the product container
        if not product['selling_price'] and not product['mrp']:
            price_container = container.find('div', class_=lambda x: x and 'cLeSKJ' in x and 'cJbxmR' in x)
            if price_container:
                # Extract selling price (first price)
                selling_price_elem = price_container.find('p', class_=lambda x: x and 'cGFDG0' in x and 'cB6nZL' in x)
                if selling_price_elem:
                    selling_price_text = selling_price_elem.get_text(strip=True)
                    price_match = re.search(r'₹(\d+)', selling_price_text)
                    if price_match:
                        product['selling_price'] = price_match.group(1)
                
                # Extract MRP (second price)
                mrp_elem = price_container.find('p', class_=lambda x: x and 'cFLlze' in x)
                if mrp_elem:
                    mrp_text = mrp_elem.get_text(strip=True)
                    price_match = re.search(r'₹(\d+)', mrp_text)
                    if price_match:
                        product['mrp'] = price_match.group(1)
        
        # Final fallback: extract prices from container text
        if not product['selling_price'] and not product['mrp']:
            container_text = container.get_text()
            prices = re.findall(r'₹(\d+)', container_text)
            if prices:
                prices = sorted([int(p) for p in prices])
                if len(prices) >= 2:
                    product['selling_price'] = str(prices[0])
                    product['mrp'] = str(prices[1])
                else:
                    product['selling_price'] = str(prices[0])
        
        # Check for stock availability - look for ADD button
        add_button = container.find('button', string='ADD')
        product['stock_availability'] = add_button is not None
        
        # Check for sponsored content
        container_text = container.get_text()
        if 'sponsored' in container_text.lower() or 'ad' in container_text.lower():
            product['sponsored'] = True
        
        return product
    
    def _parse_span_group(self, spans, position: int) -> Dict:
        """Parse a group of spans into a product"""
        product = {
            'name': '',
            'image_url': '',
            'product_id': '',
            'stock_availability': True,
            'sponsored': False,
            'mrp': '',
            'selling_price': '',
            'position': position
        }
        
        # Find the product name
        for span in spans:
            text = span.get_text(strip=True)
            if text.startswith('Lay\'s') and len(text) > len(product['name']):
                product['name'] = text
                break
        
        # Find product ID from spans
        for span in spans:
            # Check if span contains href attribute or pvid pattern
            if span.name == 'a' and span.get('href'):
                href = span.get('href')
                pvid_match = re.search(r'/pvid/([a-f0-9-]+)', href)
                if pvid_match:
                    product['product_id'] = pvid_match.group(1)
                    break
            else:
                # Check span text for pvid pattern
                text = span.get_text(strip=True)
                pvid_match = re.search(r'/pvid/([a-f0-9-]+)', text)
                if pvid_match:
                    product['product_id'] = pvid_match.group(1)
                    break
        
        # Find prices
        prices = []
        for span in spans:
            text = span.get_text(strip=True)
            if '₹' in text:
                price_matches = re.findall(r'₹(\d+)', text)
                prices.extend([int(p) for p in price_matches])
        
        if prices:
            prices.sort()
            if len(prices) >= 2:
                product['selling_price'] = str(prices[0])
                product['mrp'] = str(prices[1])
            else:
                product['selling_price'] = str(prices[0])
        
        # Check for stock availability
        group_text = ' '.join([span.get_text(strip=True) for span in spans])
        if 'sold out' in group_text.lower() or 'unavailable' in group_text.lower():
            product['stock_availability'] = False
        
        # Check for sponsored content
        if 'sponsored' in group_text.lower() or 'ad' in group_text.lower():
            product['sponsored'] = True
        
        return product
    
    def scrape_lays_page(self, url: str, latitude: str = None, longitude: str = None) -> List[Dict]:
        """Scrape Lay's products from the Zepto page"""
        if latitude and longitude:
            self.set_location(latitude, longitude)
        
        soup = self.get_page_content(url)
        if not soup:
            return []
        
        products = self.extract_products_from_content(soup)
        logger.info(f"Extracted {len(products)} products")
        
        return products
    
    def save_to_csv(self, products: List[Dict], filename: str = 'products.csv'):
        """Save products to CSV file"""
        if not products:
            logger.warning("No products to save")
            return
        
        fieldnames = ['Product Name', 'Product Image URL', 'Product ID', 'Stock Availability', 
                     'Sponsored', 'MRP', 'Selling Price', 'Product Position']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for product in products:
                writer.writerow({
                    'Product Name': product['name'],
                    'Product Image URL': product['image_url'],
                    'Product ID': product['product_id'],
                    'Stock Availability': product['stock_availability'],
                    'Sponsored': product['sponsored'],
                    'MRP': product['mrp'],
                    'Selling Price': product['selling_price'],
                    'Product Position': product['position']
                })
        
        logger.info(f"Saved {len(products)} products to {filename}")

def main():
    """Main function to run the scraper"""
    # Configuration
    brand_url = "https://www.zeptonow.com/brand/Lay's/18d6cb72-65aa-4881-8984-a08aa295dd35"
    
    # Cities for location-based scraping
    cities = [
        {'name': 'Mumbai', 'lat': '19.0760', 'lng': '72.8777'},
        {'name': 'Delhi', 'lat': '28.7041', 'lng': '77.1025'},
        {'name': 'Bangalore', 'lat': '12.9716', 'lng': '77.5946'},
    ]
    
    scraper = ZeptoLaysScraper()
    all_products = []
    
    # Scrape from multiple locations
    for city in cities:
        logger.info(f"Scraping from {city['name']}...")
        products = scraper.scrape_lays_page(brand_url, city['lat'], city['lng'])
        
        # Add city information to products
        for product in products:
            product['city'] = city['name']
        
        all_products.extend(products)
        time.sleep(2)  # Be respectful to the server
    
    # Save all products to CSV
    if all_products:
        scraper.save_to_csv(all_products, 'products.csv')
        logger.info(f"Scraping completed! Found {len(all_products)} total products.")
        
        # Print first few products for verification
        print("\nFirst 5 products found:")
        for i, product in enumerate(all_products[:5]):
            print(f"{i+1}. {product['name']} - ₹{product['selling_price']} (MRP: ₹{product['mrp']})")
    else:
        logger.error("No products found. The page structure might have changed.")

if __name__ == "__main__":
    main()
