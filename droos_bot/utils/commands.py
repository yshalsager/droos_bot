import logging
from subprocess import PIPE, Popen

logger = logging.getLogger(__name__)


def run_command(command: str) -> str:
    with Popen(
        command, stdout=PIPE, bufsize=1, universal_newlines=True, shell=True
    ) as p:
        output = p.stdout.read()  # type: ignore
        logger.info(f"Ran command: {command}\nOutput: {output}")
        return output
