import subprocess
import sys

def install_packages():
    packages = [
        'requests==2.31.0',
        'httpx==0.25.2',
        'google==3.0.0',
        'protobuf==4.25.1',
        'pycryptodome==3.19.0',
        'psutil==5.9.6',
        'PyJWT==2.8.0',
        'urllib3==2.0.7',
        'aiohttp==3.9.1',
        'cfonts==1.5.0'
    ]
    
    print("Installing required packages...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed: {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
    
    print("\nInstallation complete!")

if __name__ == "__main__":
    install_packages()