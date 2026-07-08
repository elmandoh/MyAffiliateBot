import os
import sys
from atproto import Client
from groq import Groq
import requests

# 1. توجيه البوت للمجلد 'python' الموجود في مستودعك
# بما أنك رفعت المجلد 'python' إلى المجلد الرئيسي للمشروع
python_sdk_path = os.path.join(os.getcwd(), 'python')
if python_sdk_path not in sys.path:
    sys.path.append(python_sdk_path)

# 2. استيراد المكتبة من المجلد الذي رفعته
# وفقاً لصورك، المكتبة موجودة داخل 'python/iop'
from iop.base import IopClient, IopRequest

# إعداد العملاء
bsky = Client()
bsky.login(os.environ["BLUESKY_HANDLE"], os.environ["BLUESKY_PASSWORD"])
groq = Groq(api_key=os.environ["GROQ_API_KEY"])

def get_aliexpress_product():
    # استخدام IopClient الخاص بالمكتبة التي رفعتها
    app_key = os.environ["ALIEXPRESS_APP_KEY"]
    app_secret = os.environ["ALIEXPRESS_APP_SECRET"]
    
    client = IopClient("https://api-sg.aliexpress.com/sync", app_key, app_secret)
    
    # بناء الطلب حسب هيكلية مكتبة IOP
    request = IopRequest("aliexpress.affiliate.hotproduct.query")
    request.add_api_param("commission_rate_min", "1000")
    request.add_api_param("fields", "product_title,promotion_link,app_sale_price")
    
    try:
        response = client.execute(request)
        if response.is_success():
            # تحويل النص إلى JSON لاستخراج البيانات
            import json
            data = json.loads(response.body)
            result = data.get('aliexpress_affiliate_hotproduct_query_response', {})\
                         .get('resp_result', {}).get('result', {})
            products = result.get('products', {}).get('product', [])
            return products[0] if products else None
        else:
            print(f"API Error: {response.message}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

# --- باقي الكود (generate_content و post_to_github_report) كما هو ---
# ...


def generate_content(prompt):
    completion = groq.chat.completions.create(
        messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile"
    )
    return completion.choices[0].message.content[:280]

    # تأكد من هذا الجزء في دالة post_to_github_report
def post_to_github_report(content):
    url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues"
    # لاحظ أننا نستخدم os.environ['GITHUB_TOKEN'] الذي مررناه من الـ Workflow
    headers = {"Authorization": f"token {os.environ['GITHUB_TOKEN']}"} 
    requests.post(url, json={"title": "Daily Bot Report", "body": f"Published: {content}"}, headers=headers)

# منطق العمل
# --- التشغيل الأساسي ---
product = get_aliexpress_product()

if product:
    # سيتم تنفيذ هذا الجزء فقط إذا تم جلب منتج سليم
    prompt = f"Write a casual, helpful US-style recommendation for {product['name']} (Price: {product['price']}). Include link: {product['link']}."
    post_content = generate_content(prompt)
    bsky.send_post(text=post_content)
    post_to_github_report(post_content)
    print("تم النشر بنجاح!")
else:
    # البوت سيتوقف هنا بسلام ولن يظهر أي خطأ أحمر
    print("لم يتم العثور على منتج سليم. البوت ينهي عمله بسلام.")
    exit(0)
