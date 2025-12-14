import requests
import os
import re
import time

# --- CONFIGURATION (CONSTANTS) ---
# This is the prefix for 2nd Year (2023 Batch). 
# You can change this to "24075A" if you need Lateral Entry.
COLLEGE_PREFIX = "23071A" 
SAVE_DIR_NAME = r"C:\Users\chari\hall_downloads"
DELAY_SECONDS = 0.5 

def get_full_sequence():
    """
    Creates the master list of all possible ID suffixes:
    01-99, then A0-A9, B0-B9 ... up to Z9
    """
    full_ids = []
    
    # 1. Add numbers 01 to 99
    for i in range(1, 100):
        full_ids.append(f"{i:02d}")
        
    # 2. Add alphabets A0 to Z9
    # ASCII value of A is 65, Z is 90
    for char_code in range(65, 91): 
        char = chr(char_code)
        for num in range(0, 10):
            full_ids.append(f"{char}{num}")
            
    return full_ids

# --- STEP 1: GET USER INPUTS ---
print("-" * 50)
print(" VNR VJIET HALL TICKET DOWNLOADER ")
print("-" * 50)

# Input Branch Code
branch_code = input(f"Enter Branch Code (e.g., 66, 05, 12): ").strip()

# Input Start and End Series
print("Enter the suffixes (e.g., 01, 99, A0, K6)")
start_input = input("Start Number (e.g., 01): ").strip().upper()
end_input   = input("End Number   (e.g., K6): ").strip().upper()

# Normalize inputs (Turn "5" into "05")
if start_input.isdigit(): start_input = start_input.zfill(2)
if end_input.isdigit():   end_input = end_input.zfill(2)

# --- STEP 2: CALCULATE THE ROLL LIST ---
master_sequence = get_full_sequence()

if start_input not in master_sequence or end_input not in master_sequence:
    print("❌ Error: Invalid start or end number format.")
    print("   Please use format like '01' or 'A5'.")
    exit()

start_index = master_sequence.index(start_input)
end_index = master_sequence.index(end_input)

if start_index > end_index:
    print("❌ Error: Start number cannot be after End number.")
    exit()

# Slice the list to get only the requested range
target_suffixes = master_sequence[start_index : end_index + 1]

# Generate full Roll Numbers
roll_list = [f"{COLLEGE_PREFIX}{branch_code}{suffix}" for suffix in target_suffixes]

print(f"\n📋 Prepared {len(roll_list)} roll numbers.")
print(f"   From: {roll_list[0]}")
print(f"   To:   {roll_list[-1]}")
print(f"📂 Saving to: {SAVE_DIR_NAME}")

confirm = input("\nType 'y' to start downloading: ").lower()
if confirm != 'y':
    print("Cancelled.")
    exit()

# --- STEP 3: DOWNLOAD LOOP ---
os.makedirs(SAVE_DIR_NAME, exist_ok=True)
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

for roll_no in roll_list:
    try:
        # Get List
        list_url = f"https://vnrvjietexams.net/EduPrime3Exam/HallTicket/GetList?id={roll_no}"
        time.sleep(DELAY_SECONDS) # Polite delay
        
        list_response = session.get(list_url, headers=headers)
        
        # Check if request was successful
        if list_response.status_code != 200:
            print(f"⚠️  {roll_no}: Network error or bad request.")
            continue

        try:
            tickets = list_response.json()
        except:
            # Usually means the server returned an HTML error page because RollNo doesn't exist
            print(f"⚠️  {roll_no}: Not found (Invalid Roll No).")
            continue

        if not tickets:
            print(f"⚠️  {roll_no}: No tickets available.")
            continue

        # Download each ticket found
        for t in tickets:
            ticket_id = t["Text"]
            exam_name = t["Value"]

            # Clean filename
            safe_exam_name = re.sub(r'[\\/:*?"<>|]', "_", exam_name)
            filename = f"{roll_no}_{safe_exam_name}.pdf"
            file_path = os.path.join(SAVE_DIR_NAME, filename)

            if os.path.exists(file_path):
                print(f"⏭️  {roll_no}: Already exists.")
                continue

            # Download PDF
            download_url = f"https://vnrvjietexams.net/EduPrime3Exam/HallTicket/Get?id={ticket_id}"
            pdf_response = session.get(download_url, headers=headers)

            if pdf_response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(pdf_response.content)
                print(f"✅ {roll_no}: Downloaded.")
            else:
                print(f"❌ {roll_no}: Failed to get PDF file.")

    except Exception as e:
        print(f"❌ {roll_no}: Unexpected Error - {e}")

print("\n🎉 Batch processing finished.")