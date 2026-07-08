import os
import sys
import json
from atproto import Client
from groq import Groq

# إضافة مسار مكتبة IOP
sys.path.append(os.path.join(os.getcwd(), 'python'))
from iop.base import IopClient, IopRequest

# إعداد العملاء
bsky = Client()
bsky.login(os.environ["BLUESKY_HANDLE"], os.environ["BLUESKY_PASSWORD"])
groq = Groq(api_key=os.environ["GROQ_API_KEY"])

def get_product_data(query):
    # 1. البحث عن المنتج
    client = IopClient("https://api-sg.aliexpress.com/sync", os.environ["ALIEXPRESS_APP_KEY"], os.environ["ALIEXPRESS_APP_SECRET"])
    req = IopRequest("aliexpress.affiliate.product.query")
    req.add_api_param("keywords", query)
    req.add_api_param("fields", "product_id,product_detail_url,product_title,app_sale_price")
    
    resp = client.execute(req)
    if resp.code == "0":
        data = json.loads(resp.body)
        products = data.get('aliexpress_affiliate_product_query_response', {}).get('resp_result', {}).get('result', {}).get('products', {}).get('product', [])
        return products[0] if products else None
    return None

def generate_affiliate_link(original_url):
    # 2. تحويل الرابط إلى رابط أفلييت
    client = IopClient("https://api-sg.aliexpress.com/sync", os.environ["ALIEXPRESS_APP_KEY"], os.environ["ALIEXPRESS_APP_SECRET"])
    req = IopRequest("aliexpress.affiliate.link.generate")
    req.add_api_param("promotion_link_type", "0")
    req.add_api_param("source_values", original_url)
    
    resp = client.execute(req)
    if resp.code == "0":
        data = json.loads(resp.body)
        return data['aliexpress_affiliate_link_generate_response']['resp_result']['result']['promotion_links']['promotion_link'][0]['promotion_link']
    return None

# --- منطق التشغيل ---
query = "Smart Watch" # أو اجعلها من Groq
product = get_product_data(query)

if product:
    affiliate_link = generate_affiliate_link(product['product_detail_url'])
    if affiliate_link:
        print(f"تم الحصول على الرابط: {affiliate_link}")
        # هنا تكملة كود النشر على Bluesky...
    else:
        print("فشل تحويل الرابط.")
else:
    print("لم يتم العثور على المنتج.")
