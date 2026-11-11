"""真实 Chromium 交互；通过测试代理接入隔离 API，不保存 trace/凭证/截图。"""

import asyncio
import json
import os
from urllib.parse import urlsplit

from playwright.async_api import async_playwright, expect


async def main():
    config = json.loads(os.environ["AI_BROWSER_TEST_CONFIG"])
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        errors = []

        async def context_for(role):
            context = await browser.new_context()
            page = await context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))

            async def proxy(route):
                path = urlsplit(route.request.url)
                response = await context.request.fetch(
                    config["api_url"] + path.path + ("?" + path.query if path.query else ""),
                    method=route.request.method,
                    headers=route.request.headers,
                    data=route.request.post_data_buffer,
                )
                await route.fulfill(response=response)

            await page.route("**/api/v1/**", proxy)
            await page.goto(config["web_url"] + "/login")
            await page.get_by_placeholder("用户名", exact=True).fill(config[role])
            await page.get_by_placeholder("密码", exact=True).fill(config["password"])
            await page.locator('button[type="submit"]').click()
            await page.wait_for_url(lambda url: "/login" not in urlsplit(url).path)
            return context, page

        admin_context, page = await context_for("admin")
        await page.goto(config["web_url"] + "/classroom/ai-devices")
        await expect(page.get_by_text("注册设备", exact=True)).to_be_visible()
        await page.get_by_placeholder("设备名称", exact=True).fill("browser-device")
        await page.get_by_placeholder("source alias，例如 camera-1", exact=True).fill("browser-camera")
        await page.get_by_placeholder("获准教师 ID，逗号分隔", exact=True).fill(str(config["teacher_id"]))
        await page.get_by_role("button", name="注册", exact=True).click()
        await expect(page.get_by_text("browser-device", exact=False).first).to_be_visible()
        await page.get_by_role("button", name="签发 / 轮换凭证", exact=True).last.click()
        await page.get_by_role("button", name="确认", exact=True).click()
        await expect(page.get_by_test_id("device-secret")).to_contain_text("aic_")
        secret = await page.get_by_test_id("device-secret").inner_text()
        storage = await page.evaluate("JSON.stringify(localStorage)")
        assert secret not in storage
        await page.get_by_role("button", name="已保存，关闭并清除", exact=True).click()
        await expect(page.get_by_test_id("device-secret")).not_to_be_visible()
        assert secret not in await page.locator("body").inner_text()
        del secret
        await admin_context.close()

        teacher_context, page = await context_for("teacher")
        await page.goto(config["web_url"] + f"/teacher/classroom/detail?session_id={config['session_id']}")
        await expect(page.get_by_text("AI 课堂采集", exact=True)).to_be_visible()
        await expect(page.get_by_role("button", name="暂停", exact=True)).to_be_enabled()
        await page.get_by_role("button", name="暂停", exact=True).click()
        await expect(page.get_by_text("期望：已暂停", exact=False)).to_be_visible()
        await page.goto(config["web_url"] + "/classroom/ai-jobs")
        await expect(page.get_by_text("AI 课堂采集", exact=True)).to_be_visible()
        await page.goto(config["web_url"] + f"/teacher/classroom/detail?session_id={config['foreign_session_id']}")
        await expect(page.get_by_text("AI 课堂采集", exact=True)).not_to_be_visible()
        await teacher_context.close()

        student_context, page = await context_for("student")
        calls = []
        page.on("request", lambda request: calls.append(request.url) if "/ai/" in request.url else None)
        await page.goto(config["web_url"] + "/classroom/ai-jobs")
        await page.wait_for_timeout(1200)
        assert "/classroom/ai-jobs" not in page.url
        assert not calls
        await student_context.close()
        assert not errors, errors
        await browser.close()
        print("Chromium: admin register/once-secret/clear; teacher pause/own-scope; student route isolation passed.")


if __name__ == "__main__":
    asyncio.run(main())
