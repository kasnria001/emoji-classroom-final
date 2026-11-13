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
        assert urlsplit(page.url).path == "/classroom/dashboard"
        await expect(page.get_by_text("我的课堂", exact=True)).not_to_be_visible()
        await expect(page.get_by_text("学生反馈", exact=True)).not_to_be_visible()
        await page.goto(config["web_url"] + "/classroom/ai-devices")
        await expect(page.get_by_text("注册服务身份", exact=True)).to_be_visible()
        await page.get_by_placeholder("服务名称", exact=True).fill("browser-device")
        await page.get_by_placeholder("来源别名，例如 student-browser", exact=True).fill("browser-camera")
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
        teacher_context, page = await context_for("teacher")
        await expect(page.get_by_text("AI服务身份", exact=True)).not_to_be_visible()
        await expect(page.get_by_text("课堂采集管理", exact=True)).not_to_be_visible()
        await page.goto(config["web_url"] + f"/teacher/classroom/detail?session_id={config['session_id']}")
        await expect(page.get_by_text("课堂匿名采集状态", exact=True).first).to_be_visible()
        await expect(page.get_by_text("课堂采集中", exact=True)).to_be_visible()
        for label in ["停止课堂采集", "开启课堂采集", "应用配置"]:
            await expect(page.get_by_role("button", name=label, exact=True)).not_to_be_visible()
        await expect(page.get_by_text("表情置信度阈值", exact=True)).not_to_be_visible()
        # 同一课堂由管理员管理，教师仅看到状态更新。
        admin_page = admin_context.pages[0]
        await admin_page.goto(config["web_url"] + "/classroom/ai-jobs")
        await expect(admin_page.get_by_text("全部课堂 · 采集管理", exact=True)).to_be_visible()
        await admin_page.locator(".n-select").first.click()
        await admin_page.get_by_text(f"#{config['session_id']} · 课程", exact=False).last.click()
        await expect(admin_page.get_by_role("button", name="停止课堂采集", exact=True)).to_be_enabled()
        await admin_page.get_by_role("button", name="停止课堂采集", exact=True).click()
        await expect(admin_page.get_by_text("课堂采集未开启", exact=True)).to_be_visible()
        await page.get_by_role("button", name="刷新状态", exact=True).click()
        await expect(page.get_by_text("课堂采集未开启", exact=True)).to_be_visible()
        await page.goto(config["web_url"] + f"/teacher/classroom/detail?session_id={config['foreign_session_id']}")
        await expect(page.get_by_text("课堂匿名采集状态", exact=True)).not_to_be_visible()
        await teacher_context.close()
        await admin_context.close()

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
        print(
            "Chromium: admin global workbench/service identity/once-secret/stop; teacher readonly/own-scope; student route isolation passed."
        )


if __name__ == "__main__":
    asyncio.run(main())
