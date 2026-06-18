import urllib.request
import re
import csv
import time
import os

# Configuration
BASE_URL = "https://www.lagallega.com.ar/productosnl.asp"
BASE_DOMAIN = "https://www.lagallega.com.ar"
OUTPUT_FILE = "lagallega_products.csv"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Regex patterns
RE_PRODUCT_BLOCK = re.compile(r'<li class="cuadProd">.*?</li>', re.DOTALL)
RE_NAME = re.compile(r'<div class="desc">([^<]+)</div>')
RE_PRICE = re.compile(r"<div class='izq'>\$([^<]+)</div>")
RE_ID = re.compile(r"onClick=\"PCompra\('([^']+)'\);\"")
RE_IMAGE = re.compile(r'<img\s+src="([^"]+)"')
RE_BARCODE = re.compile(r'alt="(\d{8,14})\s*-')
RE_PAGINATION = re.compile(r'(\d+)\s+de\s+(\d+)')
RE_CATEGORY = re.compile(r"<div class='categ1'>.*?&nbsp;([^<]+)</div>", re.DOTALL | re.IGNORECASE)

def fetch_page(nl, pg=1):
    url = f"{BASE_URL}?nl={nl}&pg={pg}&TM=cx"
    print(f"Fetching: {url}")
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_products(html):
    products = []
    blocks = RE_PRODUCT_BLOCK.findall(html)
    for block in blocks:
        name_match = RE_NAME.search(block)
        price_match = RE_PRICE.search(block)
        id_match = RE_ID.search(block)
        image_match = RE_IMAGE.search(block)
        barcode_match = RE_BARCODE.search(block)
        
        if name_match and price_match and id_match:
            img_url = ""
            if image_match:
                img_path = image_match.group(1).strip()
                if img_path.startswith('/'):
                    img_url = f"{BASE_DOMAIN}{img_path}"
                elif img_path.startswith('http'):
                    img_url = img_path
                else:
                    img_url = f"{BASE_DOMAIN}/{img_path}"

            products.append({
                'id': id_match.group(1).strip(),
                'barcode': barcode_match.group(1) if barcode_match else "",
                'name': name_match.group(1).strip(),
                'price': price_match.group(1).replace('&nbsp;', '').strip(),
                'image_url': img_url
            })
    return products

def get_pagination_info(html):
    match = RE_PAGINATION.search(html)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 1, 1

def get_category_name(html):
    # Try to find the category name in breadcrumbs or header
    # <div class='categ1'>&nbsp;<img ...>&nbsp;almacen</div>
    # Let's try to refine the regex for category name
    match = re.search(r"<div class='categ1'>.*?&nbsp;([^<]+)</div>", html, re.IGNORECASE | re.DOTALL)
    if match:
        name = match.group(1).strip()
        # Clean up tags if any
        name = re.sub(r'<[^>]*>', '', name)
        return name
    return "Unknown"

def main():
    # We will probe top-level categories from 01 to 40
    categories_to_probe = [f"{i:02d}000000" for i in range(1, 41)]
    
    empty_consecutive = 0
    max_empty_consecutive = 5
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'barcode', 'name', 'price', 'category', 'category_id', 'image_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for nl in categories_to_probe:
            print(f"--- Processing Category: {nl} ---")
            html = fetch_page(nl, 1)
            if not html:
                continue
            
            if "No se han encontrado productos" in html:
                print(f"No products in category {nl}")
                empty_consecutive += 1
                if empty_consecutive >= max_empty_consecutive:
                    print(f"Reached {max_empty_consecutive} consecutive empty categories. Stopping.")
                    break
                continue
            
            empty_consecutive = 0
            
            cat_name = get_category_name(html)
            print(f"Category Name: {cat_name}")
            
            current_pg, total_pgs = get_pagination_info(html)
            print(f"Pages: {total_pgs}")
            
            for pg in range(1, total_pgs + 1):
                if pg > 1:
                    html = fetch_page(nl, pg)
                    if not html:
                        break
                
                products = extract_products(html)
                print(f"  Page {pg}: Found {len(products)} products")
                
                for p in products:
                    p['category'] = cat_name
                    p['category_id'] = nl
                    writer.writerow(p)
                
                # Be nice to the server
                time.sleep(0.5)

    print(f"Finished! Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
