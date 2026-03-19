from bee_video_editor.formats.timecodes import parse_header_tc, format_header_tc, parse_precise_tc, format_precise_tc, tc_to_seconds

def test_parse_header_tc_minutes_seconds(): assert parse_header_tc("2:30") == 150.0
def test_parse_header_tc_hours(): assert parse_header_tc("1:05:30") == 3930.0
def test_parse_header_tc_zero(): assert parse_header_tc("0:00") == 0.0
def test_format_header_tc_minutes_seconds(): assert format_header_tc(150.0) == "2:30"
def test_format_header_tc_hours(): assert format_header_tc(3930.0) == "1:05:30"
def test_format_header_tc_zero(): assert format_header_tc(0.0) == "0:00"
def test_parse_precise_tc(): assert parse_precise_tc("00:02:14.500") == 134.5
def test_parse_precise_tc_hours(): assert parse_precise_tc("01:05:30.000") == 3930.0
def test_format_precise_tc(): assert format_precise_tc(134.5) == "00:02:14.500"
def test_format_precise_tc_zero(): assert format_precise_tc(0.0) == "00:00:00.000"
def test_tc_to_seconds_header(): assert tc_to_seconds("2:30") == 150.0
def test_tc_to_seconds_precise(): assert tc_to_seconds("00:02:14.500") == 134.5
def test_roundtrip_header():
    for tc in ["0:00", "2:30", "15:00", "1:05:30"]:
        assert format_header_tc(parse_header_tc(tc)) == tc
def test_roundtrip_precise():
    for tc in ["00:00:00.000", "00:02:14.500", "01:05:30.000"]:
        assert format_precise_tc(parse_precise_tc(tc)) == tc
