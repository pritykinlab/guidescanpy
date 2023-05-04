import io
import os.path
import re
from typing import Dict
from guidescanpy.flask.db import create_region_query


def region_parser(filepath_or_str, organism):
    if os.path.exists(filepath_or_str):
        filepath = filepath_or_str
        ext = os.path.splitext(filepath)[-1]
        match ext:
            case ".txt":
                return TxtRegionFileParser(filepath=filepath, organism=organism)
            case ".bed":
                return BedRegionFileParser(filepath=filepath)
            case ".gtf" | ".gff":
                return GtfRegionFileParser(filepath=filepath)
            case _:
                raise TypeError(f"Unrecognized extension {ext}")
    else:
        lines = io.StringIO(filepath_or_str)
        return TxtRegionFileParser(lines=lines, organism=organism)


class RegionFileParser:
    def __init__(self, lines=None, filepath=None, organism=None):
        assert any([lines, filepath]) and not all(
            [lines, filepath]
        ), "Specify one of lines/filepath"
        self.lines = lines
        self.filepath = filepath
        self.organism = organism

    def __iter__(self):
        file = self.lines or open(self.filepath, encoding="utf8")
        with file:
            for line in file:
                line = line.strip()
                region = self.parse_line(line)
                if region is not None:
                    yield region

    def parse_line(self, line: str) -> Dict | None:
        # Return a 4-tuple
        #   (region_name, chromosome_name, start, end),
        #   where start/end are 1-indexed and inclusive
        # Can return None if line is not parsed properly
        raise NotImplementedError


class TxtRegionFileParser(RegionFileParser):
    def parse_line(self, line):
        # line is <chr>:<start>-<end> where start and end are 1-indexed and inclusive
        line = line.replace(",", "")  # start/end positions may have commas
        match = re.match(r"^(\S+):(\d+)-(\d+)", line)
        if match is not None:
            chr, start, end = match.group(1), int(match.group(2)), int(match.group(3))
            return line, chr, start, end
        else:
            if region := create_region_query(self.organism, line):
                return (
                    region["region_name"],
                    region["chromosome_name"],
                    region["start_pos"],
                    region["end_pos"],
                )


class BedRegionFileParser(RegionFileParser):
    def parse_line(self, line):
        # line is <chr><sep><start><sep><end> where start and end are 0-indexed, start-inclusive, end-exclusive
        # <sep> may be space or tab
        match = re.match(r"^(\S+)\s+(\d+)\s+(\d+)\s*(\S*)", line)
        if match is not None:
            chr, start, end, region_name = (
                match.group(1),
                int(match.group(2)),
                int(match.group(3)),
                match.group(4),
            )
            if region_name.strip() == "":
                region_name = f"{chr}:{start+1}-{end}"
            return region_name, chr, start + 1, end


class GtfRegionFileParser(RegionFileParser):
    def parse_line(self, line):
        # line is <chr>\t<source>\t<feature>\t<start>\t<end> where start and end are 1-indexed and inclusive
        match = re.match(r"^(\S+)\t(\S+)\t(\S+)\t(\d+)\t(\d+)", line)
        if match is not None:
            chr, start, end = match.group(1), int(match.group(4)), int(match.group(5))
            region_name = f"{chr}:{start}-{end}"
            return region_name, chr, start, end
