import os
import hashlib
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# إعدادات الـ API
APP_KEY = os.getenv("ALIEXPRESS_APP_KEY", "").strip()
SECRET_KEY = os.getenv("ALIEXPRESS_APP_SECRET", "").strip()
TRACKING_ID = os.getenv("ALIEXPRESS_TRACKING_ID", "").strip()

def generate_aliexpress_sign(params, secret_key):
    sorted_keys = sorted(params.keys())
    sign_string = secret_key
    for key in sorted_keys:
        sign_string += f"{key}{str(params[key])}"
    sign_string += secret_key
    return hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()

def call_aliexpress_api(method, api_params={}):
    url = "https://api-sg.aliexpress.com/sync/api/asyn"
    sys_params = {
        "app_key": APP_KEY,
        "method": method,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "json",
        "v": "2.0",
        "sign_method": "md5"
    }
    all_params = {**sys_params, **api_params}
    all_params["sign"] = generate_aliexpress_sign(all_params, SECRET_KEY)
    response = requests.post(url, data=all_params, timeout=15)
    return response.json()

def save_to_rss(product, affiliate_link):
    filename = "products_feed.xml"
    if os.path.exists(filename):
        tree = ET.parse(filename)
        root = tree.getroot()
    else:
        root = ET.Element("rss", version="2.0")
        ET.SubElement(root, "channel")
    
    channel = root.find("channel")
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = product.get("product_title")
    ET.SubElement(item, "link").text = affiliate_link
    ET.SubElement(item, "price").text = product.get("sale_price")
    ET.SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    
    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    hot_res = call_aliexpress_api("aliexpress.affiliate.hotproduct.query", {
        "fields": "product_title,product_detail_url,sale_price",
        "tracking_id": TRACKING_ID, "page_size": "1"
    })
    
    product = hot_res.get("aliexpress_affiliate_hotproduct_query_response", {}).get("resp_result", {}).get("result", {}).get("products", {}).get("product", [{}])[0]
    
    if product:
        link_res = call_aliexpress_api("aliexpress.affiliate.link.generate", {
            "tracking_id": TRACKING_ID, "source_values": product.get("product_detail_url").split('?')[0]
        })
        aff_link = link_res.get("aliexpress_affiliate_link_generate_response", {}).get("resp_result", {}).get("result", {}).get("live_link_list", {}).get("live_link", [{}])[0].get("promotion_link")
        
        if aff_link:
            save_to_rss(product, aff_link)
            print("✅ تم تحديث ملف RSS بنجاح!")
