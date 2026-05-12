import importlib
import sys

required_modules = [
    'requests', 'os', 'psutil', 'sys', 'jwt', 'pickle', 'json', 
    'binascii', 'time', 'urllib3', 'base64', 'datetime', 're', 
    'socket', 'threading', 'ssl', 'pytz', 'aiohttp', 'protobuf_decoder',
    'google.protobuf.timestamp_pb2', 'concurrent.futures',
    'Crypto.Cipher', 'Crypto.Util.Padding', 'cfonts',
    'asyncio', 'random'
]

for module in required_modules:
    try:
        importlib.import_module(module)
        print(f"✓ {module}")
    except ImportError as e:
        print(f"✗ {module}: {e}")