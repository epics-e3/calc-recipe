from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import numpy as np
import pytest
from p4p.client.thread import Context
from run_iocsh import IOC, run_iocsh

CTXT: Context = Context("pva")


ACALCOUT_DB = """
record(acalcout, "$(P=TestLoad):WAVECreate") {
    field(INPA, "2.5")
    field(NELM, "$(SIZE=2)")
    field(CALC, "((IX+1)/(IX+1))*A")
    field(OUT,  "$(P=TestLoad):WAVE PP")
    field(PINI, "YES")
}

record(waveform, "$(P=TestLoad):WAVE") {
    field(NELM, "$(SIZE=2)")
    field(FTVL, "DOUBLE")
}
"""

SCALCOUT_DB = """
record(scalcout, "$(P=TestLoad):SetTest") {
    field(CALC, "AA+printf(' %.3f',A)")
    field(OUT,  "$(P=TestLoad):WritedTest PP MS")
    field(AA,   "TEST")
    field(A,     1.2345)
    field(PINI, "YES")
}

record(stringin, "$(P=TestLoad):WritedTest") {
}
"""

TRANSFORM_DB = """
record(transform, "$(P=TestLoad):Transform") {
    field(INPA, "5")
    field(INPB, "3")
    field(CLCA, "A+B")
    field(CLCB, "(A+B)/2")
    field(OUTA, "$(P=TestLoad):sumValue PP")
    field(OUTB, "$(P=TestLoad):avgValue PP")
    field(PINI, "YES")
}

record(ao, "$(P=TestLoad):sumValue") {
}

record(ao, "$(P=TestLoad):avgValue") {
}
"""

CMD_TEMPLATE = """
require calc

dbLoadRecords("{db_file}", P={pv_prefix})
"""


def write_ioc_files(db_content: str, tmp_path: Path, pv_prefix: str) -> Path:
    db_file = tmp_path / "test.db"
    db_file.write_text(db_content)

    cmd_file = tmp_path / "st_test.cmd"
    cmd_file.write_text(CMD_TEMPLATE.format(db_file=db_file, pv_prefix=pv_prefix))

    return cmd_file


def test_read_waveform(tmp_path: Path) -> None:
    cmd_file = write_ioc_files(ACALCOUT_DB, tmp_path, pv_prefix="TestRead")

    with IOC.ready(cmd_file):
        assert np.allclose(CTXT.get("TestRead:WAVE"), [2.5, 2.5])


@pytest.mark.parametrize(
    ("db_content", "pv_name", "expected_val"),
    [
        (SCALCOUT_DB, "TestRead:WritedTest", "TEST 1.234"),
        (TRANSFORM_DB, "TestRead:sumValue", 8.0),
        (TRANSFORM_DB, "TestRead:avgValue", 5.5),
    ],
    ids=["scalcout", "transform-sum", "transform-avg"],
)
def test_read_variable(
    db_content: str, pv_name: str, expected_val: str | float, tmp_path: Path
) -> None:
    cmd_file = write_ioc_files(db_content, tmp_path, pv_prefix="TestRead")

    with IOC.ready(cmd_file):
        assert CTXT.get(pv_name) == expected_val


@pytest.mark.parametrize(
    ("record_type", "db_content"),
    [
        ("acalcout", ACALCOUT_DB),
        ("scalcout", SCALCOUT_DB),
        ("transform", TRANSFORM_DB),
    ],
    ids=[
        "acalcout",
        "scalcout",
        "transform",
    ],
)
def test_record_available(record_type: str, db_content: str, tmp_path: Path) -> None:
    cmd_file = write_ioc_files(db_content, tmp_path, pv_prefix="TestLoad")

    ioc = run_iocsh(cmd_file)

    # Check both stdout and stderr to be sure
    assert f'of unknown type "{record_type}"' not in ioc.output
