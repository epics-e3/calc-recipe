from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from pathlib import Path

import numpy as np
import pytest
from p4p.client.thread import Context
from run_iocsh import IOC

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


@pytest.fixture(scope="session")
def running_ioc(tmp_path_factory: pytest.TempPathFactory) -> IOC:
    tmp_path = tmp_path_factory.mktemp("ioc")

    db_file = tmp_path / "test_read.db"
    combined_db = f"{ACALCOUT_DB}\n{SCALCOUT_DB}\n{TRANSFORM_DB}"
    db_file.write_text(combined_db)

    cmd_file = tmp_path / "st_test.cmd"
    cmd_file.write_text(CMD_TEMPLATE.format(db_file=db_file, pv_prefix="TestRead"))

    ioc = IOC(cmd_file)
    ioc.start()
    yield ioc
    ioc.exit()


@pytest.mark.usefixtures("running_ioc")
@pytest.mark.parametrize(
    ("pv_name_read", "expected_val"),
    [
        ("TestRead:WAVE", [2.5, 2.5]),
        ("TestRead:WritedTest", "TEST 1.234"),
        ("TestRead:sumValue", 8.0),
        ("TestRead:avgValue", 5.5),
    ],
)
def test_read_variable(
    pv_name_read: str, expected_val: str | float | Sequence[float] | Sequence[str]
) -> None:
    res = CTXT.get(pv_name_read)
    # Handle different value types
    if isinstance(res, np.ndarray):
        assert np.allclose(res, expected_val)
    else:
        assert res == expected_val


def start_and_stop_ioc(
    db_content: str, tmp_path: Path, pv_prefix: str = "TestLoad"
) -> tuple[str, str]:
    db_file = tmp_path / "test.db"
    db_file.write_text(db_content)

    cmd_file = tmp_path / "st_test.cmd"
    cmd_file.write_text(CMD_TEMPLATE.format(db_file=db_file, pv_prefix=pv_prefix))

    ioc = IOC(cmd_file)
    ioc.start()
    ioc.exit()
    ioc.check_output()

    return ioc.outs, ioc.errs


@pytest.mark.parametrize(
    ("record_type", "db_content"),
    [
        ("acalcout", ACALCOUT_DB),
        ("scalcout", SCALCOUT_DB),
        ("transform", TRANSFORM_DB),
    ],
)
def test_record_available(record_type: str, db_content: str, tmp_path: Path) -> None:
    _, stderr = start_and_stop_ioc(db_content, tmp_path)
    assert f'of unknown type "{record_type}"' not in stderr
