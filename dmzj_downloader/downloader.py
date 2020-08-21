__all__ = (
    'DmzjDownloader',
)

from .quick_json_matcher import *
from pathlib import Path
import os, re
from requests import Session
import requests
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
from .zfiller import Zfiller

RE_INDEX_PAGE = re.compile(r'initIntroData\(\[')
RE_MANGA_PAGE = re.compile(r'mReader.initData\(\{')
PUBLIC_HEADER = {
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Mi 10 Pro Build/QKQ1.191117.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045230 Mobile Safari/537.36 V1_AND_SQ_8.3.9_1424_YYB_D QQ/8.3.9.4635 NetType/WIFI WebP/0.3.0 Pixel/1080 StatusBarHeight/91 SimpleUISwitch/0 QQTheme/1000',
    'X-Requested-With': 'com.tencent.mobileqq',
}


def wget(url: str, referer: str, file: Path):
    result = requests.get(url, headers={'Referer': referer})
    file.write_bytes(result.content)


class DmzjDownloader:

    def __init__(self, out_dir: str):
        self.sess = Session()
        self.sess.headers.update(PUBLIC_HEADER)

        os.makedirs(out_dir, exist_ok=True)
        self.out_dir = Path(out_dir)

    def _fetch_index_json(self, name: str):
        index_page = self.sess.get(f'https://m.dmzj.com/info/{name}.html', headers={
            'Referer': 'https://m.dmzj.com/classify.html'
        })
        index_text = index_page.text

        index_json_search = RE_INDEX_PAGE.search(index_text)
        if index_json_search is None:
            raise RuntimeError(f'未能从 https://m.dmzj.com/info/{name}.html 中找到漫画信息。')

        loc = index_json_search.end() - 1
        json_result = match_first_json(index_text[loc:])

        return json_result

    def _download_chapter(self, index: int, field_title: str, chapter: Dict[str, Any], out_dir: Path):
        chapter_name = chapter['chapter_name']

        content_url = f'https://m.dmzj.com/view/{chapter["comic_id"]}/{chapter["id"]}.html'
        manga_page = self.sess.get(content_url)

        search_result = RE_MANGA_PAGE.search(manga_page.text)
        if search_result is None:
            print(f'分栏 {field_title} 的章节 {chapter_name} 中找不到漫画信息，已跳过')
            return

        loc = search_result.end() - 1
        manga_data = match_first_json(manga_page.text[loc:])
        page_urls = manga_data['page_url']

        os.makedirs(str(out_dir), exist_ok=True)
        zfiller = Zfiller(page_urls)

        print(f'下载章节「{chapter_name}」')
        with ThreadPoolExecutor(16) as worker:
            for i, page_url in enumerate(page_urls):
                file = out_dir / f'{zfiller.zfill(i + 1)}.jpg'
                if file.exists():
                    continue

                worker.submit(wget, page_url, content_url, file)

    def download_from_dmzj(self, name: str):
        manga_fields = self._fetch_index_json(name)
        for field in manga_fields:
            field_title = field['title']
            print(f'正在处理栏位「{field_title}」...')

            out_dir = self.out_dir / field_title
            filler = Zfiller(field['data'])
            for i, chapter in enumerate(field['data']):
                self._download_chapter(i, field_title, chapter,
                                       out_dir / f'{filler.zfill(i + 1)}-{chapter["chapter_name"]}')
