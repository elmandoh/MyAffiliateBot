import json
import os
import sys
import time

# إعداد مسار المكتبة
sys.path.append(os.path.join(os.getcwd(), 'python'))
from iop.base import IopClient, IopRequest

# إعدادات العميل
client = IopClient("https://api-sg.aliexpress.com/sync", os.environ["ALIEXPRESS_APP_KEY"], os.environ["ALIEXPRESS_APP_SECRET"])

def get_deals():
    req = IopRequest("aliexpress.affiliate.product.query")
    
    # فلاتر البحث عن العروض:
    req.add_api_param("keywords", "coupon") # التركيز على المنتجات التي تدعم الكوبونات
    req.add_api_param("fields", "product_id,product_title,product_detail_url,app_sale_price,promotion_link")
    req.add_api_param("sort", "discount_desc") # الترتيب حسب الأعلى خصم
    
    resp = client.execute(req)
    
    if resp.code == "0":
        data = json.loads(resp.body)
        products = data.get('aliexpress_affiliate_product_query_response', {}).get('resp_result', {}).get('result', {}).get('products', {}).get('product', [])
        
        # حفظ النتائج في ملف
        with open("deals_feed.json", "w", encoding='utf-8') as f:
            json.dump(products, f, indent=4)
        print(f"تم العثور على {len(products)} عرض وحفظها في deals_feed.json")
    else:
        print(f"خطأ في الاتصال: {resp.message}")

if __name__ == "__main__":
    get_deals()
