#!/usr/bin/env python3
# friend_service.py - خدمة إدارة الأصدقاء (مستقلة)

import requests
import json
import time
import os
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# بيانات التشفير
ENCRYPTION_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
ENCRYPTION_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

# وظائف التشفير
def encrypt_packet(plain_text, key=ENCRYPTION_KEY, iv=ENCRYPTION_IV):
    plain_text_bytes = bytes.fromhex(plain_text)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text_bytes, AES.block_size))
    return cipher_text.hex()

def decrypt_packet(cipher_text, key=ENCRYPTION_KEY, iv=ENCRYPTION_IV):
    cipher_text_bytes = bytes.fromhex(cipher_text)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain_text = unpad(cipher.decrypt(cipher_text_bytes), AES.block_size)
    return plain_text.hex()

def Encrypt_ID(number):
    number = int(number)
    encoded_bytes = []
    while True:
        byte = number & 0x7F
        number >>= 7
        if number:
            byte |= 0x80
        encoded_bytes.append(byte)
        if not number:
            break
    return bytes(encoded_bytes).hex()

def encrypt_api(plain_text):
    return encrypt_packet(plain_text, ENCRYPTION_KEY, ENCRYPTION_IV)

def decrypt_api(cipher_text):
    return decrypt_packet(cipher_text, ENCRYPTION_KEY, ENCRYPTION_IV)

# وظيفة JWT المحدثة لـ OB52
def TOKEN_MAKER(OLD_ACCESS_TOKEN, NEW_ACCESS_TOKEN, OLD_OPEN_ID, NEW_OPEN_ID, uid):
    data = bytes.fromhex(
        '1a13323032352d31312d32362030313a35313a3238220966726565206669726528013a07312e3132302e314232416e64726f6964204f532039202f204150492d3238202850492f72656c2e636a772e32303232303531382e313134313333294a0848616e6468656c64520c4d544e2f537061636574656c5a045749464960800a68d00572033234307a2d7838362d3634205353453320535345342e3120535345342e32204156582041565832207c2032343030207c20348001e61e8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e329a012b476f6f676c657c36323566373136662d393161372d343935622d396631362d303866653964336336353333a2010e3137362e32382e3133392e313835aa01026172b201203433303632343537393364653836646134323561353263616164663231656564ba010134c2010848616e6468656c64ca010d4f6e65506c7573204135303130ea014063363961653230386661643732373338623637346232383437623530613361316466613235643161313966616537343566633736616334613065343134633934f00101ca020c4d544e2f537061636574656cd2020457494649ca03203161633462383065636630343738613434323033626638666163363132306635e003b5ee02e8039a8002f003af13f80384078004a78f028804b5ee029004a78f029804b5ee02b00404c80401d2043d2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f6c69622f61726de00401ea045f65363261623933353464386662356662303831646233333861636233333439317c2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f626173652e61706bf00406f804018a050233329a050a32303139313139303236a80503b205094f70656e474c455332b805ff01c00504e005be7eea05093372645f7061727479f205704b717348543857393347646347335a6f7a454e6646775648746d377171316552554e6149444e67526f626f7a4942744c4f695943633459367a767670634943787a514632734f453463627974774c7334785a62526e70524d706d5752514b6d654f35766373386e51594268777148374bf805e7e4068806019006019a060134a2060134b2062213521146500e590349510e460900115843395f005b510f685b560a6107576d0f0366'
    )
    data = data.replace(OLD_OPEN_ID.encode(), NEW_OPEN_ID.encode())
    data = data.replace(OLD_ACCESS_TOKEN.encode(), NEW_ACCESS_TOKEN.encode())
    d = encrypt_api(data.hex())
    Final_Payload = bytes.fromhex(d)
    
    headers = {
        "Host": "loginbp.ggpolarbear.com",
        "X-Unity-Version": "2018.4.11f1",
        "Accept": "*/*",
        "Authorization": "Bearer",
        "ReleaseVersion": "OB52",
        "X-GA": "v1 1",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(len(Final_Payload)),
        "User-Agent": "Free%20Fire/2019118692 CFNetwork/3826.500.111.2.2 Darwin/24.4.0",
        "Connection": "keep-alive"
    }
    
    URL = "https://loginbp.ggpolarbear.com/MajorLogin"
    RESPONSE = requests.post(URL, headers=headers, data=Final_Payload, verify=False)
    
    if RESPONSE.status_code == 200:
        if len(RESPONSE.text) < 10:
            return False
        BASE64_TOKEN = RESPONSE.text[RESPONSE.text.find("eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ"):-1]
        second_dot_index = BASE64_TOKEN.find(".", BASE64_TOKEN.find(".") + 1)
        BASE64_TOKEN = BASE64_TOKEN[:second_dot_index + 44]
        return BASE64_TOKEN
    else:
        print(f"MajorLogin failed with status: {RESPONSE.status_code}")
        return False

def fetch_jwt_token_direct(uid, password):
    """جلب التوكن مباشرة بدون استخدام API خارجي"""
    try:
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {
            "Host": "100067.connect.garena.com",
            "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close",
        }
        data = {
            "uid": f"{uid}",
            "password": f"{password}",
            "response_type": "token",
            "client_type": "2",
            "client_secret": "",
            "client_id": "100067",
        }
        
        response = requests.post(url, headers=headers, data=data, verify=False)
        print(f"📩 استجابة Garena API: {response.text}")
        
        data = response.json()
        
        if "access_token" not in data or "open_id" not in data:
            print(f"❌ مفاتيح مفقودة في الاستجابة: {data}")
            return None

        NEW_ACCESS_TOKEN = data['access_token']
        NEW_OPEN_ID = data['open_id']
        OLD_ACCESS_TOKEN = "c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94"
        OLD_OPEN_ID = "4306245793de86da425a52caadf21eed"
        
        token = TOKEN_MAKER(OLD_ACCESS_TOKEN, NEW_ACCESS_TOKEN, OLD_OPEN_ID, NEW_OPEN_ID, uid)
        if token:
            print(f"✅ تم توليد التوكن بنجاح: {token[:50]}...")
            return token
        else:
            print("❌ فشل توليد التوكن")
            return None
            
    except Exception as e:
        print(f"⚠️ خطأ أثناء جلب التوكن مباشرة: {e}")
        return None

def get_player_info(uid):
    """جلب معلومات اللاعب - النسخة المحدثة"""
    try:
        # استخدام API بديل موثوق
        res = requests.get(f"http://5.175.178.221:6005/get?uid={uid}", timeout=10, verify=False)
        if res.status_code == 200:
            data = res.json()
            if "AccountInfo" in data:
                info = data["AccountInfo"]
                name = info.get("AccountName", "غير معروف")
                region = info.get("AccountRegion", "N/A")
                level = info.get("AccountLevel", "N/A")
                return name, region, level
        return "غير معروف", "N/A", "N/A"
    except Exception as e:
        print(f"⚠️ Error fetching info for {uid}: {e}")
        return "غير معروف", "N/A", "N/A"

def send_friend_request(token, player_id):
    """إرسال طلب صداقة - النسخة المحدثة لـ OB52"""
    enc_id = Encrypt_ID(player_id)
    payload = f"08a7c4839f1e10{enc_id}1801" 
    encrypted_payload = encrypt_api(payload)
    
    url = "https://clientbp.ggblueshark.com/RequestAddingFriend"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB52",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    
    try:
        r = requests.post(url, headers=headers, data=bytes.fromhex(encrypted_payload), timeout=15, verify=False)
        
        if r.status_code == 200:
            if "BR_FRIEND_NOT_SAME_REGION" in r.text:
                return False, "لا يمكن إضافة اللاعب لأنه ليس في نفس منطقتك (السيرفر)"
            return True, "تم إرسال طلب الصداقة بنجاح!"
                    
        elif r.status_code == 400:
            if "BR_FRIEND_NOT_SAME_REGION" in r.text:
                return False, "لا يمكن إضافة اللاعب لأنه ليس في نفس منطقتك (السيرفر)"
            return False, "خطأ في الطلب - قد يكون اللاعب من منطقة مختلفة"
        elif r.status_code == 401:
            return False, "التوكن غير صالح أو منتهي الصلاحية"
        elif r.status_code == 404:
            return False, "اللاعب غير موجود أو خطأ في الاتصال بنقطة النهاية"
        else:
            return False, f"فشل إرسال الطلب. كود الخطأ: {r.status_code}"
            
    except Exception as e:
        return False, f"حدث خطأ أثناء إرسال الطلب: {str(e)}"

def remove_friend(token, player_id):
    """حذف صديق - النسخة المحدثة لـ OB52"""
    enc_id = Encrypt_ID(player_id)
    payload = f"08a7c4839f1e10{enc_id}1802"  
    encrypted_payload = encrypt_api(payload)
    
    url = "https://clientbp.ggblueshark.com/RemoveFriend"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB52",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    
    try:
        r = requests.post(url, headers=headers, data=bytes.fromhex(encrypted_payload), timeout=15, verify=False)
        
        if r.status_code == 200:
            return True, "تم الحذف بنجاح!"
        elif r.status_code == 401:
            return False, "التوكن غير صالح أو منتهي الصلاحية"
        elif r.status_code == 400:
            server_error = r.text.strip()
            if server_error:
                 return False, f"فشل الحذف. استجابة السيرفر: {server_error}"
            return False, "فشل الحذف. تحقق من الحمولة Protobuf"
        elif r.status_code == 404:
            return False, "اللاعب غير موجود في قائمة الأصدقاء"
        else:
            return False, f"فشل الحذف. كود الخطأ: {r.status_code}"
            
    except Exception as e:
        return False, f"حدث خطأ أثناء الحذف: {str(e)}"