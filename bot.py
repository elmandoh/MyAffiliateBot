import os
import sys
import json
from atproto import Client
from groq import Groq

# 1. إضافة مسار المكتبة

sys.path.append(os.path.join(os.getcwd(), 'python'))
from iop.base import IopClient, IopRequest

# 2. إعداد العملاء
bsky = Client()
bsky.login(os.environ["BLUESKY_HANDLE"], os.environ["BLUESKY_PASSWORD"])
groq = Groq(api_key=os.environ["GROQ_API_KEY"])

USED_PRODUCTS_FILE = "used_products.json"

def get_used_products():
    if not os.path.exists(USED_PRODUCTS_FILE): return []
    with open(USED_PRODUCTS_FILE, 'r') as f: return json.load(f)

def save_used_product(product_id):
    used = get_used_products()
    used.append(str(product_id))
    with open(USED_PRODUCTS_FILE, 'w') as f: json.dump(used, f)

# 3. اقتراح المنتجات من Groq
def get_product_ideas():
    prompt = """Suggest 10 trending unique electronic products on AliExpress. 
    Return ONLY a raw JSON list. Do not include any markdown, 
    no backticks, no explanations. 
    Format: [{"name": "Product Name", "search_query": "search query"}]"""
    
    response = groq.chat.completions.create(
        messages=[{"role": "user", "content": prompt}], 
        model="llama-3.3-70b-versatile"
    )
    
    content = response.choices[0].message.content.strip()
    
    # تنظيف النص من أي رموز ماركداون قد يضيفها Groq
    content = content.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Raw content received: {content}")
        return [] # إرجاع قائمة فارغة لتجنب الانهيار

# 4. البحث وجلب البيانات
def get_aliexpress_product(query):
    client = IopClient("https://api-sg.aliexpress.com/sync", os.environ["ALIEXPRESS_APP_KEY"], os.environ["ALIEXPRESS_APP_SECRET"])
    request = IopRequest("aliexpress.affiliate.product.query")
    request.add_api_param("keywords", query)
    request.add_api_param("fields", "product_id,product_title,promotion_link,app_sale_price")
    
    response = client.execute(request)
    if response.code == "0":
        data = json.loads(response.body)
        products = data.get('aliexpress_affiliate_product_query_response', {}).get('resp_result', {}).get('result', {}).get('products', {}).get('product', [])
        return products[0] if products else None
    return None

# 5. صياغة المنشور
def generate_post(product):
    prompt = f"Write an engaging US-style marketing post for Bluesky about this product: {product['product_title']}. Price: {product['app_sale_price']}. Link: {product['promotion_link']}. Keep it short and viral."
    completion = groq.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return completion.choices[0].message.content

# --- تنفيذ الدورة ---
ideas = get_product_ideas()
for item in ideas:
    product = get_aliexpress_product(item['search_query'])
    if product and str(product['product_id']) not in get_used_products():
        # نشر المنشور
        post_text = generate_post(product)
        bsky.send_post(text=post_text)
        
        # حفظ المنتج لمنع تكراره
        save_used_product(product['product_id'])
        print(f"تم نشر المنتج: {product['product_title']}")
        break # نكتفي بمنتج واحد في كل دورة كل ساعتين
    else:
        continue
