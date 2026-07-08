import os
import sys
import json
from atproto import Client
from groq import Groq

# 1. توجيه المسار للمجلد 'python' الذي رفعته
sys.path.append(os.path.join(os.getcwd(), 'python'))

# 2. الاستيراد الصحيح للمكتبة المرفوعة
from iop.base import IopClient, IopRequest

# إعداد العملاء
bsky = Client()
bsky.login(os.environ["BLUESKY_HANDLE"], os.environ["BLUESKY_PASSWORD"])
groq = Groq(api_key=os.environ["GROQ_API_KEY"])

def get_aliexpress_product():
    # استخدام بيانات الاعتماد من GitHub Secrets
    app_key = os.environ["ALIEXPRESS_APP_KEY"]
    app_secret = os.environ["ALIEXPRESS_APP_SECRET"]
    
    # تهيئة العميل (IopClient هو الحل الصحيح للـ Signature)
    client = IopClient("https://api-sg.aliexpress.com/sync", app_key, app_secret)
    
    # بناء الطلب الصحيح
    request = IopRequest("aliexpress.affiliate.hotproduct.query")
    request.add_api_param("commission_rate_min", "1000")
    request.add_api_param("fields", "product_title,promotion_link,app_sale_price")
    
    # تنفيذ الطلب
    response = client.execute(request)
    
    # التحقق من الاستجابة (بناءً على هيكلية IopResponse)
    if response.body:
        data = json.loads(response.body)
        # الوصول للمنتجات من هيكل الـ JSON
        result = data.get('aliexpress_affiliate_hotproduct_query_response', {})\
                     .get('resp_result', {}).get('result', {})
        products = result.get('products', {}).get('product', [])
        return products[0] if products else None
    else:
        print(f"API Error: {response.type} - {response.message}")
        return None

# --- باقي الكود ---
product = get_aliexpress_product()
if product:
    print("تم جلب المنتج بنجاح!")
    # كمل باقي منطق النشر هنا...
else:
    print("لم يتم العثور على منتج.")
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
