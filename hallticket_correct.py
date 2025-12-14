import requests
import os
import re
import time

# --- CONFIGURATION ---
BASE_ROLL = "23071A66"
SAVE_PATH = r"C:\Users\chari\hall_batch"  # Changed folder name to keep them organized
DELAY_SECONDS = 0.5  # Time to wait between requests (prevents blocking)

# Create directory
os.makedirs(SAVE_PATH, exist_ok=True)

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def generate_roll_numbers():
    """Generates the list from 01-99, then A0-K6"""
    rolls = []
    
    # 1. Generate 01 to 99
    for i in range(1, 100):
        rolls.append(f"{BASE_ROLL}{i:02d}")
    
    # 2. Generate A0 to K6
    # Define range of letters from A to K
    start_char = 'A'
    end_char = 'K'
    
    for char_code in range(ord(start_char), ord(end_char) + 1):
        char = chr(char_code)
        
        # Determine the numeric limit for this letter
        # For 'K', we stop at 6. For others (A-J), we go 0-9.
        limit = 6 if char == 'K' else 9
        
        for num in range(0, limit + 1):
            rolls.append(f"{BASE_ROLL}{char}{num}")
            
    return rolls

# Generate the full list
student_list = generate_roll_numbers()
print(f"📋 Generated {len(student_list)} roll numbers to process.")
print(f"📂 Saving to: {SAVE_PATH}")
print("-" * 40)

# Loop through every student
for roll_no in student_list:
    try:
        # Step 1: Get list of tickets for this Roll No
        list_url = f"https://vnrvjietexams.net/EduPrime3Exam/HallTicket/GetList?id={roll_no}"
        
        # Short pause to be polite to the server
        time.sleep(DELAY_SECONDS)
        
        list_response = session.get(list_url, headers=headers)
        
        # If response isn't JSON or valid, skip
        if list_response.status_code != 200:
            print(f"⚠️  {roll_no}: Failed to fetch data.")
            continue

        try:
            tickets = list_response.json()
        except:
            # This happens if the server returns HTML (error page) instead of JSON
            print(f"⚠️  {roll_no}: No valid data found (Invalid Roll No?).")
            continue

        if not tickets:
            print(f"⚠️  {roll_no}: No hall tickets available.")
            continue

        # Step 2: Download tickets found
        for t in tickets:
            ticket_id = t["Text"]
            exam_name = t["Value"]

            # Clean filename
            safe_exam_name = re.sub(r'[\\/:*?"<>|]', "_", exam_name)
            
            # Construct filename: RollNo_ExamName.pdf
            filename = f"{roll_no}_{safe_exam_name}.pdf"
            file_path = os.path.join(SAVE_PATH, filename)

            # Check if we already downloaded it to save time
            if os.path.exists(file_path):
                print(f"⏭️  {roll_no}: Already downloaded.")
                continue

            download_url = f"https://vnrvjietexams.net/EduPrime3Exam/HallTicket/Get?id={ticket_id}"
            pdf_response = session.get(download_url, headers=headers)

            if pdf_response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(pdf_response.content)
                print(f"✅ {roll_no}: Downloaded.")
            else:
                print(f"❌ {roll_no}: Failed to download PDF.")

    except Exception as e:
        print(f"❌ {roll_no}: Error - {e}")

print("-" * 40)
print("🎉 Batch download complete!")