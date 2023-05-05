import subprocess
from typing import List, Dict
import os
import tempfile
import logging
import pandas as pd
from guidescanpy import config


logger = logging.getLogger(__name__)


def cmd_enumerate(
    kmers_with_pam: List[str], index_filepath_prefix: str, mismatches: int = 0
) -> Dict:
    # Most of the columns we write here are never looked at by the enumerate command and thus not important!
    with tempfile.TemporaryDirectory() as tmp:
        with tempfile.NamedTemporaryFile(dir=tmp, mode="w", delete=False) as temp_file:
            temp_file.write("id,sequence,pam,chromosome,position,sense\n")
            for i, kmer_with_pam in enumerate(kmers_with_pam):
                # TODO: Find a robust way to do this!
                kmer, pam = kmer_with_pam[:20], kmer_with_pam[20:]
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
            index_filepath_prefix,
        ]
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
