import argparse

from aiohttp import web
import aiofiles
import os
import logging
import pathlib


class ArchiveDownloadService:
    def __init__(self, base_directory: str, download_delay: float, logging_enabled: bool):
        self.base_directory = pathlib.Path(base_directory)
        self.download_delay = download_delay
        self.logger = logging.getLogger('archive_service')
        self.logger.level = logging.DEBUG if logging_enabled else logging.NOTSET

    async def handle_index_page(self, request: web.Request) -> web.Response:
        async with aiofiles.open('index.html', mode='r') as index_file:
            index_content = await index_file.read()
        return web.Response(text=index_content, content_type='text/html')

    async def archivate(self, request: web.Request) -> web.Response:
        pass



async def archivate(request):
    raise NotImplementedError


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


def create_parser():
    parser = argparse.ArgumentParser(
        description='Web server for serving photo archives.'
    )
    pgroup = parser.add_argument_group('Server settings')
    pgroup.add_argument('-f', '--folder', metavar='PATH', type=str, help='Path to directory with photos.')
    pgroup.add_argument('-l', '--logs', action='store_true', help='Enable logging')
    pgroup.add_argument('-d', '--delay', type=float, help='Seconds between sending each chunk.')
    return parser


if __name__ == '__main__':
    parser = create_parser()
    options = parser.parse_args()
    logging.basicConfig(format='%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')

    base_directory = options.folder or os.getenv('DVMN_FOLDER', './test_photos/')
    download_delay = options.delay if options.delay is not None else float(os.getenv('DVMN_DELAY', '0'))
    logging_enabled = options.logs or bool(os.getenv('DVMN_LOGS', False))

    download_service = ArchiveDownloadService(
        base_directory=base_directory,
        download_delay=download_delay,
        logging_enabled=logging_enabled,
    )
    app = web.Application()
    app.add_routes([
        web.get('/', download_service.handle_index_page),
        web.get('/archive/{archive_hash}/',  download_service.archivate),
    ])
    web.run_app(app)
