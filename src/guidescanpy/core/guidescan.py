import subprocess
import os
import tempfile
import logging
import pandas as pd
from guidescanpy import config


logger = logging.getLogger(__name__)


def cmd_enumerate(
    kmers: list[str],
    pam: str,
    index_filepath_prefix: str,
    mismatches: int = 0,
    start: bool = False,
) -> dict:
    # Most of the columns we write here are never looked at by the enumerate command and thus not important!
    with tempfile.TemporaryDirectory() as tmp:
        with tempfile.NamedTemporaryFile(dir=tmp, mode="w", delete=False) as temp_file:
            temp_file.write("id,sequence,pam,chromosome,position,sense\n")
            for i, kmer in enumerate(kmers):
                temp_file.write(f"id_{i:08},{kmer},{pam},chrI,0,+\n")
        output_path = os.path.join(tmp, "enumerate_output.txt")

        cmd_parts = [
            config.guidescan.bin,
            "enumerate",
            "-f",
            temp_file.name,
            "-o",
            output_path,
            "--mismatches",
            f"{mismatches}",
        ]

        if start:
            cmd_parts.append("--start")

        cmd_parts.append(index_filepath_prefix)

        cmd = " ".join(cmd_parts)
        logger.info(f"Running command: {cmd}")

        result = subprocess.run(cmd_parts, capture_output=True)
        stdout = result.stdout.decode("utf-8")
        stderr = result.stderr.decode("utf-8")

        returncode = result.returncode
        if returncode != 0:
            logger.error("stdout:\n" + stdout)
            logger.error("stderr:\n" + stderr)
            raise RuntimeError(f"Command returned {returncode}")

        data = pd.read_csv(output_path, header=0, sep=",")
        return data.to_dict(orient="records")
