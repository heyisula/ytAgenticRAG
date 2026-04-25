from selenium import webdriver
import time

def export_youtube_cookies():
    print("Launching Microsoft Edge...")
    driver = webdriver.Edge()
    
    print("\nNavigating to YouTube...")
    driver.get("https://www.youtube.com")
    
    print("\n[!] ACTION REQUIRED:")
    print("1. A browser window has opened.")
    print("2. Please 'Accept All' cookies if it asks.")
    print("3. Optional: Log into your account if you want.")
    
    input("\nPress ENTER here in the terminal when you are fully loaded into YouTube...")
    
    cookies = driver.get_cookies()
    netscape_str = "# Netscape HTTP Cookie File\n"
    
    for cookie in cookies:
        domain = cookie['domain']
        flag = "TRUE" if domain.startswith('.') else "FALSE"
        path = cookie['path']
        secure = "TRUE" if cookie['secure'] else "FALSE"
        expiry = str(int(cookie.get('expiry', 2147483647)))
        name = cookie['name']
        value = cookie['value']
        
        netscape_str += f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n"
    
    with open("cookies.txt", "w") as f:
        f.write(netscape_str)
        
    print(f"\nSuccess! Dumped {len(cookies)} cookies to cookies.txt")
    driver.quit()

if __name__ == '__main__':
    export_youtube_cookies()
