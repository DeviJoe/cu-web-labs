import asyncio
import hashlib
import sqlite3
import time

from playwright.async_api import async_playwright

DATABASE = "users.db"


async def visit_url(url):
    """Admin bot visits the reported URL using Playwright"""
    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.chromium.launch(
                headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"]
            )

            context = await browser.new_context()
            page = await context.new_page()

            # Set timeout
            page.set_default_timeout(10000)

            # Login as admin
            await page.goto("http://localhost:5000/login")

            await page.fill('input[name="username"]', "admin")
            await page.fill('input[name="password"]', "admin_secret_password_123")

            await page.click('button[type="submit"]')

            # Wait for navigation
            await page.wait_for_timeout(1000)

            # Visit the reported URL
            await page.goto(url)
            await page.wait_for_timeout(3000)

        except Exception as e:
            print(f"Admin bot error: {e}")
        finally:
            if browser:
                await browser.close()


def visit_url_sync(url):
    """Synchronous wrapper for async visit_url"""
    asyncio.run(visit_url(url))
