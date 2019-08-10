import argparse

from aiohttp import web
import aiofiles


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
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archivate),
    ])
    web.run_app(app)
