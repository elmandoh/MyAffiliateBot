import os
import random
from atproto import Client
from groq import Groq
from aliexpress_api import AliexpressApi

# الإعدادات
bsky = Client()
bsky.login(os.environ["BLUESKY_HANDLE"], os.environ["BLUESKY_PASSWORD"])
groq = Groq(api_key=os.environ["GROQ_API_KEY"])
ali = AliexpressApi(os.environ["ALIEXPRESS_APP_KEY"], os.environ["ALIEXPRESS_APP_SECRET"], models="api.aliexpress.com")

def get_ai_response(prompt):
    completion = groq.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return completion.choices[0].message.content[:280]

def interact_with_others():
    # البحث عن منشورات تقنية حديثة في أمريكا
    posts = bsky.app.bsky.feed.search_posts(params={'q': 'smart home', 'limit': 5})
    for post in posts.posts:
        if random.random() > 0.5: # 50% فرصة للتعليق
            comment = get_ai_response(f"Write a friendly, insightful 1-sentence comment on this post: {post.record.text}")
            bsky.send_post(text=comment, reply_to=post.uri)
            print("تم التعليق على منشور!")
            break

def post_affiliate():
    products = ali.get_hot_products(cat_ids=[34], limit=1)
    p = products[0]
    prompt = f"Write a helpful, non-salesy recommendation for {p.product_title}. Link: {p.promotion_link}. Be conversational, like a friend."
    bsky.send_post(text=get_ai_response(prompt))

# المنطق الرئيسي: تفاعل ثم انشر
if random.choice([True, False]):
    interact_with_others()
post_affiliate()
