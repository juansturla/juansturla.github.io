import csv
import json
import os

CSV_FILE = 'lagallega_products.csv'
JSON_FILE = 'products.json'

def convert():
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found.")
        return

    products_by_barcode = {}
    
    with open(CSV_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            barcode = row.get('barcode', '').strip()
            if barcode:
                # Store by barcode. If multiple products have same barcode, 
                # we'll store the last one or we could store a list.
                # Usually barcodes are unique per product.
                products_by_barcode[barcode] = row

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(products_by_barcode, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully converted {len(products_by_barcode)} products to {JSON_FILE}")

if __name__ == "__main__":
    convert()
