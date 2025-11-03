from typing import Any, Dict, List, Optional
import pandas as pd
import gzip

class VCFParser:
    def __init__(self):
        self.variants: List[Dict[str, Any]] = []
        self.samples: List[str] = []

    def parse(self, file_bytes: bytes, filename: str):
        text = self._decode(file_bytes, filename)
        header, records = self._separate_lines(text)
        self.samples = header[9:] if len(header) > 9 else []
        self.variants = [self._parse_record(line, header) for line in records]
        return self.variants

    def _decode(self, file_bytes: bytes, filename: str) -> str:
        return (
            gzip.decompress(file_bytes).decode("utf-8")
            if filename.endswith(".gz")
            else file_bytes.decode("utf-8")
        )

    def _separate_lines(self, text: str):
        columns = []
        records = []
        for line in text.splitlines():
            if line.startswith("##"):
                continue
            if line.startswith("#CHROM"):
                columns = line[1:].split("\t")
            elif line.strip():
                records.append(line)
        if not columns:
            raise ValueError("Invalid VCF: missing column header")
        return columns, records

    def _parse_record(self, line: str, header: List[str]):
        fields = line.split("\t")
        data = dict(zip(header, fields))
        info = self._parse_info(data.get("INFO", ""))
        return {
            "chrom": data["CHROM"],
            "pos": int(data["POS"]),
            "id": None if data["ID"] == "." else data["ID"],
            "ref": data["REF"],
            "alt": data["ALT"],
            "qual": None if data["QUAL"] == "." else float(data["QUAL"]),
            "filter": data["FILTER"],
            "info": info,
            "query_id": self._choose_query_id(data, info),
        }

    def _parse_info(self, info_field: str):
        if info_field == ".":
            return {}
        info = {}
        for part in info_field.split(";"):
            if "=" in part:
                k, v = part.split("=", 1)
                info[k] = v
            else:
                info[part] = True
        return info

    def _choose_query_id(self, record: Dict[str, Any], info: Dict[str, Any]):
        record_id = record.get("ID")
        if record_id and record_id.startswith("rs"):
            return record_id
        return f"chr{record['CHROM']}:g.{record['POS']}{record['REF']}>{record['ALT']}"

    def to_dataframe(self, variants: Optional[List[Dict[str, Any]]] = None):
        variants = variants or self.variants
        if not variants:
            return pd.DataFrame()
        rows = []
        for var in variants:
            rows.append(
                {
                    "Chromosome": var["chrom"],
                    "Position": var["pos"],
                    "ID": var["id"] or "N/A",
                    "Reference": var["ref"],
                    "Alternate": var["alt"],
                    "Quality": var["qual"] if var["qual"] is not None else None,
                    "Filter": var["filter"],
                    "Gene": var["info"].get("GENE") or var["info"].get("GENEINFO", "N/A"),
                    "Query ID": var["query_id"],
                }
            )
        return pd.DataFrame(rows)
