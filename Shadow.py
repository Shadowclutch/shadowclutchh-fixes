import os
import shutil
import urllib.request
import tempfile
import sys
import json
from zipfile import ZipFile

# Third-party library checks
try:
    import py7zr
    import rarfile
except ImportError:
    print("\n[!] Missing required libraries.")
    print("Please run this command in your terminal first:")
    print("pip install py7zr rarfile\n")
    input("Press Enter to exit...")
    sys.exit(1)

# =========================================================================
# LIVE SHADOWCLUTCHH CLOUD DATABASE LINK
# =========================================================================
DATABASE_URL = "https://raw.githubusercontent.com/Shadowclutch/shadowclutchh-fixes/main/database.json"

def load_remote_database():
    try:
        req = urllib.request.Request(DATABASE_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"[!] Failed to fetch latest game database from server: {e}")
        return {}

def install_game_fix(app_id, game_directory, game_map):
    if app_id not in game_map:
        print(f"\n[Error] App ID {app_id} is not registered in the database mapping.")
        return False
        
    game_data = game_map[app_id]
    game_name = game_data["name"]
    download_url = game_data["url"]
    
    # Automatically read the extension type (.zip, .7z, or .rar) from the URL link
    file_extension = os.path.splitext(download_url.split('?')[0])[1]
    
    temp_dir = tempfile.gettempdir()
    archive_path = os.path.join(temp_dir, f"download{file_extension}")
    extract_path = os.path.join(temp_dir, f"extract_temp")

    if not os.path.exists(game_directory):
        print(f"\n[Error] Target directory does not exist:\n{game_directory}")
        return False

    try:
        print(f"\n[*] Match Found: {game_name}")
        print(f"[*] Downloading file cleanly from your repository cloud storage...")
        
        req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(archive_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        os.makedirs(extract_path, exist_ok=True)

        print(f"[*] Extracting archive contents...")
        if file_extension.lower() == ".zip":
            with ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
        elif file_extension.lower() == ".7z":
            with py7zr.SevenZipFile(archive_path, mode='r') as sz_ref:
                sz_ref.extractall(extract_path)
        elif file_extension.lower() == ".rar":
            with rarfile.RarFile(archive_path) as rar_ref:
                rar_ref.extractall(extract_path)

        # -----------------------------------------------------------------
        # NESTED FOLDER DETECTION ENGINE
        # -----------------------------------------------------------------
        # Check if the archive contains exactly one item and that item is a folder
        top_level_items = os.listdir(extract_path)
        if len(top_level_items) == 1 and os.path.isdir(os.path.join(extract_path, top_level_items[0])):
            print(f"[*] Nested folder detected: '{top_level_items[0]}'. Bypassing it...")
            source_folder = os.path.join(extract_path, top_level_items[0])
        else:
            source_folder = extract_path

        # -----------------------------------------------------------------
        # DEPLOYMENT PIPELINE
        # -----------------------------------------------------------------
        print(f"[*] Copying items directly into game folder...")
        for item in os.listdir(source_folder):
            source_item = os.path.join(source_folder, item)
            destination_item = os.path.join(game_directory, item)
            
            if os.path.isdir(source_item):
                if os.path.exists(destination_item):
                    shutil.rmtree(destination_item)
                shutil.copytree(source_item, destination_item)
            else:
                if os.path.exists(destination_item):
                    os.remove(destination_item)
                shutil.copy2(source_item, destination_item)

        print("\n[+] Process completed successfully with zero ad-walls!")
        return True

    except Exception as e:
        print(f"\n[!] An error occurred during deployment: {e}")
        return False
        
    finally:
        if os.path.exists(archive_path):
            os.remove(archive_path)
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)

if __name__ == "__main__":
    print("=" * 55)
    print("      SHADOWCLUTCHH GAME FIX AUTO-INSTALLER          ")
    print("=" * 55)

    print("[*] Syncing live server allocations...")
    live_map = load_remote_database()
    
    if not live_map:
        print("[!] Could not connect to remote repository database.")
        input("\nPress Enter to exit...")
        sys.exit(1)

    # 1. Get Game App ID
    user_app_id = input("\nEnter the Game App ID: ").strip()
    while not user_app_id:
        user_app_id = input("App ID cannot be empty: ").strip()

    # 2. Get Game Directory Path
    print("\nEnter the absolute path to the game folder.")
    print("Example: C:\\Program Files (x86)\\Steam\\steamapps\\common\\Grand Theft Auto V")
    user_dir = input("Path: ").strip().strip('"')

    while not os.path.exists(user_dir):
        print("\n[!] That folder path does not exist. Please check it and try again.")
        print("Example: C:\\Program Files (x86)\\Steam\\steamapps\\common\\Grand Theft Auto V")
        user_dir = input("Path: ").strip().strip('"')

    # 3. Run direct script pipeline execution
    install_game_fix(user_app_id, user_dir, live_map)
    
    print("\n" + "=" * 55)
    input("Press Enter to close this window...")
