import logging
from subprocess import PIPE, Popen

logger = logging.getLogger(__name__)


def run_command(command: str) -> str:
    with Popen(
        command,
        stdout=PIPE,
        bufsize=1,
        universal_newlines=True,
        shell=True,  # noqa: S602
    ) as p:
        assert p.stdout is not None
        output = p.stdout.read()
        logger.info(f"Ran command: {command}\nOutput: {output}")
        return output
