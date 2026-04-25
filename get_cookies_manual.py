def parse_raw_cookie_to_netscape():
    print("=========================================================")
    print("       MANUAL COOKIE EXTRACTION (NO EXTENSIONS)          ")
    print("=========================================================")
    print("Since Google blocks automated login, we'll extract it directly from your normal browser.")
    print("1. Open your normal web browser (Chrome/Edge) and go to https://www.youtube.com")
    print("2. Ensure you are signed in.")
    print("3. Press F12 to open Developer Tools.")
    print("4. Click the 'Network' tab at the top of the Developer Tools panel.")
    print("5. Refresh the YouTube page (F5).")
    print("6. In the Network panel list, click the very first item (usually 'www.youtube.com').")
    print("7. In the panel that opens, scroll down to 'Request Headers'.")
    print("8. Find the property called 'cookie:' (or 'Cookie:').")
    print("9. Right-click the massive text value next to it and select 'Copy value'.")
    print("\nPaste that entire copied text below and press ENTER:")
    
    raw_cookie = input("> ")
    
    if not raw_cookie or len(raw_cookie) < 50:
        print("Error: The copied cookie string seems too short or invalid.")
        return

    netscape_str = "# Netscape HTTP Cookie File\n"
    cookies = raw_cookie.split(";")
    
    for c in cookies:
        if "=" not in c: continue
        name_val = c.strip().split("=", 1)
        name = name_val[0]
        val = name_val[1]
        
        # Hardcoding standard YouTube domains for netscape mapping
        domain = ".youtube.com"
        flag = "TRUE"
        path = "/"
        secure = "TRUE"
        expiry = "2147483647"
        
        if name in ['__Secure-1PSID', '__Secure-3PSID', 'VISITOR_INFO1_LIVE', 'LOGIN_INFO', 'SID', 'HSID']:
            netscape_str += f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{val}\n"
    
    with open("cookies.txt", "w") as f:
        f.write(netscape_str)
        
    print("\nSUCCESS! Successfully parsed your cookies and created 'cookies.txt'.")
    print("You can now run `python app.py`!")

if __name__ == '__main__':
    parse_raw_cookie_to_netscape()
