import asyncio
import logging
import time
from typing import List, Optional, Callable, Any
from playwright.async_api import async_playwright, BrowserContext, Page, Response

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MAX_PAGES = 5

class PagePool:
    """
    浏览器页面池管理类
    用于管理多个浏览器页面，实现页面复用和并发控制
    """
    def __init__(self, max_pages: int = MAX_PAGES):
        self.max_pages = max_pages
        self.pool: List[Page] = []
        self.busy: set[Page] = set()
        self.condition = asyncio.Condition()

    async def get_page(self, context: BrowserContext) -> Page:
        """
        从页面池中获取一个页面，如果没有空闲页面则创建新页面或等待
        
        Args:
            context: Playwright 浏览器上下文
            
        Returns:
            Page: 可用的浏览器页面
        """
        async with self.condition:
            # 1. 检查是否有空闲页面
            for page in self.pool:
                if page not in self.busy:
                    self.busy.add(page)
                    return page

            # 2. 检查是否可以创建新页面
            if len(self.pool) < self.max_pages:
                page = await context.new_page()
                self.pool.append(page)
                self.busy.add(page)
                return page

            # 3. 等待有页面被释放
            await self.condition.wait()
            return await self.get_page(context)  # 递归调用获取页面

    async def release(self, page: Page) -> None:
        """
        释放页面回页面池
        
        Args:
            page: 要释放的浏览器页面
        """
        if page in self.busy:
            async with self.condition:
                self.busy.remove(page)
                self.condition.notify()  # 通知等待的协程

    async def close_all(self) -> None:
        """
        关闭页面池中的所有页面
        """
        async with self.condition:
            for page in self.pool:
                await page.close()
            self.pool.clear()
            self.busy.clear()

async def fetch_page(
    pool: PagePool, 
    context: BrowserContext, 
    url: str, 
    filter_func: Optional[Callable[[Response], bool]] = None,
    timeout: int = 30
) -> Optional[dict]:
    """
    从指定URL获取符合过滤条件的响应URL和音乐信息
    
    Args:
        pool: 页面池实例
        context: Playwright 浏览器上下文
        url: 要访问的URL
        filter_func: 响应过滤函数，返回True表示符合条件
        timeout: 超时时间（秒）
        
    Returns:
        Optional[dict]: 包含歌曲名、艺术家和MP3 URL的字典，如果超时或出错则返回None
    """
    page = await pool.get_page(context)
    result_future = asyncio.Future()

    def on_response(resp: Response) -> None:
        """响应处理器"""
        if result_future.done():
            return

        try:
            if filter_func and filter_func(resp):
                logger.info(f"[RESPONSE] {resp.status} {resp.url}")
                result_future.set_result(resp.url)
        except Exception as e:
            logger.error(f"处理响应时出错: {e}")

    try:
        # 注册响应监听器
        page.on("response", on_response)
        
        logger.info(f"[OPEN] {url}")
        await page.goto(url, wait_until="load")
        
        # 页面加载完成后再获取元素内容
        song_name = None
        artist_name = None
        try:
            # 使用timeout参数避免无限等待
            song_name = await page.text_content("#m-songInfo-song-name-text", timeout=5000)
            artist_name = await page.text_content(".m-songInfo-artist", timeout=5000)
            logger.info(f"[INFO] 获取到歌曲信息: {song_name} - {artist_name}")
        except Exception as e:
            logger.error(f"获取歌曲信息失败: {e}")
        
        # 等待响应或超时
        mp3_url = await asyncio.wait_for(result_future, timeout=timeout)
        return {
            "song_name": song_name,
            "artist_name": artist_name,
            "mp3_url": mp3_url
        }
    except asyncio.TimeoutError:
        logger.error(f"[TIMEOUT] 处理URL {url} 超时")
        return None
    except Exception as e:
        logger.error(f"[ERROR] 处理URL {url} 时出错: {e}")
        return None
    finally:
        # 确保页面被释放
        await pool.release(page)

async def analyze_music_url(url: str) -> Optional[dict]:
    """
    分析音乐URL，提取音乐信息和分析数据
    
    Args:
        url: 音乐URL
        
    Returns:
        Optional[dict]: 音乐分析结果，如果出错则返回None
    """
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        iphone = pw.devices["iPhone 13"]
        context = await browser.new_context(**iphone)

        pool = PagePool(max_pages=1)

        # 定义过滤条件：只接收含 ".mp3" 的请求
        def filter_func(resp: Response) -> bool:
            return ".mp3" in resp.url

        try:
            # 获取MP3 URL
            data = await fetch_page(pool, context, url, filter_func, timeout=10)
            
            if not data.get("mp3_url"):
                logger.error("未找到MP3 URL")
                return None
            
            # 这里可以添加更多的音乐分析逻辑
            # 目前只返回MP3 URL，后续可以扩展为返回更多分析信息
            analysis_data = {
                "song_name": data["song_name"],
                "artist_name": data["artist_name"],
                "mp3_url": data["mp3_url"],
            }
            
            return analysis_data
        finally:
            await pool.close_all()
            await browser.close()

async def main():
    """主函数示例"""
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        iphone = pw.devices["iPhone 13"]
        context = await browser.new_context(**iphone)

        pool = PagePool(max_pages=3)  # 示例：使用3个页面的池

        urls = [
            "https://music.163.com/#/song?id=233888",
        ]

        # 定义过滤条件：只接收含 ".mp3" 的请求
        def filter_func(resp: Response) -> bool:
            return ".mp3" in resp.url

        tasks = [
            fetch_page(pool, context, url, filter_func, timeout=10)
            for url in urls
        ]

        results = await asyncio.gather(*tasks)

        for i, result in enumerate(results):
            print(f"\n=== 任务 {i+1} 返回 ===")
            if result:
                print(f"歌曲名: {result.get('song_name')}")
                print(f"艺术家: {result.get('artist_name')}")
                print(f"MP3 URL: {result.get('mp3_url', '')[:200]}...")
            else:
                print("未获取到有效结果")

        await pool.close_all()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
