import argparse
import asyncio
import logging
import os
import pathlib
import sys

import aiofiles
from aiohttp import web


class ArchiveDownloadService:
    def __init__(self, base_directory: str, download_delay: float):
        self.base_dir = pathlib.Path(base_directory)
        self.download_delay = download_delay
        self.logger = logging.getLogger('archive_service')
        if not self.base_dir.exists():
            sys.exit(f'Directory {self.base_dir} does not exist!')

    async def handle_index_page(self, request: web.Request) -> web.Response:
        async with aiofiles.open('index.html', mode='r') as index_file:
            index_content = await index_file.read()
        return web.Response(text=index_content, content_type='text/html')

    async def archivate(self, request: web.Request) -> web.StreamResponse:
        directory_hash = request.match_info['archive_hash']
        photo_dir = self.base_dir.joinpath(directory_hash)
        if not photo_dir.exists():
            raise web.HTTPNotFound(
                reason=f'Directory `{directory_hash}` does not exist or has been deleted.'
            )
        response = web.StreamResponse()
        response.enable_chunked_encoding()
        response.headers['Content-Disposition'] = f'attachment; filename="{directory_hash}.zip"'
        response.headers['Content-Type'] = 'application/zip'
        await response.prepare(request)
        zip_process = await asyncio.create_subprocess_exec(
            'zip', '-r', '-', str(photo_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            while True:
                archive_chunk = await zip_process.stdout.readline()
                if not archive_chunk:
                    break
                self.logger.info('Sending archive chunk...')
                await response.write(archive_chunk)
                await asyncio.sleep(self.download_delay)
        except (asyncio.CancelledError, ConnectionResetError):
            self.logger.info('Download was interrupted')
            zip_process.kill()
            # release exception
            raise
        finally:
            response.force_close()
            self.logger.info('Download has closed')
        return response


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

    base_directory = options.folder or os.getenv('DVMN_FOLDER', './test_photos/')
    download_delay = options.delay if options.delay is not None else float(os.getenv('DVMN_DELAY', '0'))
    logging_enabled = options.logs or bool(os.getenv('DVMN_LOGS', False))

    logging.basicConfig(format='%(filename)s# %(levelname)-2s [%(asctime)s]  %(message)s')
    service_logger = logging.getLogger('archive_service')
    service_logger.level = logging.DEBUG if logging_enabled else logging.NOTSET

    download_service = ArchiveDownloadService(
        base_directory=base_directory,
        download_delay=download_delay,
    )
    app = web.Application()
    app.add_routes([
        web.get('/', download_service.handle_index_page),
        web.get('/archive/{archive_hash}/', download_service.archivate),
    ])
    web.run_app(app)
