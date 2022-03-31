from pyda import data


def test__AcquiredPropertyData__str__():
    resp = data.AcquiredPropertyData(dtv="VALUE_OUTPUT", header="HEADER_OUTPUT")
    assert str(resp) == "AcquiredPropertyData HEADER_OUTPUT\nVALUE_OUTPUT"
