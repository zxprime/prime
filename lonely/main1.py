# Standard library imports
import os
import sys
import time
import json
import base64
import binascii
import pickle
import re
import socket
import threading
import ssl
import datetime
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from datetime import datetime

# Third-party imports
import requests
import psutil
import jwt
import urllib3
# pytz removed - using zoneinfo or UTC instead
import aiohttp
import asyncio
import random
from protobuf_decoder.protobuf_decoder import Parser
from google.protobuf.timestamp_pb2 import Timestamp
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from cfonts import render, say

# Local imports
from HIMO import *
from RIHAB import *
from NoTmeowl import (
    DEcwHisPErMsG_pb2,
    MajoRLoGinrEs_pb2,
    PorTs_pb2,
    MajoRLoGinrEq_pb2,
    sQ_pb2,
    Team_msg_pb2
)

# Timezone handling without pytz
try:
    # Python 3.9+ has zoneinfo
    from zoneinfo import ZoneInfo
    TIMEZONE_AVAILABLE = True
    TIMEZONE_UTIL = ZoneInfo
except ImportError:
    # Fallback for older Python versions
    TIMEZONE_AVAILABLE = False
    # Use UTC as default
    class UTCZone:
        def __init__(self, tzname="UTC"):
            self.tzname = tzname
        
        def __repr__(self):
            return f"UTCZone({self.tzname})"
    
    TIMEZONE_UTIL = UTCZone

#EMOTES BY NoTmeowl X CODEX
# FIXED BY NoTmeowl ❄️ 

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  

# Variables globales
#------------------------------------------#
online_writer = None
whisper_writer = None
spam_room = False
spammer_uid = None
spam_chat_id = None
spam_uid = None
Spy = False
Chat_Leave = False
fast_spam_running = False
fast_spam_task = None
custom_spam_running = False
custom_spam_task = None
spam_request_running = False
spam_request_task = None
evo_fast_spam_running = False
evo_fast_spam_task = None
evo_custom_spam_running = False
evo_custom_spam_task = None
lag_running = False
lag_task = None

# NEW: Store current group members
current_group_members = []
bot_uid = None

# ========== متغيرات جديدة للإعدادات ==========
BOT_NAME = "ＳＡＲＧＯ²²⁩"              # اسم البوت الأساسي
BOT_DISPLAY_NAME = "ＳＡＲＧＯ²²⁩_a_n_t_i_b_a_n"  # الاسم المعروض
CURRENT_UID = None
CURRENT_PW = None
# ============================================

# Emote mapping for evo commands
EMOTE_MAP = {
    1: 909000063,
    2: 909000081,
    3: 909000075,
    4: 909000085,
    5: 909000134,
    6: 909000098,
    7: 909035007,
    8: 909051012,
    9: 909042007,
    10: 909000012,
    11: 909051015,
    12: 909041002,
    13: 909039004,
    14: 909042008,
    15: 909051014,
    16: 909039012,
    17: 909040010,
    18: 909035010,
    19: 909000081,
    20: 909051003,
    21: 909034001
}

# Load emotes from JSON file
def load_emotes_from_json():
    try:
        with open('emotes.json', 'r') as f:
            emotes_data = json.load(f)
        emotes_map = {}
        for emote in emotes_data:
            if emote['Number'] != 'no':
                emotes_map[emote['Number']] = int(emote['Id'])
        return emotes_map
    except Exception as e:
        print(f"Error loading emotes.json: {e}")
        return {}

# Load the emotes mapping
GENERAL_EMOTES_MAP = load_emotes_from_json()

# ========== دوال تحميل ومراقبة الإعدادات ==========
def load_config():
    """تحميل إعدادات ملف JSON"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("[ERROR] ملف config.json غير موجود!")
        return None
    except json.JSONDecodeError:
        print("[ERROR] ملف config.json غير صالح!")
        return None
    except Exception as e:
        print(f"[ERROR] فشل تحميل ملف الإعدادات: {e}")
        return None

def update_bot_names_from_config(config):
    """تحديث أسماء البوت من ملف الإعدادات"""
    global BOT_NAME, BOT_DISPLAY_NAME
    if config and 'bot' in config:
        old_name = BOT_NAME
        old_display = BOT_DISPLAY_NAME
        BOT_NAME = config['bot'].get('name', BOT_NAME)
        BOT_DISPLAY_NAME = config['bot'].get('display_name', BOT_DISPLAY_NAME)
        if old_name != BOT_NAME or old_display != BOT_DISPLAY_NAME:
            print(f"[System] ✅ تم تحديث أسماء البوت: {BOT_NAME} / {BOT_DISPLAY_NAME}")
        return True
    return False

def check_config_changes():
    """التحقق من تغييرات ملف الإعدادات"""
    global CURRENT_UID, CURRENT_PW, BOT_NAME, BOT_DISPLAY_NAME
    
    config = load_config()
    if not config:
        return False, False
    
    # التحقق من تغيير UID أو كلمة المرور
    new_uid = config['account']['uid']
    new_pw = config['account']['password']
    
    account_changed = (new_uid != CURRENT_UID) or (new_pw != CURRENT_PW)
    
    # التحقق من تغيير أسماء البوت
    names_changed = update_bot_names_from_config(config)
    
    return account_changed, names_changed

async def config_monitor():
    """مراقبة ملف الإعدادات كل 5 ثواني"""
    global CURRENT_UID, CURRENT_PW
    
    # تحميل الإعدادات الحالية
    config = load_config()
    if config:
        CURRENT_UID = config['account']['uid']
        CURRENT_PW = config['account']['password']
        update_bot_names_from_config(config)
    
    while True:
        await asyncio.sleep(5)  # فحص كل 5 ثواني
        
        account_changed, names_changed = check_config_changes()
        
        if account_changed:
            print("[System] 🔄 تم تغيير بيانات الحساب! جاري إعادة تشغيل البوت...")
            # إعادة تشغيل العملية بالكامل
            os.execv(sys.executable, ['python'] + sys.argv)
# =================================================

# NEW FUNCTION: /r command implementation - FASTER VERSION
async def r_command_operation(team_code, target_uid, emote_id, key, iv, region):
    """Execute /r command: join team, send emote, then leave - FAST VERSION"""
    try:
        # Step 1: Join the team
        join_packet = await GenJoinSquadsPacket(team_code, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)
        await asyncio.sleep(1)  # Reduced wait time for join to complete
        
        # Step 2: Send emote to target UID (using direct emote ID)
        uid_int = int(target_uid)
        emote_packet = await Emote_k(uid_int, int(emote_id), key, iv, region)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', emote_packet)
        await asyncio.sleep(0.5)  # Reduced wait time for emote to be sent
        
        # Step 3: Leave the team (solo)
        leave_packet = await ExiT(None, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', leave_packet)
        await asyncio.sleep(1)  # Reduced wait time for leave to complete
        
        return True, f"Success! Joined team {team_code}, sent emote ID {emote_id} to {target_uid}, and left team."
    
    except Exception as e:
        return False, f"Error in /r command: {str(e)}"

# Helper functions for ghost join
def dec_to_hex(decimal):
    """Convert decimal to hex string"""
    hex_str = hex(decimal)[2:]
    return hex_str.upper() if len(hex_str) % 2 == 0 else '0' + hex_str.upper()

async def encrypt_packet(packet_hex, key, iv):
    """Encrypt packet using AES CBC"""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    packet_bytes = bytes.fromhex(packet_hex)
    padded_packet = pad(packet_bytes, AES.block_size)
    encrypted = cipher.encrypt(padded_packet)
    return encrypted.hex()

async def nmnmmmmn(packet_hex, key, iv):
    """Wrapper for encrypt_packet"""
    return await encrypt_packet(packet_hex, key, iv)

async def ghost_join_packet(player_id, secret_code, key, iv):
    """Create ghost join packet"""
    try:
        # Create a simple packet structure for joining
        # This is a basic implementation - adjust based on your needs
        packet_data = f"01{dec_to_hex(len(secret_code))}{secret_code.encode().hex()}"
        
        # Encrypt the packet
        encrypted_packet = await encrypt_packet(packet_data, key, iv)
        
        # Create header
        header_length = len(encrypted_packet) // 2
        header_length_hex = dec_to_hex(header_length)
        
        # Build final packet based on header length
        if len(header_length_hex) == 2:
            final_packet = "0515000000" + header_length_hex + encrypted_packet
        elif len(header_length_hex) == 3:
            final_packet = "051500000" + header_length_hex + encrypted_packet
        elif len(header_length_hex) == 4:
            final_packet = "05150000" + header_length_hex + encrypted_packet
        elif len(header_length_hex) == 5:
            final_packet = "0515000" + header_length_hex + encrypted_packet
        else:
            final_packet = "0515000000" + header_length_hex + encrypted_packet
            
        return bytes.fromhex(final_packet)
        
    except Exception as e:
        print(f"Error creating ghost join packet: {e}")
        return None

async def lag_team_loop(team_code, key, iv, region):
    """Rapid join/leave loop to create lag"""
    global lag_running
    count = 0
    
    while lag_running:
        try:
            # Join the team
            join_packet = await GenJoinSquadsPacket(team_code, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)
            
            # Very short delay before leaving
            await asyncio.sleep(0.01)  # 10 milliseconds
            
            # Leave the team
            leave_packet = await ExiT(None, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', leave_packet)
            
            count += 1
            print(f"Lag cycle #{count} completed for team: {team_code}")
            
            # Short delay before next cycle
            await asyncio.sleep(0.01)  # 10 milliseconds between cycles
            
        except Exception as e:
            print(f"Error in lag loop: {e}")
            # Continue the loop even if there's an error
            await asyncio.sleep(0.1)

async def general_emote_spam(uids, emote_number, key, iv, region):
    """Send general emotes based on number mapping from JSON file"""
    try:
        emote_id = GENERAL_EMOTES_MAP.get(str(emote_number))
        if not emote_id:
            return False, f"Invalid emote number! Use numbers from 1-{len(GENERAL_EMOTES_MAP)}"
        
        success_count = 0
        for uid in uids:
            try:
                uid_int = int(uid)
                H = await Emote_k(uid_int, emote_id, key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                success_count += 1
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Error sending general emote to {uid}: {e}")
        
        return True, f"Sent emote {emote_number} (ID: {emote_id}) to {success_count} player(s)"
    
    except Exception as e:
        return False, f"Error in general_emote_spam: {str(e)}"

# NEW FUNCTION: Random evolution emote spam to command sender - 2.5 SECONDS DELAY
async def random_evo_emote_spam_sender(key, iv, region):
    """Send all 21 evolution emotes in random order to command sender - 2.5 SECONDS DELAY"""
    try:
        # Get all evolution emote IDs (1-21)
        emote_ids = list(EMOTE_MAP.values())
        
        # Shuffle the emotes for random order
        random.shuffle(emote_ids)
        
        success_count = 0
        total_emotes = len(emote_ids)
        total_time = total_emotes * 2.5  # Calculate total time
        
        for emote_id in emote_ids:
            try:
                # Use the UID of the person who sent the command
                uid_int = int(uid)
                H = await Emote_k(uid_int, emote_id, key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                success_count += 1
                
                # Get emote number from ID for display
                emote_number = [k for k, v in EMOTE_MAP.items() if v == emote_id][0]
                print(f"Random: Sent evolution emote {emote_number} (ID: {emote_id}) to command sender {uid} - {success_count}/{total_emotes}")
                
                await asyncio.sleep(2.5)  # 2.5 seconds delay between emotes
            except Exception as e:
                print(f"Error sending emote {emote_id} to command sender: {e}")
        
        return True, f"BoT Come Online Now You Can Use Commonds "
    
    except Exception as e:
        return False, f"Error in random_evo_emote_spam_sender: {str(e)}"

# UPDATED FUNCTION: Dance - ALL 21 emotes to specified UIDs - 2.5 SECONDS DELAY
async def dance_group_emotes(uids, key, iv, region):
    """Send ALL 21 evolution emotes to specified UIDs - 2.5 SECONDS DELAY"""
    try:
        # Get all evolution emote IDs (1-21)
        emote_ids = list(EMOTE_MAP.values())
        
        # Shuffle the emotes for random order
        random.shuffle(emote_ids)
        
        success_count = 0
        total_emotes = len(emote_ids)
        total_time = total_emotes * 2.5  # Calculate total time
        
        print(f"Dance: Sending to {len(uids)} players: {uids}")
        
        for emote_id in emote_ids:
            try:
                # Send to EACH specified UID individually
                emote_sent_count = 0
                for member_uid in uids:
                    try:
                        uid_int = int(member_uid)
                        H = await Emote_k(uid_int, emote_id, key, iv, region)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                        emote_sent_count += 1
                        print(f"Dance: Sent emote to UID {member_uid}")
                    except Exception as e:
                        print(f"Error sending to UID {member_uid}: {e}")
                
                success_count += 1
                
                # Get emote number from ID for display
                emote_number = [k for k, v in EMOTE_MAP.items() if v == emote_id][0]
                print(f"Dance: Sent evolution emote {emote_number} (ID: {emote_id}) to {emote_sent_count} players - {success_count}/{total_emotes}")
                
                await asyncio.sleep(2.5)  # 2.5 seconds delay between emotes
            except Exception as e:
                print(f"Error sending dance emote {emote_id} to group: {e}")
        
        return True, f"🎉 Ultimate dance party! Sent ALL {success_count} evolution emotes (1-21) to {len(uids)} players! (2.5s delay)"
    
    except Exception as e:
        return False, f"Error in dance_group_emotes: {str(e)}"
 

#CHAT WITH AI
def talk_with_ai(question):
    url = f"http://217.154.239.23:14008/execute_command_all?command=/AlliFF=5357804"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        msg = data["message"]["content"]
        return msg
    else:
        return "An error occurred while connecting to the server."
#SPAM REQUESTS

####################################
#CHECK ACCOUNT IS BANNED

Hr = {
    'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/x-www-form-urlencoded",
    'Expect': "100-continue",
    'X-Unity-Version': "2018.4.11f1",
    'X-GA': "v1 1",
    'ReleaseVersion': "OB52"}

# ---- Random Colores ----
def get_random_color():
    colors = [
        "[FF0000]", "[00FF00]", "[0000FF]", "[FFFF00]", "[FF00FF]", "[00FFFF]", "[FFFFFF]", "[FFA500]",
        "[A52A2A]", "[800080]", "[000000]", "[808080]", "[C0C0C0]", "[FFC0CB]", "[FFD700]", "[ADD8E6]",
        "[90EE90]", "[D2691E]", "[DC143C]", "[00CED1]", "[9400D3]", "[F08080]", "[20B2AA]", "[FF1493]",
        "[7CFC00]", "[B22222]", "[FF4500]", "[DAA520]", "[00BFFF]", "[00FF7F]", "[4682B4]", "[6495ED]",
        "[5F9EA0]", "[DDA0DD]", "[E6E6FA]", "[B0C4DE]", "[556B2F]", "[8FBC8F]", "[2E8B57]", "[3CB371]",
        "[6B8E23]", "[808000]", "[B8860B]", "[CD5C5C]", "[8B0000]", "[FF6347]", "[FF8C00]", "[BDB76B]",
        "[9932CC]", "[8A2BE2]", "[4B0082]", "[6A5ACD]", "[7B68EE]", "[4169E1]", "[1E90FF]", "[191970]",
        "[00008B]", "[000080]", "[008080]", "[008B8B]", "[B0E0E6]", "[AFEEEE]", "[E0FFFF]", "[F5F5DC]",
        "[FAEBD7]"
    ]
    return random.choice(colors)

async def encrypted_proto(encoded_hex):
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(encoded_hex, AES.block_size)
    encrypted_payload = cipher.encrypt(padded_message)
    return encrypted_payload
    
async def GeNeRaTeAccEss(uid , password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": (await Ua()),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"}
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=Hr, data=data) as response:
            if response.status != 200: return "Failed to get access token"
            data = await response.json()
            open_id = data.get("open_id")
            access_token = data.get("access_token")
            return (open_id, access_token) if open_id and access_token else (None, None)

async def EncRypTMajoRLoGin(open_id, access_token):
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    major_login.event_time = str(datetime.now())[:-7]
    major_login.game_name = "free fire"
    major_login.platform_id = 1
    major_login.client_version = "1.120.2"
    major_login.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_type = "WIFI"
    major_login.screen_width = 1920
    major_login.screen_height = 1080
    major_login.screen_dpi = "280"
    major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major_login.memory = 3003
    major_login.gpu_renderer = "Adreno (TM) 640"
    major_login.gpu_version = "OpenGL ES 3.1 v1.46"
    major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip = "223.191.51.89"
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    memory_available = major_login.memory_available
    memory_available.version = 55
    memory_available.hidden_value = 81
    major_login.access_token = access_token
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Verizon"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.external_storage_total = 36235
    major_login.external_storage_available = 31335
    major_login.internal_storage_total = 2519
    major_login.internal_storage_available = 703
    major_login.game_disk_storage_available = 25010
    major_login.game_disk_storage_total = 26628
    major_login.external_sdcard_avail_storage = 32992
    major_login.external_sdcard_total_storage = 36235
    major_login.login_by = 3
    major_login.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major_login.reg_avatar = 1
    major_login.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major_login.channel_type = 3
    major_login.cpu_type = 2
    major_login.cpu_architecture = "64"
    major_login.client_version_code = "2019116753"
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 16383
    major_login.login_open_id_type = 4
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    major_login.loading_time = 13564
    major_login.release_channel = "android"
    major_login.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major_login.android_engine_init_flag = 110009
    major_login.if_push = 1
    major_login.is_vpn = 1
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    string = major_login.SerializeToString()
    return  await encrypted_proto(string)

async def MajorLogin(payload):
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200: return await response.read()
            return None

async def GetLoginData(base_url, payload, token):
    url = f"{base_url}/GetLoginData"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    Hr['Authorization']= f"Bearer {token}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200: return await response.read()
            return None


async def DecRypTMajoRLoGin(MajoRLoGinResPonsE):
    proto = MajoRLoGinrEs_pb2.MajorLoginRes()
    proto.ParseFromString(MajoRLoGinResPonsE)
    return proto

async def DecRypTLoGinDaTa(LoGinDaTa):
    proto = PorTs_pb2.GetLoginData()
    proto.ParseFromString(LoGinDaTa)
    return proto

async def DecodeWhisperMessage(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = DEcwHisPErMsG_pb2.DecodeWhisper()
    proto.ParseFromString(packet)
    return proto
    
async def decode_team_packet(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = sQ_pb2.recieved_chat()
    proto.ParseFromString(packet)
    return proto
    
async def xAuThSTarTuP(TarGeT, token, timestamp, key, iv):
    uid_hex = hex(TarGeT)[2:]
    uid_length = len(uid_hex)
    encrypted_timestamp = await DecodE_HeX(timestamp)
    encrypted_account_token = token.encode().hex()
    encrypted_packet = await EnC_PacKeT(encrypted_account_token, key, iv)
    encrypted_packet_length = hex(len(encrypted_packet) // 2)[2:]
    if uid_length == 9: headers = '0000000'
    elif uid_length == 8: headers = '00000000'
    elif uid_length == 10: headers = '000000'
    elif uid_length == 7: headers = '000000000'
    else: print('Unexpected length') ; headers = '0000000'
    return f"0115{headers}{uid_hex}{encrypted_timestamp}00000{encrypted_packet_length}{encrypted_packet}"
     
async def cHTypE(H):
    if not H: return 'Squid'
    elif H == 1: return 'CLan'
    elif H == 2: return 'PrivaTe'
    
async def SEndMsG(H , message , Uid , chat_id , key , iv):
    TypE = await cHTypE(H)
    if TypE == 'Squid': msg_packet = await xSEndMsgsQ(message , chat_id , key , iv)
    elif TypE == 'CLan': msg_packet = await xSEndMsg(message , 1 , chat_id , chat_id , key , iv)
    elif TypE == 'PrivaTe': msg_packet = await xSEndMsg(message , 2 , Uid , Uid , key , iv)
    return msg_packet

async def SEndPacKeT(OnLinE , ChaT , TypE , PacKeT):
    if TypE == 'ChaT' and ChaT: whisper_writer.write(PacKeT) ; await whisper_writer.drain()
    elif TypE == 'OnLine': online_writer.write(PacKeT) ; await online_writer.drain()
    else: return 'UnsoPorTed TypE ! >> ErrrroR (:():)' 

async def safe_send_message(chat_type, message, target_uid, chat_id, key, iv, max_retries=3):
    """Safely send message with retry mechanism"""
    for attempt in range(max_retries):
        try:
            P = await SEndMsG(chat_type, message, target_uid, chat_id, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
            print(f"Message sent successfully on attempt {attempt + 1}")
            return True
        except Exception as e:
            print(f"Failed to send message (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)  # Wait before retry
    return False

async def fast_emote_spam(uids, emote_id, key, iv, region):
    """Fast emote spam function that sends emotes rapidly"""
    global fast_spam_running
    count = 0
    max_count = 25  # Spam 25 times
    
    while fast_spam_running and count < max_count:
        for uid in uids:
            try:
                uid_int = int(uid)
                H = await Emote_k(uid_int, int(emote_id), key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            except Exception as e:
                print(f"Error in fast_emote_spam for uid {uid}: {e}")
        
        count += 1
        await asyncio.sleep(0.1)  # 0.1 seconds interval between spam cycles

# NEW FUNCTION: Custom emote spam with specified times
async def custom_emote_spam(uid, emote_id, times, key, iv, region):
    """Custom emote spam function that sends emotes specified number of times"""
    global custom_spam_running
    count = 0
    
    while custom_spam_running and count < times:
        try:
            uid_int = int(uid)
            H = await Emote_k(uid_int, int(emote_id), key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            count += 1
            await asyncio.sleep(0.1)  # 0.1 seconds interval between emotes
        except Exception as e:
            print(f"Error in custom_emote_spam for uid {uid}: {e}")
            break

# FIXED FUNCTION: Faster spam request loop - Sends exactly 30 requests quickly
async def spam_request_loop(target_uid, key, iv, region):
    """Spam request function that creates group and sends join requests in loop - FIXED VERSION"""
    global spam_request_running
    count = 0
    max_requests = 30  # Send exactly 30 requests
    
    while spam_request_running and count < max_requests:
        try:
            # Create squad
            PAc = await OpEnSq(key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', PAc)
            await asyncio.sleep(0.3)  # Increased delay for stability
            
            # Send invite
            V = await SEnd_InV(5, int(target_uid), key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', V)
            await asyncio.sleep(0.3)  # Increased delay for stability
            
            # Leave squad
            E = await ExiT(None, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
            
            count += 1
            print(f"Sent request #{count} to {target_uid}")
            
            # Delay between requests
            await asyncio.sleep(0.8)  # Increased delay for stability
            
        except Exception as e:
            print(f"Error in spam_request_loop for uid {target_uid}: {e}")
            # Continue with next request instead of breaking
            await asyncio.sleep(1)

# NEW FUNCTION: Evolution emote spam with mapping
async def evo_emote_spam(uids, number, key, iv, region):
    """Send evolution emotes based on number mapping"""
    try:
        emote_id = EMOTE_MAP.get(int(number))
        if not emote_id:
            return False, f"Invalid number! Use 1-21 only."
        
        success_count = 0
        for uid in uids:
            try:
                uid_int = int(uid)
                H = await Emote_k(uid_int, emote_id, key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                success_count += 1
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Error sending evo emote to {uid}: {e}")
        
        return True, f"Sent evolution emote {number} (ID: {emote_id}) to {success_count} player(s)"
    
    except Exception as e:
        return False, f"Error in evo_emote_spam: {str(e)}"

# NEW FUNCTION: Fast evolution emote spam
async def evo_fast_emote_spam(uids, number, key, iv, region):
    """Fast evolution emote spam function"""
    global evo_fast_spam_running
    count = 0
    max_count = 25  # Spam 25 times
    
    emote_id = EMOTE_MAP.get(int(number))
    if not emote_id:
        return False, f"Invalid number! Use 1-21 only."
    
    while evo_fast_spam_running and count < max_count:
        for uid in uids:
            try:
                uid_int = int(uid)
                H = await Emote_k(uid_int, emote_id, key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            except Exception as e:
                print(f"Error in evo_fast_emote_spam for uid {uid}: {e}")
        
        count += 1
        await asyncio.sleep(0.1)  # CHANGED: 0.5 seconds to 0.1 seconds
    
    return True, f"Completed fast evolution emote spam {count} times"

# NEW FUNCTION: Custom evolution emote spam with specified times
async def evo_custom_emote_spam(uids, number, times, key, iv, region):
    """Custom evolution emote spam with specified repeat times"""
    global evo_custom_spam_running
    count = 0
    
    emote_id = EMOTE_MAP.get(int(number))
    if not emote_id:
        return False, f"Invalid number! Use 1-21 only."
    
    while evo_custom_spam_running and count < times:
        for uid in uids:
            try:
                uid_int = int(uid)
                H = await Emote_k(uid_int, emote_id, key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            except Exception as e:
                print(f"Error in evo_custom_emote_spam for uid {uid}: {e}")
        
        count += 1
        await asyncio.sleep(0.1)  # CHANGED: 0.5 seconds to 0.1 seconds
    
    return True, f"Completed custom evolution emote spam {count} times"

async def TcPOnLine(ip, port, key, iv, AutHToKen, reconnect_delay=0.5):
    global online_writer , spam_room , whisper_writer , spammer_uid , spam_chat_id , spam_uid , XX , uid , Spy,data2, Chat_Leave, fast_spam_running, fast_spam_task, custom_spam_running, custom_spam_task, spam_request_running, spam_request_task, evo_fast_spam_running, evo_fast_spam_task, evo_custom_spam_running, evo_custom_spam_task, lag_running, lag_task, current_group_members  # ADD current_group_members

    while True:
        try:
            reader , writer = await asyncio.open_connection(ip, int(port))
            online_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen)
            online_writer.write(bytes_payload)
            await online_writer.drain()
            while True:
                data2 = await reader.read(9999)
                if not data2: break
                
                # NEW: Capture group members from squad data
                if data2.hex().startswith('0500') and len(data2.hex()) > 1000:
                    try:
                        print(data2.hex()[10:])
                        packet = await DeCode_PackEt(data2.hex()[10:])
                        print(packet)
                        packet = json.loads(packet)
                        OwNer_UiD , CHaT_CoDe , SQuAD_CoDe = await GeTSQDaTa(packet)

                        # NEW: Extract group members from packet
                        if 'members' in packet:
                            try:
                                current_group_members = []
                                for member in packet['members']:
                                    if 'uid' in member and str(member['uid']) != str(bot_uid):
                                        current_group_members.append(str(member['uid']))
                                print(f"Group members updated: {current_group_members}")
                            except Exception as e:
                                print(f"Error updating group members: {e}")

                        JoinCHaT = await AutH_Chat(3 , OwNer_UiD , CHaT_CoDe, key,iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', JoinCHaT)
             
                        P = await SEndMsG(0 , message , OwNer_UiD , OwNer_UiD , key , iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                    except Exception as e:
                        print(f"Error processing group data: {e}")
                        if data2.hex().startswith('0500') and len(data2.hex()) > 1000:
                            try:
                                print(data2.hex()[10:])
                                packet = await DeCode_PackEt(data2.hex()[10:])
                                print(packet)
                                packet = json.loads(packet)
                                OwNer_UiD , CHaT_CoDe , SQuAD_CoDe = await GeTSQDaTa(packet)

                                JoinCHaT = await AutH_Chat(3 , OwNer_UiD , CHaT_CoDe, key,iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', JoinCHaT)
                                                              
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            except:
                                pass

            online_writer.close() ; await online_writer.wait_closed() ; online_writer = None

        except Exception as e: print(f"- ErroR With {ip}:{port} - {e}") ; online_writer = None
        await asyncio.sleep(reconnect_delay)
                            
async def TcPChaT(ip, port, AutHToKen, key, iv, LoGinDaTaUncRypTinG, ready_event, region , reconnect_delay=0.5):
    print(region, 'TCP CHAT')

    global spam_room , whisper_writer , spammer_uid , spam_chat_id , spam_uid , online_writer , chat_id , XX , uid , Spy,data2, Chat_Leave, fast_spam_running, fast_spam_task, custom_spam_running, custom_spam_task, spam_request_running, spam_request_task, evo_fast_spam_running, evo_fast_spam_task, evo_custom_spam_running, evo_custom_spam_task, lag_running, lag_task, current_group_members, bot_uid  # ADD current_group_members and bot_uid

    while True:
        try:
            reader , writer = await asyncio.open_connection(ip, int(port))
            whisper_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen)
            whisper_writer.write(bytes_payload)
            await whisper_writer.drain()
            ready_event.set()
            if LoGinDaTaUncRypTinG.Clan_ID:
                clan_id = LoGinDaTaUncRypTinG.Clan_ID
                clan_compiled_data = LoGinDaTaUncRypTinG.Clan_Compiled_Data
                print('\n - TarGeT BoT in CLan ! ')
                print(f' - Clan Uid > {clan_id}')
                print(f' - BoT ConnEcTed WiTh CLan ChaT SuccEssFuLy ! ')
                pK = await AuthClan(clan_id , clan_compiled_data , key , iv)
                if whisper_writer: whisper_writer.write(pK) ; await whisper_writer.drain()
            while True:
                data = await reader.read(9999)
                if not data: break
                
                if data.hex().startswith("120000"):

                    msg = await DeCode_PackEt(data.hex()[10:])
                    chatdata = json.loads(msg)
                    try:
                        response = await DecodeWhisperMessage(data.hex()[10:])
                        uid = response.Data.uid
                        chat_id = response.Data.Chat_ID
                        XX = response.Data.chat_type
                        inPuTMsG = response.Data.msg.lower()
                        
                        # Debug print to see what we're receiving
                        print(f"Received message: {inPuTMsG} from UID: {uid} in chat type: {XX}")
                        
                    except:
                        response = None


                    if response:
                        # ALL COMMANDS NOW WORK IN ALL CHAT TYPES (SQUAD, GUILD, PRIVATE)
                        
                        # UPDATED DANCE COMMAND - Now requires UIDs
                        if inPuTMsG.strip().startswith('/dance '):
                            print('Processing dance command with UIDs in any chat type')
                            
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 2:
                                error_msg = f" [C][FF0000]❌ ERROR! Usage: /dance uid1 [uid2] [uid3] [uid4]\nExample: /dance 123456789 987654321\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                # Parse UIDs from command
                                uids = []
                                for part in parts[1:]:
                                    if part.isdigit() and len(part) > 3:  # UIDs should be longer than 3 digits
                                        uids.append(part)
                                
                                if not uids:
                                    error_msg = f" [C][FF0000]❌ ERROR! No valid UIDs provided! Usage: /dance uid1 [uid2] [uid3] [uid4]\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                else:
                                    total_time = 21 * 2.5  # 21 emotes × 2.5 seconds
                                    initial_message = f" [C]{get_random_color()}\n🎉 Starting ULTIMATE dance party with ALL 21 evolution emotes...\nSending to {len(uids)} players...\nThis will take about {total_time} seconds...\nEmote change every 2.5 seconds...\n"
                                    await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                                    
                                    success, result_msg = await dance_group_emotes(uids, key, iv, region)
                                    
                                    if success:
                                        success_msg = f" [C][00FF00]✅ {result_msg}\n"
                                        await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                                    else:
                                        error_msg = f" [C][FF0000]❌ ERROR! {result_msg}\n"
                                        await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        # NEW /r COMMAND - Team join, emote trigger, then leave - FAST VERSION
                        if inPuTMsG.strip().startswith('/r '):
                            print('Processing /r command in any chat type')
                            
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 4:
                                error_msg = f" [C][FF0000]❌ ERROR! Usage: /r [team_code] [uid] [emote_id]\nExample: /r ABC123 123456789 909000001\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                team_code = parts[1]
                                target_uid = parts[2]
                                emote_id = parts[3]
                                
                                initial_message = f" [C]{get_random_color()}\nExecuting /r command...\nJoining team: {team_code}\nTarget UID: {target_uid}\nEmote ID: {emote_id}\nSpeed: 0.5 seconds\n"
                                await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                                
                                # Execute the /r command operation with direct emote ID
                                success, result_msg = await r_command_operation(team_code, target_uid, emote_id, key, iv, region)
                                
                                if success:
                                    success_msg = f" [C][00FF00]✅ SUCCESS! {result_msg}\n"
                                    await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                                else:
                                    error_msg = f" [C][FF0000]❌ ERROR! {result_msg}\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)


                        # Invite Command - /inv (creates 5-player group and sends request)
                        if inPuTMsG.strip().startswith('/inv '):
                            print('Processing invite command in any chat type')
                            
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 2:
                                error_msg = f" [C][FF0000]❌ ERROR! Usage: /inv (uid)\nExample: /inv 123456789\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                target_uid = parts[1]
                                initial_message = f" [C]{get_random_color()}\nCreating 5-Player Group and sending request to {target_uid}...\n"
                                await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                                
                                try:
                                    # Fast squad creation and invite for 5 players
                                    PAc = await OpEnSq(key, iv, region)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', PAc)
                                    await asyncio.sleep(0.3)
                                    
                                    C = await cHSq(5, int(target_uid), key, iv, region)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', C)
                                    await asyncio.sleep(0.3)
                                    
                                    V = await SEnd_InV(5, int(target_uid), key, iv, region)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', V)
                                    await asyncio.sleep(0.3)
                                    
                                    E = await ExiT(None, key, iv)
                                    await asyncio.sleep(2)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                                    
                                    # SUCCESS MESSAGE
                                    success_message = f" [C][00FF00]✅ SUCCESS! 5-Player Group invitation sent successfully to {target_uid}!\n"
                                    await safe_send_message(response.Data.chat_type, success_message, uid, chat_id, key, iv)
                                    
                                except Exception as e:
                                    error_msg = f" [C][FF0000]❌ ERROR sending invite: {str(e)}\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        if inPuTMsG.startswith(("/6")):
                            # Process /6 command - Create 4 player group
                            initial_message = f" [C]{get_random_color()}\n\nCreating 6-Player Group...\n\n"
                            await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                            
                            # Fast squad creation and invite for 4 players
                            PAc = await OpEnSq(key, iv, region)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', PAc)
                            
                            C = await cHSq(6, uid, key, iv, region)
                            await asyncio.sleep(0.3)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', C)
                            
                            V = await SEnd_InV(6, uid, key, iv, region)
                            await asyncio.sleep(0.3)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', V)
                            
                            E = await ExiT(None, key, iv)
                            await asyncio.sleep(3.5)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                            
                            # SUCCESS MESSAGE
                            success_message = f" [C][00FF00]✅ SUCCESS! 6-Player Group invitation sent successfully to {uid}!\n"
                            await safe_send_message(response.Data.chat_type, success_message, uid, chat_id, key, iv)

                        if inPuTMsG.startswith(("/3")):
                            # Process /3 command - Create 3 player group
                            initial_message = f" [C]{get_random_color()}\n\nCreating 3-Player Group...\n\n"
                            await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                            
                            # Fast squad creation and invite for 6 players
                            PAc = await OpEnSq(key, iv, region)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', PAc)
                            
                            C = await cHSq(3, uid, key, iv, region)
                            await asyncio.sleep(0.3)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', C)
                            
                            V = await SEnd_InV(3, uid, key, iv, region)
                            await asyncio.sleep(0.3)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', V)
                            
                            E = await ExiT(None, key, iv)
                            await asyncio.sleep(3.5)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                            
                            # SUCCESS MESSAGE
                            success_message = f" [C][00FF00]✅ SUCCESS! 6-Player Group invitation sent successfully to {uid}!\n"
                            await safe_send_message(response.Data.chat_type, success_message, uid, chat_id, key, iv)

                        if inPuTMsG.startswith(("/5")):
                            # Process /5 command in any chat type
                            initial_message = f" [C]{get_random_color()}\n\nSending Group Invitation...\n\n"
                            await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                            
                            # Fast squad creation and invite
                            PAc = await OpEnSq(key, iv, region)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', PAc)
                            
                            C = await cHSq(5, uid, key, iv, region)
                            await asyncio.sleep(0.3)  # Reduced delay
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', C)
                            
                            V = await SEnd_InV(5, uid, key, iv, region)
                            await asyncio.sleep(0.3)  # Reduced delay
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', V)
                            
                            E = await ExiT(None, key, iv)
                            await asyncio.sleep(3.5)  # Reduced from 3 seconds
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                            
                            # SUCCESS MESSAGE
                            success_message = f" [C][00FF00]✅ SUCCESS! Group invitation sent successfully to {uid}!\n"
                            await safe_send_message(response.Data.chat_type, success_message, uid, chat_id, key, iv)

                        if inPuTMsG.strip() == "/admin":
                            # Process /admin command in any chat type - مع اسم البوت المتغير
                            admin_message = f"""
[C] [FF0000]╔══════════╗
[FFFFFF]✨ folow on Instagram   
[FFFFFF]⚡ {BOT_DISPLAY_NAME}❤️  
[FFFFFF] thank for support 
[FF0000]╠══════════╣
[FFD700]⚡ OWNER : [FFFFFF]    {BOT_NAME}
[FFD700]✨ Name on instagram : [FFFFFF]{BOT_DISPLAY_NAME}  
[FF0000]╚══════════╝
[FFD700]✨ Developer —͟͞͞ </> {BOT_NAME}_bo  ⚡
"""
                            await safe_send_message(response.Data.chat_type, admin_message, uid, chat_id, key, iv)

                        # FIXED JOIN COMMAND
                        if inPuTMsG.startswith('/aim'):
                            # Process /join command in any chat type
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 2:
                                error_msg = f" [C][FF0000]❌ ERROR! Usage: /aim (team_code)\nExample: /aim ABC123\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                CodE = parts[1]
                                initial_message = f" [C]{get_random_color()}\nJoining squad with code: {CodE}...\n"
                                await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                                
                                try:
                                    # Try using the regular join method first
                                    EM = await GenJoinSquadsPacket(CodE, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', EM)
                                    
                                    # SUCCESS MESSAGE
                                    success_message = f" [C][00FF00]✅ SUCCESS! aim squad with code: {CodE}!\n"
                                    await safe_send_message(response.Data.chat_type, success_message, uid, chat_id, key, iv)
                                    
                                except Exception as e:
                                    print(f"Regular aim failed, trying ghost aim: {e}")
                                    # If regular join fails, try ghost join
                                    try:
                                        # Get bot's UID from global context or login data
                                        bot_uid = LoGinDaTaUncRypTinG.AccountUID if hasattr(LoGinDaTaUncRypTinG, 'AccountUID') else TarGeT
                                        
                                        ghost_packet = await ghost_join_packet(bot_uid, CodE, key, iv)
                                        if ghost_packet:
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', ghost_packet)
                                            success_message = f" [C][00FF00]✅ SUCCESS! Ghost joining squad with code: {CodE}!\n"
                                            await safe_send_message(response.Data.chat_type, success_message, uid, chat_id, key, iv)
                                        else:
                                            error_msg = f" [C][FF0000]❌ ERROR! Failed to create ghost join packet.\n"
                                            await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                            
                                    except Exception as ghost_error:
                                        print(f"Ghost join also failed: {ghost_error}")
                                        error_msg = f" [C][FF0000]❌ ERROR! Failed to join squad: {str(ghost_error)}\n"
                                        await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)



                        if inPuTMsG.startswith('/leave'):
                            # Process /exit command in any chat type
                            initial_message = f" [C]{get_random_color()}\nLeaving current squad...\n"
                            await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                            
                            leave = await ExiT(uid,key,iv)
                            await SEndPacKeT(whisper_writer , online_writer , 'OnLine' , leave)
                            
                            # SUCCESS MESSAGE
                            success_message = f" [C][00FF00]✅ SUCCESS! Left the squad successfully!\n"
                            await safe_send_message(response.Data.chat_type, success_message, uid, chat_id, key, iv)

                        if inPuTMsG.strip().startswith('fuck'):
                            # Process /s command in any chat type
                            initial_message = f" [C]{get_random_color()}\nStarting match...\n"
                            await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                            
                            EM = await FS(key , iv)
                            await SEndPacKeT(whisper_writer , online_writer , 'OnLine' , EM)
                            
                            # SUCCESS MESSAGE
                            success_message = f" [C][00FF00]✅ SUCCESS! Match starting command sent!\n"
                            await safe_send_message(response.Data.chat_type, success_message, uid, chat_id, key, iv)

                        # NEW GENERAL EMOTE COMMAND - /c
                        if inPuTMsG.strip().startswith('/c '):
                            print('Processing general emote command in any chat type')
                            
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 3:
                                error_msg = f" [C][FF0000]❌ ERROR! Usage: /c uid1 [uid2] [uid3] [uid4] number(1-{len(GENERAL_EMOTES_MAP)})\nExample: /c 123456789 1\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                # Parse uids and number
                                uids = []
                                number = None
                                
                                for part in parts[1:]:
                                    if part.isdigit():
                                        if len(part) <= 3:  # Number should be 1-409 (1-3 digits)
                                            number = part
                                        else:
                                            uids.append(part)
                                    else:
                                        break
                                
                                if not number and parts[-1].isdigit() and len(parts[-1]) <= 3:
                                    number = parts[-1]
                                
                                if not uids or not number:
                                    error_msg = f" [C][FF0000]❌ ERROR! Invalid format! Usage: /c uid1 [uid2] [uid3] [uid4] number(1-{len(GENERAL_EMOTES_MAP)})\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                else:
                                    try:
                                        number_str = str(number)
                                        if number_str not in GENERAL_EMOTES_MAP:
                                            error_msg = f" [C][FF0000]❌ ERROR! Number must be between 1-{len(GENERAL_EMOTES_MAP)} only!\n"
                                            await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                        else:
                                            initial_message = f" [C]{get_random_color()}\nSending emote {number_str}...\n"
                                            await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                                            
                                            success, result_msg = await general_emote_spam(uids, number_str, key, iv, region)
                                            
                                            if success:
                                                emote_id = GENERAL_EMOTES_MAP[number_str]
                                                success_msg = f" [C][00FF00]✅ SUCCESS! {result_msg}\n"
                                                await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                                            else:
                                                error_msg = f" [C][FF0000]❌ ERROR! {result_msg}\n"
                                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                            
                                    except ValueError:
                                        error_msg = f" [C][FF0000]❌ ERROR! Invalid number format! Use 1-{len(GENERAL_EMOTES_MAP)} only.\n"
                                        await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        # Emote command - works in all chat types
                        if inPuTMsG.strip().startswith('/em'):
                            print(f'Processing emote command in chat type: {response.Data.chat_type}')
                            
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 3:
                                error_msg = f" [C][FF0000]❌ ERROR! Usage: /e (uid) (emote_id)\nExample: /e 123456789 909000001\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                continue
                                
                            initial_message = f' [C]{get_random_color()}\nSending emote to target...\n'
                            await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)

                            uid2 = uid3 = uid4 = uid5 = None
                            s = False
                            target_uids = []

                            try:
                                target_uid = int(parts[1])
                                target_uids.append(target_uid)
                                uid2 = int(parts[2]) if len(parts) > 2 else None
                                if uid2: target_uids.append(uid2)
                                uid3 = int(parts[3]) if len(parts) > 3 else None
                                if uid3: target_uids.append(uid3)
                                uid4 = int(parts[4]) if len(parts) > 4 else None
                                if uid4: target_uids.append(uid4)
                                uid5 = int(parts[5]) if len(parts) > 5 else None
                                if uid5: target_uids.append(uid5)
                                idT = int(parts[-1])  # Last part is emote ID

                            except ValueError as ve:
                                print("ValueError:", ve)
                                s = True
                            except Exception as e:
                                print(f"Error parsing emote command: {e}")
                                s = True

                            if not s:
                                try:
                                    for target in target_uids:
                                        H = await Emote_k(target, idT, key, iv, region)
                                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                        await asyncio.sleep(0.1)
                                    
                                    # SUCCESS MESSAGE
                                    success_msg = f" [C][00FF00]✅ SUCCESS! Emote {idT} sent to {len(target_uids)} player(s)!\nTargets: {', '.join(map(str, target_uids))}\n"
                                    await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)

                                except Exception as e:
                                    error_msg = f" [C][FF0000]❌ ERROR sending emote: {str(e)}\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                error_msg = f" [C][FF0000]❌ ERROR! Invalid UID format. Usage: /e (uid) (emote_id)\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        # Fast emote spam command - works in all chat types
                        if inPuTMsG.strip().startswith('/fast'):
                            print('Processing fast emote spam in any chat type')
                            
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 3:
                                error_msg = f" [C][FF0000]❌ ERROR! Usage: /fast uid1 [uid2] [uid3] [uid4] emoteid\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                # Parse uids and emoteid
                                uids = []
                                emote_id = None
                                
                                for part in parts[1:]:
                                    if part.isdigit():
                                        if len(part) > 3:  # Assuming UIDs are longer than 3 digits
                                            uids.append(part)
                                        else:
                                            emote_id = part
                                    else:
                                        break
                                
                                if not emote_id and parts[-1].isdigit():
                                    emote_id = parts[-1]
                                
                                if not uids or not emote_id:
                                    error_msg = f" [C][FF0000]❌ ERROR! Invalid format! Usage: /fast uid1 [uid2] [uid3] [uid4] emoteid\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                else:
                                    # Stop any existing fast spam
                                    if fast_spam_task and not fast_spam_task.done():
                                        fast_spam_running = False
                                        fast_spam_task.cancel()
                                    
                                    # Start new fast spam
                                    fast_spam_running = True
                                    fast_spam_task = asyncio.create_task(fast_emote_spam(uids, emote_id, key, iv, region))
                                    
                                    # SUCCESS MESSAGE
                                    success_msg = f" [C][00FF00]✅ SUCCESS! Fast emote spam started!\nTargets: {len(uids)} players\nEmote: {emote_id}\nSpam count: 25 times\n"
                                    await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)

                        # Custom emote spam command - works in all chat types
                        if inPuTMsG.strip().startswith('/p'):
                            print('Processing custom emote spam in any chat type')
                            
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 4:
                                error_msg = f" [C][FF0000]❌ ERROR! Usage: /p (uid) (emote_id) (times)\nExample: /p 123456789 909000001 10\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                try:
                                    target_uid = parts[1]
                                    emote_id = parts[2]
                                    times = int(parts[3])
                                    
                                    if times <= 0:
                                        error_msg = f" [C][FF0000]❌ ERROR! Times must be greater than 0!\n"
                                        await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                    elif times > 100:
                                        error_msg = f" [C][FF0000]❌ ERROR! Maximum 100 times allowed for safety!\n"
                                        await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                    else:
                                        # Stop any existing custom spam
                                        if custom_spam_task and not custom_spam_task.done():
                                            custom_spam_running = False
                                            custom_spam_task.cancel()
                                            await asyncio.sleep(0.5)
                                        
                                        # Start new custom spam
                                        custom_spam_running = True
                                        custom_spam_task = asyncio.create_task(custom_emote_spam(target_uid, emote_id, times, key, iv, region))
                                        
                                        # SUCCESS MESSAGE
                                        success_msg = f" [C][00FF00]✅ SUCCESS! Custom emote spam started!\nTarget: {target_uid}\nEmote: {emote_id}\nTimes: {times}\n"
                                        await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                                        
                                except ValueError:
                                    error_msg = f" [C][FF0000]❌ ERROR! Invalid number format! Usage: /p (uid) (emote_id) (times)\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                except Exception as e:
                                    error_msg = f" [C][FF0000]❌ ERROR! {str(e)}\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        # FIXED Spam request command - works in all chat types
                     # NEW SPROM COMMAND - START ROOM SPAM
                        if inPuTMsG.strip().startswith('/sprom '):
                            print('Processing sprom command in any chat type')
                            
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 2:
                                error_msg = f" [C][FF0000]❌ ERROR! Usage: /sprom (uid) [duration]\nExample: /sprom 123456789 60\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                try:
                                    target_id = parts[1]
                                    duration = parts[2] if len(parts) > 2 else "60"  # Default 60 seconds
                                    
                                    initial_message = f" [C]{get_random_color()}\n🚀 بدء سبام الروم...\nالهدف: {target_id}\nالمدة: {duration} ثانية\n"
                                    await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                                    
                                    # بناء URL للـ API
                                    url = f"https://sargo44.onrender.com/spam?user_id={target_id}&duration={duration}"
                                    
                                    # تشغيل الطلب في الخلفية باستخدام threading
                                    def send_spam_request():
                                        try:
                                            response = requests.get(url, timeout=10)
                                            print(f"Spam API response: {response.status_code}")
                                            if response.status_code == 200:
                                                print(f"✅ Room spam started successfully for {target_id}")
                                            else:
                                                print(f"❌ Failed to start spam: {response.status_code}")
                                        except Exception as e:
                                            print(f"Error calling spam API: {e}")
                                    
                                    # بدء السبام في thread منفصل
                                    spam_thread = threading.Thread(target=send_spam_request)
                                    spam_thread.daemon = True
                                    spam_thread.start()
                                    
                                    success_msg = f" [C][00FF00]✅ تم بدء سبام الروم بنجاح!\n🎯 الهدف: {target_id}\n⏱️ المدة: {duration} ثانية\n"
                                    await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                                    
                                except Exception as e:
                                    error_msg = f" [C][FF0000]❌ ERROR! {str(e)}\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        # NEW STROM COMMAND - STOP ROOM SPAM
                        if inPuTMsG.strip().startswith('/strom '):
                            print('Processing strom command in any chat type')
                            
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 2:
                                error_msg = f" [C][FF0000]❌ ERROR! Usage: /strom (uid)\nExample: /strom 123456789\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                try:
                                    target_id = parts[1]
                                    
                                    initial_message = f" [C]{get_random_color()}\n🛑 إيقاف سبام الروم...\nالهدف: {target_id}\n"
                                    await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                                    
                                    # بناء URL للـ API
                                    url = f"https://sargo44.onrender.com/stop?user_id={target_id}"
                                    
                                    # تشغيل الطلب في الخلفية باستخدام threading
                                    def stop_spam_request():
                                        try:
                                            response = requests.get(url, timeout=10)
                                            print(f"Stop spam API response: {response.status_code}")
                                            if response.status_code == 200:
                                                print(f"✅ Room spam stopped successfully for {target_id}")
                                            else:
                                                print(f"❌ Failed to stop spam: {response.status_code}")
                                        except Exception as e:
                                            print(f"Error calling stop spam API: {e}")
                                    
                                    # إيقاف السبام في thread منفصل
                                    stop_thread = threading.Thread(target=stop_spam_request)
                                    stop_thread.daemon = True
                                    stop_thread.start()
                                    
                                    success_msg = f" [C][00FF00]✅ تم إيقاف سبام الروم بنجاح!\n🎯 الهدف: {target_id}\n"
                                    await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                                    
                                except Exception as e:
                                    error_msg = f" [C][FF0000]❌ ERROR! {str(e)}\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        # NEW EVO COMMANDS
                        if inPuTMsG.strip().startswith('/evo '):
                            print('Processing evo command in any chat type')
                            
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 2:
                                error_msg = f" [C][FF0000]❌ ERROR! Usage: /evo uid1 [uid2] [uid3] [uid4] number(1-21)\nExample: /evo 123456789 1\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                # Parse uids and number
                                uids = []
                                number = None
                                
                                for part in parts[1:]:
                                    if part.isdigit():
                                        if len(part) <= 2:  # Number should be 1-21 (1 or 2 digits)
                                            number = part
                                        else:
                                            uids.append(part)
                                    else:
                                        break
                                
                                if not number and parts[-1].isdigit() and len(parts[-1]) <= 2:
                                    number = parts[-1]
                                
                                if not uids or not number:
                                    error_msg = f" [C][FF0000]❌ ERROR! Invalid format! Usage: /evo uid1 [uid2] [uid3] [uid4] number(1-21)\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                else:
                                    try:
                                        number_int = int(number)
                                        if number_int not in EMOTE_MAP:
                                            error_msg = f" [C][FF0000]❌ ERROR! Number must be between 1-21 only!\n"
                                            await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                        else:
                                            initial_message = f" [C]{get_random_color()}\nSending evolution emote {number_int}...\n"
                                            await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                                            
                                            success, result_msg = await evo_emote_spam(uids, number_int, key, iv, region)
                                            
                                            if success:
                                                success_msg = f" [C][00FF00]✅ SUCCESS! {result_msg}\n"
                                                await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                                            else:
                                                error_msg = f" [C][FF0000]❌ ERROR! {result_msg}\n"
                                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                            
                                    except ValueError:
                                        error_msg = f" [C][FF0000]❌ ERROR! Invalid number format! Use 1-21 only.\n"
                                        await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        if inPuTMsG.strip().startswith('/fe '):
                            print('Processing fe command in any chat type')
                            
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 2:
                                error_msg = f" [C][FF0000]❌ ERROR! Usage: /fe uid1 [uid2] [uid3] [uid4] number(1-21)\nExample: /fe 123456789 1\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                # Parse uids and number
                                uids = []
                                number = None
                                
                                for part in parts[1:]:
                                    if part.isdigit():
                                        if len(part) <= 2:  # Number should be 1-21 (1 or 2 digits)
                                            number = part
                                        else:
                                            uids.append(part)
                                    else:
                                        break
                                
                                if not number and parts[-1].isdigit() and len(parts[-1]) <= 2:
                                    number = parts[-1]
                                
                                if not uids or not number:
                                    error_msg = f" [C][FF0000]❌ ERROR! Invalid format! Usage: /fe uid1 [uid2] [uid3] [uid4] number(1-21)\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                else:
                                    try:
                                        number_int = int(number)
                                        if number_int not in EMOTE_MAP:
                                            error_msg = f" [C][FF0000]❌ ERROR! Number must be between 1-21 only!\n"
                                            await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                        else:
                                            # Stop any existing evo_fast spam
                                            if evo_fast_spam_task and not evo_fast_spam_task.done():
                                                evo_fast_spam_running = False
                                                evo_fast_spam_task.cancel()
                                                await asyncio.sleep(0.5)
                                            
                                            # Start new evo_fast spam
                                            evo_fast_spam_running = True
                                            evo_fast_spam_task = asyncio.create_task(evo_fast_emote_spam(uids, number_int, key, iv, region))
                                            
                                            # SUCCESS MESSAGE
                                            emote_id = EMOTE_MAP[number_int]
                                            success_msg = f" [C][00FF00]✅ SUCCESS! Fast evolution emote spam started!\nTargets: {len(uids)} players\nEmote: {number_int} (ID: {emote_id})\nSpam count: 25 times\nInterval: 0.1 seconds\n"
                                            await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                                            
                                    except ValueError:
                                        error_msg = f" [C][FF0000]❌ ERROR! Invalid number format! Use 1-21 only.\n"
                                        await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        # NEW EVO_CUSTOM COMMAND
                        if inPuTMsG.strip().startswith('/evo_c '):
                            print('Processing evo_c command in any chat type')
                            
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 3:
                                error_msg = f" [C][FF0000]❌ ERROR! Usage: /evo_c uid1 [uid2] [uid3] [uid4] number(1-21) time(1-100)\nExample: /evo_c 123456789 1 10\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                # Parse uids, number, and time
                                uids = []
                                number = None
                                time_val = None
                                
                                for part in parts[1:]:
                                    if part.isdigit():
                                        if len(part) <= 2:  # Number or time should be 1-100 (1, 2, or 3 digits)
                                            if number is None:
                                                number = part
                                            elif time_val is None:
                                                time_val = part
                                            else:
                                                uids.append(part)
                                        else:
                                            uids.append(part)
                                    else:
                                        break
                                
                                # If we still don't have time_val, try to get it from the last part
                                if not time_val and len(parts) >= 3:
                                    last_part = parts[-1]
                                    if last_part.isdigit() and len(last_part) <= 3:
                                        time_val = last_part
                                        # Remove time_val from uids if it was added by mistake
                                        if time_val in uids:
                                            uids.remove(time_val)
                                
                                if not uids or not number or not time_val:
                                    error_msg = f" [C][FF0000]❌ ERROR! Invalid format! Usage: /evo_c uid1 [uid2] [uid3] [uid4] number(1-21) time(1-100)\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                else:
                                    try:
                                        number_int = int(number)
                                        time_int = int(time_val)
                                        
                                        if number_int not in EMOTE_MAP:
                                            error_msg = f" [C][FF0000]❌ ERROR! Number must be between 1-21 only!\n"
                                            await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                        elif time_int < 1 or time_int > 100:
                                            error_msg = f" [C][FF0000]❌ ERROR! Time must be between 1-100 only!\n"
                                            await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                        else:
                                            # Stop any existing evo_custom spam
                                            if evo_custom_spam_task and not evo_custom_spam_task.done():
                                                evo_custom_spam_running = False
                                                evo_custom_spam_task.cancel()
                                                await asyncio.sleep(0.5)
                                            
                                            # Start new evo_custom spam
                                            evo_custom_spam_running = True
                                            evo_custom_spam_task = asyncio.create_task(evo_custom_emote_spam(uids, number_int, time_int, key, iv, region))
                                            
                                            # SUCCESS MESSAGE
                                            emote_id = EMOTE_MAP[number_int]
                                            success_msg = f" [C][00FF00]✅ SUCCESS! Custom evolution emote spam started!\nTargets: {len(uids)} players\nEmote: {number_int} (ID: {emote_id})\nRepeat: {time_int} times\nInterval: 0.1 seconds\n"
                                            await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                                            
                                    except ValueError:
                                        error_msg = f" [C][FF0000]❌ ERROR! Invalid number/time format! Use numbers only.\n"
                                        await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        # NEW RANDOM EVO EMOTES COMMAND - 2.5 SECONDS DELAY
                        if inPuTMsG.strip() == '/rnd':
                            print('Processing random evolution emotes command in any chat type')
                            
                            try:
                                total_time = 21 * 2.5  # 21 emotes × 2.5 seconds
                                initial_message = f" [C]{get_random_color()}BoT Will Not Repond Until {total_time} Second\n"
                                await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                                
                                success, result_msg = await random_evo_emote_spam_sender(key, iv, region)
                                
                                if success:
                                    success_msg = f" [C][00FF00]✅ SUCCESS! {result_msg}\n"
                                    await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                                else:
                                    error_msg = f" [C][FF0000]❌ ERROR! {result_msg}\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                    
                            except Exception as e:
                                error_msg = f" [C][FF0000]❌ ERROR! {str(e)}\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        # NEW: Manual group update command
                        if inPuTMsG.strip() == '/update_group':
                            try:
                                # Try to get group members from current squad data
                                # This is a fallback if automatic detection doesn't work
                                initial_message = f" [C]{get_random_color()}\nUpdating group members list...\n"
                                await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                                
                                # Add current command sender to group members
                                if uid not in current_group_members:
                                    current_group_members.append(uid)
                                    
                                success_msg = f" [C][00FF00]✅ Group members updated! Current count: {len(current_group_members)}\nMembers: {', '.join(map(str, current_group_members))}\n"
                                await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                                
                            except Exception as e:
                                error_msg = f" [C][FF0000]❌ ERROR updating group: {str(e)}\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        # Stop evo_fast spam command
                        if inPuTMsG.strip() == '/sfe':
                            if evo_fast_spam_task and not evo_fast_spam_task.done():
                                evo_fast_spam_running = False
                                evo_fast_spam_task.cancel()
                                success_msg = f" [C][00FF00]✅ SUCCESS! Evolution fast spam stopped successfully!\n"
                                await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                            else:
                                error_msg = f" [C][FF0000]❌ ERROR! No active evolution fast spam to stop!\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        # Stop evo_custom spam command
                        if inPuTMsG.strip() == '/stop evo_c':
                            if evo_custom_spam_task and not evo_custom_spam_task.done():
                                evo_custom_spam_running = False
                                evo_custom_spam_task.cancel()
                                success_msg = f" [C][00FF00]✅ SUCCESS! Evolution custom spam stopped successfully!\n"
                                await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                            else:
                                error_msg = f" [C][FF0000]❌ ERROR! No active evolution custom spam to stop!\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        # FIXED HELP MENU SYSTEM - Now with updated dance command
                        if inPuTMsG.strip().lower() in ("op", "/nm", "hi", "/help"):
                            print(f"Help command detected from UID: {uid} in chat type: {response.Data.chat_type}")
                            
                            # Menu 1 - Basic Commands - مع اسم البوت المتغير
                            menu1 = f'''[b][c][00FFFF]╔══════════╗
                            
[FFFFFF] ✨مرحبا بيك في بوت {BOT_NAME}

[FFFFFF] ✨جلب اي لاعب الى الفريق
[00FFFF] /inv [uid]

[FFFFFF]╠══════════╣
[00FFFF] ✨انشاء فريق متكون من خمس اشخاص  :
[FFFFFF] /3 , /5 , /6 

[00FFFF] لي معرفة الادمن
[FFFFFF]/admin

[00FFFF]╚══════════╝
[FFFFFF] ✨NoTmeowl Panel'''
                            
                            await safe_send_message(response.Data.chat_type, menu1, uid, chat_id, key, iv)
                            
                            await asyncio.sleep(0.5)
                            
                            # Menu 2 - Advanced Commands - مع اسم البوت
                            menu2 = f'''[b][c][FF0000]╔══════════╗
                            
[00FFFF] /aim [team-code]

[FFD700] ✨لعمل اي رقصة
[FFFFFF]  /evo [uid] [1-21]

[FFD700] ✨تسريع الرقصة
[FFFFFF]  /fe [uid] [1-21]

[00FFFF]✨رقصات عشوائيه
[FFFFFF]/rnd

[FF0000]╠══════════╣

[FFD700] ✨مغادرة البوت من السكواد
[FFFFFF]  /leave

[FF0000]╚══════════╝'''
                            
                            await safe_send_message(response.Data.chat_type, menu2, uid, chat_id, key, iv)
                            
                            await asyncio.sleep(0.5)
                            
                            # Menu 3 - Emote Commands - مع الاسم المعروض
                            menu3 = f'''[b][c][FF0000]╔══════════╗
[f70505] ✨سبام اللاعب 

[f70505]لي عمل سبام VIP 
[FFFFFF] ⚡/sprom

[f70505] لي إيقاف سبام VIP 
[FFFFFF] ⚡/strom

[FF0000]╠══════════╣
[
[FF0000]╚══════════╝
[f70505] ✨ {BOT_DISPLAY_NAME} ❤️⚡
'''
                            
                            await safe_send_message(response.Data.chat_type, menu3, uid, chat_id, key, iv)


                        # BOT STATUS COMMAND - مع الأسماء المتغيرة
                        elif inPuTMsG.strip().lower() in ("status", "/status", "info", "/info", "bot", "/bot"):
                            bot_status = f"""
 [C][00FF00]🤖 BOT {BOT_NAME}

[FFFFFF]🤖 Bot Name: [00FF00]{LoGinDaTaUncRypTinG.AccountName if hasattr(LoGinDaTaUncRypTinG, 'AccountName') else BOT_NAME}
[FFFFFF]🆔 Bot UID: [00FF00]{TarGeT}
[FFFFFF]🌍 Region: [00FF00]{region}
[FFFFFF]⚡ Status: [00FF00]ONLINE & WORKING
[FFFFFF]📊 Connection: [00FF00]STABLE
[FFFFFF]🎮 Features: [00FF00]ALL ACTIVE
[FFFFFF]😎 Emotes Available: [00FF00]{len(GENERAL_EMOTES_MAP)} emotes

[C] [FFB300]👑 Developed {BOT_DISPLAY_NAME}   
[00FF00]━━━━━━━━━━━━"""
                            
                            await safe_send_message(response.Data.chat_type, bot_status, uid, chat_id, key, iv)
                        response = None
                            
            whisper_writer.close() ; await whisper_writer.wait_closed() ; whisper_writer = None
                    
                    	
                    	
        except Exception as e: print(f"ErroR {ip}:{port} - {e}") ; whisper_writer = None
        await asyncio.sleep(reconnect_delay)

async def MaiiiinE():
    global bot_uid, BOT_NAME, BOT_DISPLAY_NAME, CURRENT_UID, CURRENT_PW
    
    # ========== تحميل الإعدادات من ملف JSON ==========
    config = load_config()
    if not config:
        print("[ERROR] فشل تحميل ملف الإعدادات! تأكد من وجود config.json")
        return None
    
    Uid = config['account']['uid']
    Pw = config['account']['password']
    
    # تحديث المتغيرات العامة
    CURRENT_UID = Uid
    CURRENT_PW = Pw
    update_bot_names_from_config(config)
    # ================================================

    open_id , access_token = await GeNeRaTeAccEss(Uid , Pw)
    if not open_id or not access_token: print("ErroR - InvaLid AccounT") ; return None
    
    PyL = await EncRypTMajoRLoGin(open_id , access_token)
    MajoRLoGinResPonsE = await MajorLogin(PyL)
    if not MajoRLoGinResPonsE: print("TarGeT AccounT => BannEd / NoT ReGisTeReD ! ") ; return None
    
    MajoRLoGinauTh = await DecRypTMajoRLoGin(MajoRLoGinResPonsE)
    UrL = MajoRLoGinauTh.url
    print(UrL)
    region = MajoRLoGinauTh.region

    ToKen = MajoRLoGinauTh.token
    TarGeT = MajoRLoGinauTh.account_uid
    bot_uid = TarGeT  # ADD THIS - Store bot UID globally
    key = MajoRLoGinauTh.key
    iv = MajoRLoGinauTh.iv
    timestamp = MajoRLoGinauTh.timestamp
    
    LoGinDaTa = await GetLoginData(UrL , PyL , ToKen)
    if not LoGinDaTa: print("ErroR - GeTinG PorTs From LoGin DaTa !") ; return None
    LoGinDaTaUncRypTinG = await DecRypTLoGinDaTa(LoGinDaTa)
    OnLinePorTs = LoGinDaTaUncRypTinG.Online_IP_Port
    ChaTPorTs = LoGinDaTaUncRypTinG.AccountIP_Port
    OnLineiP , OnLineporT = OnLinePorTs.split(":")
    ChaTiP , ChaTporT = ChaTPorTs.split(":")
    acc_name = LoGinDaTaUncRypTinG.AccountName
    #print(acc_name)
    print(ToKen)
    try:
        equie_emote(ToKen,UrL)
    except:
        pass
    AutHToKen = await xAuThSTarTuP(int(TarGeT) , ToKen , int(timestamp) , key , iv)
    ready_event = asyncio.Event()
    
    task1 = asyncio.create_task(TcPChaT(ChaTiP, ChaTporT , AutHToKen , key , iv , LoGinDaTaUncRypTinG , ready_event ,region))
     
    await ready_event.wait()
    await asyncio.sleep(1)
    task2 = asyncio.create_task(TcPOnLine(OnLineiP , OnLineporT , key , iv , AutHToKen))
    os.system('clear' if os.name == 'posix' else 'cls')
    try:
        print(render('himo rihab', colors=['white', 'green'], align='center'))
    except:
        print("=== HIMO RIHAB BOT ===")
    print('')
    print(f" - Bot online ID: {TarGeT} | Bot name: {acc_name}")
    print(f" - Bot is ready! (Config file: {BOT_NAME} / {BOT_DISPLAY_NAME})")   
    print(f" - Monitoring config.json for changes...")    
    await asyncio.gather(task1 , task2)
    
async def StarTinG():
    # بدء مراقبة ملف الإعدادات
    monitor_task = asyncio.create_task(config_monitor())
    
    while True:
        try: await asyncio.wait_for(MaiiiinE() , timeout = 7 * 60 * 60)
        except asyncio.TimeoutError: print("Token ExpiRed ! , ResTartinG")
        except Exception as e: print(f"ErroR TcP - {e} => ResTarTinG ...")

if __name__ == '__main__':
    asyncio.run(StarTinG())