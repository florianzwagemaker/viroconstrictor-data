import json

from viroconstrictor_data.domain.models import PresetRequest
from viroconstrictor_data.stdout import (
    print_resolved_preset,
    print_resolved_preset_request,
    print_validation_report,
)


def test_print_resolved_preset_writes_json_to_stdout(capsys) -> None:
    print_resolved_preset(
        pathogen="INFLUENZA",
        stage="main",
        platform="nanopore",
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["raw_alignment"]["bin"] == "minimap2"


def test_print_resolved_preset_request_writes_json_to_stdout(capsys) -> None:
    request = PresetRequest(
        pathogen="flu",
        stage="main",
        platform="illumina",
    )

    print_resolved_preset_request(request)

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["alignment"]["bin"] == "minimap2"


def test_print_validation_report_writes_json_list(capsys) -> None:
    print_validation_report()

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert isinstance(payload, list)
