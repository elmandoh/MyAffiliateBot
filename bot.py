import requests
import json
import os
import random
import requests
import hmac
import hashlib
import time
from atproto import Client
from groq import Groq



import zipfile
import shutil

# 1. إعداد المسارات
sdk_zip = "aliexpress_sdk.zip"
sdk_folder = "aliexpress_sdk_content"
sdk_url = "https://ae-open-platform-public.oss-ap-southeast-1.aliyuncs.com/sdk/1.0.2-1699927624346NFOi.zip"

# 2. تحميل وفك الضغط تلقائياً
if not os.path.exists(sdk_folder):
    print("Downloading SDK...")
    response = requests.get(sdk_url)
    with open(sdk_zip, 'wb') as f:
        f.write(response.content)
    
    with zipfile.ZipFile(sdk_zip, 'r') as zip_ref:
        zip_ref.extractall(sdk_folder)
    
    # حذف ملف الزيپ بعد الفك
    os.remove(sdk_zip)
    print("SDK ready.")

# 3. إضافة المجلد لمسار البحث الخاص ببايثون
import sys
sys.path.append(os.path.join(os.getcwd(), sdk_folder))

# الآن يمكنك استيراد المكتبة وكأنها مثبتة
from aliexpress.api.rest import AliexpressAffiliateHotproductQueryRequest
from aliexpress.api import TopApiClient




# 1. إعداد العملاء
bsky = Client()
bsky.login(os.environ["BLUESKY_HANDLE"], os.environ["BLUESKY_PASSWORD"])
groq = Groq(api_key=os.environ["GROQ_API_KEY"])


from aliextop.api.rest import AliexpressAffiliateHotproductQueryRequest
from aliextop.api import TopApiClient

def get_aliexpress_product():
    # إعداد العميل باستخدام المكتبة الرسمية
    # الـ gateway الرسمي لـ AliExpress
    client = TopApiClient(
        app_key=os.environ["ALIEXPRESS_APP_KEY"],
        app_secret=os.environ["ALIEXPRESS_APP_SECRET"],
        top_gateway_url="https://api-sg.aliexpress.com/sync"
    )
    
    # إنشاء الطلب باستخدام الكلاس الرسمي
    req = AliexpressAffiliateHotproductQueryRequest()
    req.commission_rate_min = "1000"
    req.fields = "product_title,promotion_link,app_sale_price"
    
    try:
        # المكتبة تتكفل بعملية التوقيع (Signing) بالكامل
        resp = client.execute(req)
        
        # الوصول للبيانات (المكتبة ترجع البيانات بتنسيق Dictionary)
        products = resp.get('aliexpress_affiliate_hotproduct_query_response', {})\
                       .get('resp_result', {}).get('result', {}).get('products', {}).get('product', [])
        
        if products:
            return products[0]
            
    except Exception as e:
        print(f"SDK Error: {e}")
        
    return None
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
