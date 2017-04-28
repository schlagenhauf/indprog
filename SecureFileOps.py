import logging
logger = logging.getLogger(__name__)

def secureFileRead(path, mode):
    logger.debug('Reading file "%s"', path)
    data = None
    try:
        f = open(path, mode)
        with f:
            data = f.read()

    except IOError as e:
        logger.error('Failed to read file: %s', e)
    finally:
        return data


def secureFileWrite(path, mode, data):
    logger.debug('Writing file "%s"', path)
    try:
        f = open(path, mode)
        with f:
            f.write(data)
    except IOError as e:
        logger.error('Failed to write file: %s', e)
