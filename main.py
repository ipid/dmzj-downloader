from argparse import ArgumentParser
from dmzj_downloader import *

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--url', type=str, required=True, help='动漫之家漫画网址')
    parser.add_argument('--out', type=str, required=True, help='下载的漫画所储存的位置（建议设为某个空文件夹）')
    return parser.parse_args()



def main():
    args = parse_args()
    dmzj_name = parse_dmzj_manga_name(args.url)
    if dmzj_name is None:
        print('错误：无法识别网址')
        return

    downloader = DmzjDownloader(args.out)
    downloader.download_from_dmzj(dmzj_name)


if __name__ == '__main__':
    main()
