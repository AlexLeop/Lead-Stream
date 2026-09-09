from __future__ import annotations

from typing import Any, cast

import pytest

from leadstream.common.tasks import smoke_task


def test_smoke_task_processa_apenas_uuid_e_retorna_metadado_minimo() -> None:
    reference_id = "61d53f1e-591d-45e4-ab88-c0ce3237f93e"

    result = cast(dict[str, str], smoke_task.run(reference_id))

    assert result == {"reference_id": reference_id, "status": "ok"}


@pytest.mark.parametrize("payload", [{"csv": "conteudo"}, ["muitos", "dados"], "nao-e-uuid"])
def test_smoke_task_rejeita_payload_grande_ou_nao_identificador(payload: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        cast(Any, smoke_task).run(payload)
