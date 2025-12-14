import requests
import os
import re
import time

def get_full_sequence():
    full_ids = []
    # 01 to 99
    for i in range(1, 100):
        full_ids.append(f"{i:02d}")
    # A0 to Z9
    for char_code in range(65, 91): 
        char = chr(char_code)
        for num in range(0, 10):
            full_ids.append(f"{char}{num}")
    return full_ids

print("-" * 50)
print(" VNR VJIET HALL TICKET DOWNLOADER ")
print("-" * 50)

# 1. Get Inputs
prefix_input = input("Enter Prefix (e.g., 23071A): ").strip().upper()
branch_code = input("Enter Branch Code (e.g., 66): ").strip()

print("Enter the suffixes (e.g., 01, 99, A0, K6)")
start_input = input("Start Number (e.g., 01): ").strip().upper()
end_input   = input("End Number   (e.g., K6): ").strip().upper()

# 2. Logic to build the list
if start_input.isdigit(): start_input = start_input.zfill(2)
if end_input.isdigit():   end_input = end_input.zfill(2)

master_sequence = get_full_sequence()

if start_input not in master_sequence or end_input not in master_sequence:
    print("❌ Error: Invalid start or end number format.")
    exit()

start_index = master_sequence.index(start_input)
end_index = master_sequence.index(end_input)

if start_index > end_index:
    print("❌ Error: Start number cannot be after End number.")
    exit()

target_suffixes = master_sequence[start_index : end_index + 1]

# 3. Create a Specific Folder for this Batch
# Example: hall_downloads/23071A_66
base_dir = os.path.join(os.getcwd(), "hall_downloads")
batch_folder_name = f"{prefix_input}_{branch_code}"
full_save_path = os.path.join(base_dir, batch_folder_name)

os.makedirs(full_save_path, exist_ok=True)

print(f"\n📋 Prepared {len(target_suffixes)} roll numbers.")
print(f"📂 Saving to folder: {batch_folder_name}")

confirm = input("\nType 'y' to start downloading: ").lower()
if confirm != 'y':
    print("Cancelled.")
    exit()

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 4. Download Loop
for suffix in target_suffixes:
    # Construct Roll Number
    roll_no = f"{prefix_input}{branch_code}{suffix}"
    
    try:
        list_url = f"https://vnrvjietexams.net/EduPrime3Exam/HallTicket/GetList?id={roll_no}"
        time.sleep(0.5) 
        
        list_response = session.get(list_url, headers=headers)
        
        if list_response.status_code != 200:
            print(f"⚠️  {roll_no}: Network error.")
            continue

        try:
            tickets = list_response.json()
        except:
            print(f"⚠️  {roll_no}: Invalid Roll No.")
            continue

        if not tickets:
            print(f"⚠️  {roll_no}: No tickets.")
            continue

        for t in tickets:
            ticket_id = t["Text"]
            exam_name = t["Value"]

            safe_exam_name = re.sub(r'[\\/:*?"<>|]', "_", exam_name)
            
            # UPDATED FILENAME: 23071A_66_01_ExamName.pdf
            filename = f"{prefix_input}_{branch_code}_{suffix}_{safe_exam_name}.pdf"
            file_path = os.path.join(full_save_path, filename)

            if os.path.exists(file_path):
                print(f"⏭️  {roll_no}: Already exists.")
                continue

            download_url = f"https://vnrvjietexams.net/EduPrime3Exam/HallTicket/Get?id={ticket_id}"
            pdf_response = session.get(download_url, headers=headers)

            if pdf_response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(pdf_response.content)
                print(f"✅ {roll_no}: Downloaded.")
            else:
                print(f"❌ {roll_no}: Download failed.")

    except Exception as e:
        print(f"❌ {roll_no}: Error - {e}")

print("\n🎉 Batch processing finished.")