import asyncio
from playwright.async_api import async_playwright

async def take_screenshot(page, name, wait_selector=None, timeout=5000):
    print(f"Taking screenshot: {name}")
    if wait_selector:
        try:
            await page.wait_for_selector(wait_selector, timeout=timeout)
        except Exception as e:
            print(f"Timeout waiting for {wait_selector}: {e}")
    await page.wait_for_timeout(3000) # Wait a bit extra to ensure any toasts/animations are done
    
    # Hide all Streamlit UI elements that might block the view
    await page.add_style_tag(content="""
        header[data-testid="stHeader"] { display: none !important; }
        div[data-testid="stToolbar"] { display: none !important; }
        div[data-testid="stToastContainer"] { display: none !important; }
        div[data-testid="stDecoration"] { display: none !important; }
        div[data-testid="stStatusWidget"] { display: none !important; }
        div[data-testid="manage-app-button"] { display: none !important; }
        div.stAlert { opacity: 1 !important; } 
        div[role="dialog"] { display: none !important; }
    """)
    
    await page.screenshot(path=f"{name}.png", full_page=True)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1200})
        page = await context.new_page()

        print("Navigating to Streamlit app...")
        await page.goto("http://localhost:8501")
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)
        
        try:
            await page.click('button:has-text("Don\'t show again")', timeout=3000)
            print("Closed AI skills banner")
            await page.wait_for_timeout(1000)
        except Exception:
            pass
            
        # Hide header immediately
        await page.add_style_tag(content="""
            header[data-testid="stHeader"] { display: none !important; }
            div[data-testid="stToolbar"] { display: none !important; }
            div[data-testid="stToastContainer"] { display: none !important; }
            div[role="dialog"] { display: none !important; }
        """)
        
        print("Filling out Loan Risk Assessment...")
        try:
            # Fill in Name (search)
            await page.fill('input[placeholder="Start typing to search..."]', "John Doe")
            await page.click('button:has-text("🔍 Search")')
            await page.wait_for_timeout(2000)
            
            # Predict
            await page.click('button:has-text("🔮 GENERATE RISK ASSESSMENT")')
            await page.wait_for_timeout(4000)
            
            await take_screenshot(page, "1_Loan_Risk_Assessment")
            
        except Exception as e:
            print(f"Error in Loan Risk Assessment: {e}")
            await take_screenshot(page, "1_Loan_Risk_Assessment_Fallback")
            
        # 2. Customer Onboarding KYC Portal
        print("Navigating to Customer Onboarding...")
        try:
            await page.click('text="📝 Customer Onboarding"')
            await page.wait_for_timeout(2000)
            await take_screenshot(page, "2_Customer_Onboarding")
        except Exception as e:
            print(e)
            
        # 5. Customer Database
        print("Navigating to Customer Database...")
        try:
            await page.click('text="📋 Customer Database"')
            await page.wait_for_timeout(2000)
            await take_screenshot(page, "6_Customer_Database")
        except Exception as e:
            print(e)
            
        # 4. Portfolio Analytics
        print("Navigating to Portfolio Analytics...")
        try:
            await page.click('text="📊 Portfolio Analytics"')
            await page.wait_for_timeout(3000)
            await take_screenshot(page, "4_Portfolio_Analytics")
        except Exception as e:
            print(e)
            
        # 6. Model Intelligence
        print("Navigating to Model Intelligence...")
        try:
            await page.click('text="🤖 Model Intelligence"')
            await page.wait_for_timeout(2000)
            await take_screenshot(page, "5_Model_Intelligence")
        except Exception as e:
            print(e)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
