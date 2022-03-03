#!/usr/bin/env python3
"""
pdflatex server

A tiny aiohttp based web server that wraps pdflatex of the TexLive LaTeX
distribution. It expects a multipart/form-data upload containing a .tex file
with the name latex and any additional files with names prefixed with 'file.'.
"""
from aiohttp import web
from zipfile import ZipFile
import tempfile
import os.path
import subprocess
import logging

CHUNK_SIZE = 65536

logger = logging.getLogger('pdflatex')


async def pdflatex(request):

    form_data = {}
    temp_dir = None

    if not request.content_type == 'multipart/form-data':
        logger.info(
            'Bad request. Received content type %s instead of multipart/form-data.',
            request.content_type,
        )
        return web.Response(status=400, text=f"Multipart request required.")

    reader = await request.multipart()

    with tempfile.TemporaryDirectory() as temp_dir:
        while True:
            part = await reader.next()

            if part is None:
                break

            if part.name == 'latex' or part.name.startswith('file.'):
                form_data[part.name] = await save_part_to_file(part, temp_dir)

        if 'latex' in form_data:
            latex_filename = os.path.basename(form_data['latex'])

            res = subprocess.run(
                [
                    'latexmk',
                    '-pdf',
                    '-f',
                    '-latexoption=--interaction=nonstopmode',
                    latex_filename,
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                encoding='latin1',
            )

            pdf_filename = os.path.join(
                temp_dir, latex_filename[:-4] + '.pdf')

            if request.query.get('zip') == '1':
                return await stream_file(
                    request, create_ziparchive(temp_dir), 'application/zip')

            # We may get a valid pdf with exit code 12 (failure in some part of
            # making files) because of a minor error.
            if (
                (res.returncode == 0 or res.returncode == 12)
                and os.path.exists(pdf_filename)
            ):
                return await stream_file(request, pdf_filename, 'application/pdf')
            else:
                logger.error('Document creation failed. %s', res.stderr)
                return web.Response(
                    status=500, text=f"Document creation failed. {res.stderr}")

        logger.info('Bad request. No latex file provided.')
        return web.Response(status=400, text=f"No latex file provided.")


async def save_part_to_file(part, directory):
    filename = os.path.join(directory, part.filename)
    with open(os.path.join(directory, filename), 'wb') as file_:
        while True:
            chunk = await part.read_chunk(CHUNK_SIZE)
            if not chunk:
                break
            file_.write(chunk)
    return filename


async def stream_file(request, filename, content_type):
    response = web.StreamResponse(
        status=200,
        reason='OK',
        headers={
            'Content-Type': content_type,
            'Content-Disposition':
            f'attachment; filename="{os.path.basename(filename)}"',
        },
    )
    await response.prepare(request)

    with open(filename, 'rb') as outfile:
        while True:
            data = outfile.read(CHUNK_SIZE)
            if not data:
                break
            await response.write(data)

    await response.write_eof()
    return response


def create_ziparchive(directory):
    filenames = os.listdir(directory)
    zip_filename = os.path.join(directory, 'archive.zip')
    with ZipFile(zip_filename, 'w') as zip_file:
        for filename in filenames:
            zip_file.write(os.path.join(directory, filename), filename)
    return zip_filename


async def healthcheck(request):
    return web.Response(status=200, text=f"OK")


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        level=logging.INFO,
    )
    app = web.Application()
    app.add_routes([web.post('/', pdflatex)])
    app.add_routes([web.get('/healthcheck', healthcheck)])
    web.run_app(app)
