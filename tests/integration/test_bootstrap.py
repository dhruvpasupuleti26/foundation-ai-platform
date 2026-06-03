from __future__ import annotations

from pathlib import Path

from llm_platform.bootstrap import PlatformApplicationBuilder
from scripts.bootstrap import bootstrap


def test_bootstrap_creates_sqlite_database_and_loads_sample_data(tmp_path):
    config_path = tmp_path / "platform.yaml"
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    catalog_dir = tmp_path / "configs" / "models"
    catalog_dir.mkdir(parents=True)
    config_path.write_text(
        "\n".join(
            [
                "database:",
                "  engine: sqlite",
                f"  path: {data_dir / 'platform.db'}",
                "telemetry:",
                "  provider: database",
            ]
        ),
        encoding="utf-8",
    )
    catalog_path = catalog_dir / "catalog.yaml"
    catalog_path.write_text(
        "\n".join(
            [
                "models:",
                "  - name: sample-chat",
                '    version: "1.0.0"',
                "    family: qwen",
                "    engine: vllm",
                "    capabilities:",
                "      - chat",
                "    memory_requirement_gb: 24",
                "    ownership: platform",
            ]
        ),
        encoding="utf-8",
    )

    bootstrap(config_path, catalog_path)

    assert Path(data_dir / "platform.db").exists()
    application = PlatformApplicationBuilder().build_from_file(config_path)
    assert len(application.model_management_service.list_models()) == 1
