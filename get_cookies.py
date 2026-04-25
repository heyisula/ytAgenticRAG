from selenium import webdriver
import time

def export_youtube_cookies():
    print("Launching Microsoft Edge (Stealth Mode)...")
    
    options = webdriver.EdgeOptions()
    # Bypass Google's anti-automation detection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Edge(options=options)
    
    # Hide the WebDriver flag
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    
    print("\nNavigating to YouTube...")
    driver.get("https://accounts.google.com/ServiceLogin?service=youtube&hl=en&continue=https%3A%2F%2Fwww.youtube.com%2F")
    
    print("\n[!] ACTION REQUIRED:")
    print("1. A browser window has opened to the Google Sign-in page.")
    print("2. Please sign into your account.")
    
    input("\nPress ENTER here in the terminal when you are fully logged in and on YouTube...")
    
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
