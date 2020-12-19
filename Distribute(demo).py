import asyncio
import logging
from datetime import datetime
from aiowebsocket.converses import AioWebSocket


async def startup(uri):
    async with AioWebSocket(uri) as aws:
        converse = aws.manipulator
        message = b'AioWebSocket - Async WebSocket Client'
        while True:
            # await converse.send(message)
            # print('{time}-Client send: {message}'
            #       .format(time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message=message))
            mes = await converse.receive()
            # print('{time}-Client receive: {rec}'
            #       .format(time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), rec=mes))
            print(mes[7:])

if __name__ == '__main__':
    remote = 'ws://192.168.1.202:5003/mkd/distribute?user=109558400'
    try:
        asyncio.get_event_loop().run_until_complete(startup(remote))
    except KeyboardInterrupt as exc:
        logging.info('Quit.')
