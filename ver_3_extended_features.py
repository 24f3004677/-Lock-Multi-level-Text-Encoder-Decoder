import os
import sys
import json
import random
import base64
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)
# test test #test 

# ---------------- Digits for base conversions (up to base 16) ----------------
digits = "0123456789ABCDEF"

# ---------------- Conversion Helpers ----------------
def int_to_base(n, base):
    if n == 0:
        return "0"
    result = []
    while n > 0:
        result.append(digits[n % base])
        n //= base
    result.reverse()
    return "".join(result)

def base_to_int(s, base):
    n = 0
    for char in s:
        n = n * base + digits.index(char)
    return n

def str_to_base_n(s, base):
    return " ".join(int_to_base(ord(c), base) for c in s)

def base_n_to_str(basestr, base):
    chars = basestr.split()
    return "".join(chr(base_to_int(ch, base)) for ch in chars)

# ---------------- Mapping Dictionaries ----------------
str_to_func = {b: (lambda s, bb=b: str_to_base_n(s, bb)) for b in range(2, 17)}
func_to_str = {b: (lambda s, bb=b: base_n_to_str(s, bb)) for b in range(2, 17)}

# ---------------- Encoding / Decoding ----------------
def multi_encode(message, levels):
    key_list = []
    current_message = message
    for _ in range(levels):
        code = random.choice(list(str_to_func.keys()))
        key_list.append(code)
        current_message = str_to_func[code](current_message)
    key_list=key_list[-1::-1]
    return {"message": current_message, "key": key_list}
'''
def multi_decode(data):
    current_message = data["message"]
    try:
        ## for older version message decode service
        for code in data["key"][::-1]:
            current_message = func_to_str[code](current_message)
        return current_message
    except Exception :
        ## for neweer version message docode service
        for code in data["key"]:
            current_message = func_to_str[code](current_message)
        return current_message
'''
def multi_decode(data, reverse_key=True):
    current_message = data["message"]
    key = data["key"]
    
    # Use correct key order based on version
    key_seq = key[::-1] if reverse_key else key
    
    try:
        for code in key_seq:
            current_message = func_to_str[code](current_message)
        return current_message
    except KeyError:
        # Fallback: try opposite order
        alt_seq = key if reverse_key else key[::-1]
        for code in alt_seq:
            current_message = func_to_str[code](current_message)
        return current_message
    except Exception as e:
        raise ValueError(f"Decode failed: {e}")

# ---------------- File Handling ----------------
def encode_file_to_base64(file_path):
    """Convert file to base64 string"""
    try:
        with open(file_path, "rb") as file:
            file_data = file.read()
            encoded_data = base64.b64encode(file_data).decode('utf-8')
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            return f"FILE:{file_name}:{file_ext}:{encoded_data}"
    except Exception as e:
        print(Fore.RED + f"Error encoding file {file_path}: {e}")
        return None

def decode_base64_to_file(encoded_data, output_dir):
    """Convert base64 string back to file"""
    try:
        if not encoded_data.startswith("FILE:"):
            return None

        parts = encoded_data.split(":", 3)
        if len(parts) != 4:
            return None

        _, file_name, file_ext, encoded_content = parts

        # Decode base64
        file_data = base64.b64decode(encoded_content)

        # Create output path
        output_path = os.path.join(output_dir, file_name)

        # Ensure unique filename if file already exists
        counter = 1
        base_name = os.path.splitext(file_name)[0]
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{base_name}_{counter}{file_ext}")
            counter += 1

        # Write file
        with open(output_path, "wb") as file:
            file.write(file_data)

        return output_path
    except Exception as e:
        print(Fore.RED + f"Error decoding file: {e}")
        return None
def get_exe_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable) ## returns the exe file's directory  path or location 
    else:
        return os.path.dirname(os.path.abspath(__file__)) ## returns the this .py file's directory  location 

def get_save_path(filename):
    exe_dir = get_exe_dir()
    print(Fore.CYAN + "Do you want to save in a new folder? (y/n): ", end="")
    use_new_folder = input().strip().lower()

    if use_new_folder == "y":
        print(Fore.CYAN + "Enter new folder name: ", end="")
        folder_name = input().strip()
        folder_path = os.path.join(exe_dir, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(Fore.GREEN + f"📂 Created new folder: {folder_path}")
        return os.path.join(folder_path, filename)
    else:
        return os.path.join(exe_dir, filename)

def find_all_encoded_files(base_dir):
    """Recursively find all .lem and .json files in base_dir and subfolders"""
    encoded_files = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith((".lem", ".json")):
                full_path = os.path.join(root, f)
                encoded_files.append(full_path)
    return encoded_files

# ---------------- User & Contact Management ----------------
USERS_FILE = "users.json"
CONTACTS_FILE = "contacts.json"
def initialize_files():
    # Create users.json if missing
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump([], f)  # empty list of users

    # Create contacts.json if missing
    if not os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, "w") as f:
            json.dump([], f)  # empty list of contacts

def load_json(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def register_user():
    users = load_json(USERS_FILE)
    phone = input(Fore.CYAN + "Enter phone number: " + Style.RESET_ALL)
    if any(u['phone'] == phone for u in users):
        print(Fore.RED + "User already exists!" + Style.RESET_ALL)
        print(Fore.CYAN + "Please Login Using Password" + Style.RESET_ALL)
        return
    name = input(Fore.CYAN + "Enter name: " + Style.RESET_ALL)
    login_pass = input(Fore.CYAN + "Set login password: " + Style.RESET_ALL)
    decode_pass = input(Fore.CYAN + "Set decode password: " + Style.RESET_ALL)

    users.append({
        "name": name,
        "phone": phone,
        "login_password": login_pass,
        "decode_password": decode_pass
    })
    save_json(USERS_FILE, users)
    print(Fore.GREEN + "✅ User registered successfully!" + Style.RESET_ALL)

def login_user():
    users = load_json(USERS_FILE)
    while True:
        phone = input(Fore.CYAN + "Enter phone number: " + Style.RESET_ALL)
        password = input(Fore.CYAN + "Enter login password: " + Style.RESET_ALL)
        for u in users:
            if u['phone'] == phone and u['login_password'] == password:
                print(Fore.GREEN + f"Welcome {u['name']}!" + Style.RESET_ALL)
                return u
        print(Fore.RED + "❌ Invalid phone number or password." + Style.RESET_ALL)
        

def add_contact():
    contacts = load_json(CONTACTS_FILE)
    name = input(Fore.CYAN + "Enter contact name: " + Style.RESET_ALL)
    phone = input(Fore.CYAN + "Enter contact phone: " + Style.RESET_ALL)
    contacts.append({"name": name, "phone": phone})
    save_json(CONTACTS_FILE, contacts)
    print(Fore.GREEN + "✅ Contact added!" + Style.RESET_ALL)

def edit_contact():
    contacts = load_json(CONTACTS_FILE)
    if not contacts:
        print(Fore.RED + "❌ No contacts found." + Style.RESET_ALL)
        return

    while True:
        print(Fore.GREEN +"---------------------------------------"+Fore.RESET)
        print(Fore.GREEN +"Contact List" )
        print(Fore.GREEN +"---------------------------------------"+Fore.RESET)
        for i, c in enumerate(contacts):
            print(f"{i+1}. {c['name']} ({c['phone']})")
        print(Fore.GREEN +"---------------------------------------"+Fore.RESET)
        print(Fore.YELLOW + f"{len(contacts)+1}. Delete a contact" + Fore.RESET)
        print(Fore.YELLOW + f"{len(contacts)+2}. Back to main menu" + Fore.RESET)

        try:
            choice = int(input(Fore.CYAN + "Select contact to edit or delete: " + Style.RESET_ALL))
            if 1 <= choice <= len(contacts):
                # Edit contact
                contact_idx = choice - 1
                print(Fore.CYAN + f"Editing contact: {contacts[contact_idx]['name']} ({contacts[contact_idx]['phone']})" + Fore.RESET)
                new_name = input(Fore.CYAN + "Enter new name (leave empty to keep current): " + Style.RESET_ALL).strip()
                new_phone = input(Fore.CYAN + "Enter new phone (leave empty to keep current): " + Style.RESET_ALL).strip()

                if new_name:
                    contacts[contact_idx]['name'] = new_name
                if new_phone:
                    contacts[contact_idx]['phone'] = new_phone

                if new_name or new_phone:
                    save_json(CONTACTS_FILE, contacts)
                    print(Fore.GREEN + "✅ Contact updated!" + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + "No changes made." + Fore.RESET)

            elif choice == len(contacts) + 1:
                # Delete contact
                if not contacts:
                    print(Fore.RED + "❌ No contacts to delete." + Style.RESET_ALL)
                    continue

                del_choice = int(input(Fore.CYAN + "Select contact to delete (number): " + Style.RESET_ALL)) - 1
                if 0 <= del_choice < len(contacts):
                    deleted_contact = contacts.pop(del_choice)
                    save_json(CONTACTS_FILE, contacts)
                    print(Fore.GREEN + f"✅ Contact '{deleted_contact['name']}' deleted!" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "❌ Invalid choice." + Style.RESET_ALL)

            elif choice == len(contacts) + 2:
                # Back to main menu
                break
            else:
                print(Fore.RED + "❌ Invalid choice." + Style.RESET_ALL)
                continue

        except ValueError:
            print(Fore.RED + "❌ Please enter a valid number." + Style.RESET_ALL)
            continue
def pass_(text,section):
    users = load_json(USERS_FILE)
    while True:
        old_pass = input(Fore.CYAN + text + Style.RESET_ALL)
        for u in users:
            if u[section] == old_pass :
                return 1
            else:
                print(Fore.RED + "❌ Invalid password." + Style.RESET_ALL)

def edit_log_in_credentials():
    contacts = load_json(USERS_FILE)
    print(Fore.BLUE +"---------------------------------------"+Fore.RESET)
    print(Fore.BLUE +"Edit Personal Credentials" )
    print(Fore.BLUE +"---------------------------------------"+Fore.RESET)
    #name change
    new_name=input(Fore.CYAN + "Enter new name: " + Style.RESET_ALL)
    if new_name!="":
        contacts[0]['name'] = new_name
        print(Fore.GREEN + "✅ Name updated!" + Style.RESET_ALL)
    else: pass
    #phone number change
    new_phone=input(Fore.CYAN + "Enter new phone: " + Style.RESET_ALL)
    if new_phone!="":
        contacts[0]['phone'] = new_phone
        print(Fore.GREEN + "✅ Contact updated!" + Style.RESET_ALL)
    if pass_("Enter Old Login PassWord : ","login_password"):
        new_log_in_pass=input(Fore.CYAN + "Enter New Login Password: " + Style.RESET_ALL)
        if new_log_in_pass!="":
            contacts[0]["login_password"]=new_log_in_pass
            print(Fore.GREEN + "✅ Login Password updated!" + Style.RESET_ALL)
        else:
            pass
    if pass_("Enter Old Message Viewing Password : ","decode_password"):
        new_decoded_message_pass=input(Fore.CYAN + "Enter New Message Viewing Password: " + Style.RESET_ALL)
        if new_decoded_message_pass!="":
            contacts[0]["decode_password"]=new_decoded_message_pass
            print(Fore.GREEN + "✅ Message Viewing Password updated!" + Style.RESET_ALL)
        else:
            pass
    elif(new_name=="" and new_phone=="" and new_log_in_pass=="" and new_decoded_message_pass==""):
        print(Fore.LIGHTMAGENTA_EX + "\nNo Changes Made"+ Fore.RESET +"\n-----------------------------------")
    save_json(USERS_FILE, contacts)
    print(Fore.GREEN+"Updated Porfile Cridentials"+Fore.RESET)
    print(contacts[0])
def choose_receiver():
    contacts = load_json(CONTACTS_FILE)
    if not contacts:
        print(Fore.RED + "❌ No contacts found. Please add contacts first." + Style.RESET_ALL)
        print(Fore.BLUE +"Add Your Receiver's Details" + Fore.RESET)
        add_contact()
        return choose_receiver()  # Return the result of the recursive call

    while True:
        print(Fore.GREEN +"---------------------------------------"+Fore.RESET)
        print(Fore.GREEN +"Contact List"+ Fore.RESET)
        print(Fore.GREEN +"---------------------------------------"+Fore.RESET)
        for i, c in enumerate(contacts):
            print(f"{i+1}. {c['name']} ({c['phone']})")
        print(Fore.GREEN +"---------------------------------------"+Fore.RESET)
        print(Fore.YELLOW + f"{len(contacts)+1}. Add new contact" + Fore.RESET)

        try:
            receiver=[]
            while True:
                choice = int(input(Fore.CYAN + "Select receiver: " + Fore.RESET))
                if 1 <= choice <= len(contacts):
                    receiver.append(contacts[choice-1]['phone'])  # Fixed: use choice-1 for 0-based indexing
                    more_contact=str(input("Do you want to add more receivers? y/n ")).lower()
                    if more_contact == 'y':
                        continue
                    else:
                        break
                elif choice == len(contacts) + 1:
                    print(Fore.BLUE + "Adding new contact..." + Fore.RESET)
                    add_contact()
                    contacts = load_json(CONTACTS_FILE)  # Reload contacts
                    continue
                else:
                    print(Fore.RED + f"❌ Invalid choice. Please select a number between 1 and {len(contacts)+1}" + Fore.RESET)
                    continue
            return receiver
        except ValueError:
            print(Fore.RED + "❌ Please enter a valid number." + Fore.RESET)
            continue


# ---------------- Encode & Decode ----------------
def encode_message(user):
    print(Fore.CYAN + "Enter your message (blank line + Enter to finish):" + Style.RESET_ALL)
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    message = "\n".join(lines)

    # Handle file attachments
    attachments = []
    while True:
        add_file = input(Fore.CYAN + "Do you want to attach a file? (y/n): " + Style.RESET_ALL).strip().lower()
        if add_file == 'y':
            file_path = input(Fore.CYAN + "Enter file path (image or PDF): " + Style.RESET_ALL).strip()
            # Remove surrounding quotes if present
            if (file_path.startswith('"') and file_path.endswith('"')) or (file_path.startswith("'") and file_path.endswith("'")):
                file_path = file_path[1:-1]
            if os.path.exists(file_path):
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.pdf']:
                    encoded_file = encode_file_to_base64(file_path)
                    if encoded_file:
                        attachments.append(encoded_file)
                        print(Fore.GREEN + f"✅ File '{os.path.basename(file_path)}' attached!" + Style.RESET_ALL)
                    else:
                        print(Fore.RED + "❌ Failed to encode file." + Style.RESET_ALL)
                else:
                    print(Fore.RED + "❌ Only image files (jpg, png, gif, bmp) and PDF files are supported." + Style.RESET_ALL)
            else:
                print(Fore.RED + "❌ File not found." + Style.RESET_ALL)
        elif add_file == 'n':
            break
        else:
            print(Fore.YELLOW + "Please enter 'y' or 'n'." + Style.RESET_ALL)

    # Combine message and attachments
    full_message = message
    if attachments:
        attachment_str = "\n\n---ATTACHMENTS---\n" + "\n".join(attachments)
        full_message += attachment_str

    print(Fore.CYAN + "Enter level of encryption (e.g., 3): ", end="")
    try:
        levels = int(input().strip())
    except ValueError:
        print(Fore.RED + "❌ Invalid input, defaulting to 1 level.")
        levels = 1

    encoded = multi_encode(full_message, levels)
    while True:
        receiver = choose_receiver()
        if not receiver:
            print(Fore.RED+ "select proper receiver" +Fore.RESET)
        else:
            break

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    encoded["receiver"] = receiver
    encoded["timestamp"] = timestamp
    encoded["sender"] = user["phone"]

    default_filename = f"encoded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.lem"
    print(Fore.CYAN + f"Enter filename to save (default: {default_filename}) ", end="")
    print(Fore.RED +"[Custom filename ]"+ Fore.RESET ,":")
    filename = input().strip()
    if not filename.endswith(".lem"):
        filename=filename+".lem"
    if not filename:
        filename = default_filename

    save_path = get_save_path(filename)
    with open(save_path, "w") as f:
        json.dump(encoded, f)

    print(Fore.GREEN + f"✅ Encoded message saved at: {save_path}")
    print(Fore.YELLOW + "\nEncoded result (copy this if needed):" + Style.RESET_ALL)
    print(json.dumps(encoded))
'''
def decode_message(user):
    exe_dir = get_exe_dir()
    encoded_files = find_all_encoded_files(exe_dir)

    if not encoded_files:
        print(Fore.RED + "❌ No encoded files found.")
        return

    encoded_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)

    print(Fore.YELLOW + f"Available files in {exe_dir} and subfolders:")
    for idx, f in enumerate(encoded_files, start=1):
        rel_path = os.path.relpath(f, exe_dir)
        print(Fore.MAGENTA + f"[{idx}] {rel_path}")

    print(Fore.CYAN + "Enter file number to decode (or press Enter for latest): ", end="")
    choice = input().strip()

    if not choice:
        file_path = encoded_files[0]
        rel_path = os.path.relpath(file_path, exe_dir)
        print(Fore.GREEN + f"📂 Auto-selected latest file: {rel_path}")
    elif choice.isdigit() and 1 <= int(choice) <= len(encoded_files):
        file_path = encoded_files[int(choice) - 1]
    else:
        print(Fore.RED + "❌ Invalid choice.")
        return

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        decoded = multi_decode(data)
        print(Fore.YELLOW + Style.BRIGHT + f"🔓 Decoded message:")
        print(decoded) 
    except Exception:     
        with open(file_path, "r") as f:
            data = json.load(f)

        if user["phone"] not in data["receiver"] :
            print(Fore.RED + "❌ This message is not meant for you!" + Style.RESET_ALL)
            return

        decode_pass = input(Fore.CYAN + "Enter your decode password: " + Style.RESET_ALL)
        if decode_pass != user["decode_password"]:
            print(Fore.RED + "❌ Incorrect decode password!" + Style.RESET_ALL)
            return

        decoded = multi_decode(data)
        print(Fore.GREEN + "🔓 Decoded message:" + Style.RESET_ALL)

        # Separate message and attachments
        if "\n\n---ATTACHMENTS---\n" in decoded:
            message_part, attachment_part = decoded.split("\n\n---ATTACHMENTS---\n", 1)
            print(message_part)

            # Handle attachments
            if attachment_part.strip():
                print(Fore.YELLOW + "\n📎 Attachments found!" + Style.RESET_ALL)
                save_attachments = input(Fore.CYAN + "Do you want to save the attachments? (y/n): " + Style.RESET_ALL).strip().lower()

                if save_attachments == 'y':
                    # Create attachments directory
                    attachments_dir = os.path.join(exe_dir, "decoded_attachments")
                    if not os.path.exists(attachments_dir):
                        os.makedirs(attachments_dir)

                    attachment_lines = attachment_part.strip().split('\n')
                    saved_files = []

                    for line in attachment_lines:
                        if line.startswith("FILE:"):
                            saved_path = decode_base64_to_file(line, attachments_dir)
                            if saved_path:
                                saved_files.append(saved_path)

                    if saved_files:
                        print(Fore.GREEN + "✅ Attachments saved to:" + Style.RESET_ALL)
                        for file_path in saved_files:
                            print(Fore.BLUE + f"  - {file_path}" + Style.RESET_ALL)
                    else:
                        print(Fore.RED + "❌ No attachments were saved." + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + "Attachments not saved." + Style.RESET_ALL)
        else:
            print(decoded)

        print(Fore.YELLOW + f"\n--- Encoded on: {data['timestamp']} by {data['sender']} ---" + Style.RESET_ALL)

        # Option to save decoded message
        save_decoded = input(Fore.CYAN + "Do you want to save the decoded message to a file? (y/n): " + Style.RESET_ALL).strip().lower()
        if save_decoded == 'y':
            default_filename = f"decoded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            print(Fore.CYAN + f"Enter filename to save (default: {default_filename}): ", end="")
            filename = input().strip()
            if not filename:
                filename = default_filename

            save_path = get_save_path(filename)
            with open(save_path, "w", encoding='utf-8') as f:
                f.write(decoded)
            print(Fore.GREEN + f"✅ Decoded message saved at: {save_path}")
           
    except Exception as e:
        print(Fore.RED + f"❌ Failed to decode file: {e}")
'''
def decode_message(user):
    exe_dir = get_exe_dir() ## finds the directory where the exe file or .py file  is there 
    encoded_files = find_all_encoded_files(exe_dir) ## this gets all the files in that directory 

    if not encoded_files:  ## if there is no encoded files of any files are present 
        print(Fore.RED + "❌ No encoded files found.")
        return

    encoded_files.sort(key=lambda f: os.path.getmtime(f), reverse=True) ## it sorts the files in that directory wrt time modified

    print(Fore.YELLOW + f"Available files in {exe_dir} and subfolders:")
    for idx, f in enumerate(encoded_files, start=1):
        rel_path = os.path.relpath(f, exe_dir)
        print(Fore.MAGENTA + f"[{idx}] {rel_path}")

    print(Fore.CYAN + "Enter file number to decode (or press Enter for latest): ", end="")
    choice = input().strip()

    if not choice:
        file_path = encoded_files[0]
        rel_path = os.path.relpath(file_path, exe_dir)
        print(Fore.GREEN + f"📂 Auto-selected latest file: {rel_path}")
    elif choice.isdigit() and 1 <= int(choice) <= len(encoded_files):
        file_path = encoded_files[int(choice) - 1]
    else:
        print(Fore.RED + "❌ Invalid choice.")
        return

    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        # Detect version
        ext = os.path.splitext(file_path)[1].lower()
        if "sender" in data and ext == '.lem':
            version = 3
            reverse_key = False
        elif "receiver" in data:
            version = 2
            reverse_key = True
        else:
            version = 1
            reverse_key = True

        # Auth only for v2/v3
        if version >= 2:
            if user["phone"] not in data["receiver"]:
                print(Fore.RED + "❌ This message is not meant for you!" + Style.RESET_ALL)
                return
            decode_pass = input(Fore.CYAN + "Enter your decode password: " + Style.RESET_ALL)
            if decode_pass != user["decode_password"]:
                print(Fore.RED + "❌ Incorrect decode password!" + Style.RESET_ALL)
                return

        # Decode with correct key order
        decoded = multi_decode(data,reverse_key=reverse_key)  # Pass reverse_key param
        print(Fore.YELLOW + Style.BRIGHT + f"🔓 Decoded message (v{version}):")
        
        # Safe attachments handling
        saved_files = []
        if "\n\n---ATTACHMENTS---\n" in decoded:
            message_part, attachment_part = decoded.split("\n\n---ATTACHMENTS---\n", 1)
            print(message_part)

            if attachment_part.strip():
                print(Fore.YELLOW + "\n📎 Attachments found!" + Style.RESET_ALL)
                save_attachments = input(Fore.CYAN + "Do you want to save the attachments? (y/n): " + Style.RESET_ALL).strip().lower()
                if save_attachments == 'y':
                    attachments_dir = os.path.join(exe_dir, "decoded_attachments")
                    os.makedirs(attachments_dir, exist_ok=True)
                    attachment_lines = attachment_part.strip().split('\n')
                    for line in attachment_lines:
                        if line.startswith("FILE:"):
                            saved_path = decode_base64_to_file(line, attachments_dir)
                            if saved_path:
                                saved_files.append(saved_path)
                    if saved_files:
                        print(Fore.GREEN + "✅ Attachments saved to:" + Style.RESET_ALL)
                        for sp in saved_files:
                            print(Fore.BLUE + f"  - {sp}" + Style.RESET_ALL)
                    else:
                        print(Fore.RED + "❌ No attachments were saved." + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + "No attachments content." + Style.RESET_ALL)
        else:
            print(decoded)

        # Safe metadata display - only if fields exist
        metadata = []
        if version >= 2 and 'timestamp' in data:
            metadata.append(f"Encoded on: {data['timestamp']}")
        if version == 3 and 'sender' in data:
            metadata.append(f"by {data['sender']}")
        if metadata:
            print(Fore.YELLOW + " | ".join(metadata) + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "(v1 - no metadata)" + Style.RESET_ALL)

        # Save option (unchanged)
        save_decoded = input(Fore.CYAN + "Do you want to save the decoded message to a file? (y/n): " + Style.RESET_ALL).strip().lower()
        if save_decoded == 'y':
            default_filename = f"decoded_v{version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            print(Fore.CYAN + f"Enter filename (default: {default_filename}): ", end="")
            filename = input().strip() or default_filename
            save_path = get_save_path(filename)
            with open(save_path, "w", encoding='utf-8') as f:
                f.write(decoded)
            print(Fore.GREEN + f"✅ Saved: {save_path}" + Style.RESET_ALL)

    except json.JSONDecodeError as e:
        print(Fore.RED + f"❌ Invalid JSON: {e}")
    except KeyError as e:
        print(Fore.RED + f"❌ Missing required field: {e}")
    except Exception as e:
        print(Fore.RED + f"❌ Decode error: {e}")

# ---------------- Main ---------------- login option 
def main():
    flag = True
    while flag:
        # Load users from file
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                try:
                    users = json.load(f)
                except json.JSONDecodeError:
                    users = []
        else:
            users = []

        if not users:  # No registered users yet
            print(Fore.YELLOW + "⚠️ No users found. Please register first." + Style.RESET_ALL)
            register_user()
        else:
            while True:
                print(Fore.CYAN + "\nMain Menu:")
                print(Fore.YELLOW + "1. Login")
                print(Fore.YELLOW + "2. Exit")
                print(Fore.CYAN + "Enter choice: ", end="")
                choice = input().strip()
                
                if choice == "1":
                    user = login_user()
                    if user:
                        while True:
                            print(Fore.CYAN + "\nUser Menu:")
                            print(Fore.YELLOW + "1. Encode Message")
                            print(Fore.YELLOW + "2. Decode Message")
                            print(Fore.YELLOW + "3. Add Contact")
                            print(Fore.YELLOW + "4. Edit Contact")
                            print(Fore.YELLOW + "5. Edit Profile Credentials")
                            print(Fore.YELLOW + "6. Logout")
                            print(Fore.CYAN + "Enter choice: ", end="")
                            sub_choice = input().strip()
                            if sub_choice == "1":
                                encode_message(user)
                            elif sub_choice == "2":
                                decode_message(user)
                            elif sub_choice == "3":
                                add_contact()
                            elif sub_choice == "4":
                                edit_contact()
                            elif sub_choice=="5":
                                edit_log_in_credentials()
                            elif sub_choice == "6":
                                break
                            else:
                                print(Fore.RED + "❌ Invalid option." + Style.RESET_ALL)

                elif choice == "2":
                    print(Fore.GREEN + "👋 Exiting...")
                    flag = False
                    break
                else:
                    print(Fore.RED + "❌ Invalid option." + Style.RESET_ALL)


if __name__ == "__main__":
    initialize_files()
    main()
    
# task to be done next 
# 1. to able to add multiple receivers✅
# 2. to make it executale .exe
# 3. try to add ui/ux (later versions)
# 4. make it master version proof ✅
# 5. support for old version message decoding (only) ✅
# 6. new file format .lem , can read .json files also ✅
# 7. need to add chat history (terminal / UI ??)
# 8. for every person in the chat there will be a separate folder and all the messages will be there 
# 9. sender no. will be there .   ✅

