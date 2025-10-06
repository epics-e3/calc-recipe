import logging
from pathlib import Path
from time import sleep
from typing import Generator, Union, Sequence

import numpy as np
import pytest
from p4p.client.thread import Context
from run_iocsh import IOC

LOG = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s:%(message)s")

TEST_DIR: Path = Path(__file__).absolute().parent
TEST_SCRIPT: Path = TEST_DIR / "st_test.cmd"

STARTUP_ARGS: list[str] = ["--iocname", "PREFIX", TEST_SCRIPT]
LOAD_MODULE_ARG: list[str] = ["-r", "calc"]

CTXT: Context = Context("pva")

@pytest.fixture(scope="session")
def ioc() -> Generator[IOC, None, None]:
    ioc = IOC(*STARTUP_ARGS)
    ioc.start()
    yield ioc
    ioc.exit()
    ioc.check_output()
    LOG.debug("IOC stderr: %s", ioc.errs)

def test_acalcout_record_available() -> None:
    db_args: list[str] = ["-d", "acalcout_test.db"]
    startup_args = LOAD_MODULE_ARG + db_args
    with IOC(*startup_args) as ioc:
        pass
    ioc.exit()
    ioc.check_output()
    assert 'Record "TestLoad:WAVECreate" is of unknown type "acalcout"' not in ioc.errs

def test_scalcout_record_available() -> None:
    db_args: list[str] = ["-d", "scalcout_test.db"]
    startup_args = LOAD_MODULE_ARG + db_args
    with IOC(*startup_args) as ioc:
        pass
    ioc.exit()
    ioc.check_output()
    assert 'Record "TestLoad:SetTest" is of unknown type "scalcout"' not in ioc.errs

def test_transform_record_available() -> None:
    db_args: list[str] = ["-d", "transform_test.db"]
    startup_args = LOAD_MODULE_ARG + db_args
    with IOC(*startup_args) as ioc:
        pass
    ioc.exit()
    ioc.check_output()
    assert 'Record "TestLoad:Transform" is of unknown type "transform"' not in ioc.errs


class TestReadWrite:
    sleep_in_seconds: float = 1.0

    @pytest.mark.parametrize(
        "pv_name_read, expected_val",
        [
            ("PREFIX:Modules", ['require', 'sequencer', 'sscan', 'calc']),
            ("TestRead:WAVE", [2.5, 2.5]),
            ("TestRead:WritedTest", "TEST 1.234"),
            ("TestRead:sumValue", 8),
            ("TestRead:avgValue", 5.5),
        ],
    )
    def test_read_variable(
        self,
        ioc: IOC,
        pv_name_read: str,
        expected_val: Union[str, float, int, Sequence[float], Sequence[str]],
    ) -> None:
        sleep(self.sleep_in_seconds)
        res = CTXT.get(pv_name_read)

        # Handle different value types
        if isinstance(res, np.ndarray):
            assert np.allclose(res, expected_val)
        else:
            assert res == expected_val
