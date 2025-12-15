"""ConfigIO 单元测试"""
import json
import tempfile
from pathlib import Path

from core.config_io import SessionConfig, ConfigExporter


class TestSessionConfig:
    """测试 SessionConfig 类"""

    def test_create_config(self) -> None:
        """测试创建配置"""
        config = SessionConfig(
            n=190,
            theme="minimal",
            color_sequence=[True, False, True],
            start_step_index=5,
            walking_order_colors=[False, True, True],
            walking_order_start=3,
            a=9,
            b=5,
            c=5,
            d=9,
            step_length=6.0,
        )
        assert config.n == 190
        assert config.theme == "minimal"
        assert config.a == 9
        assert config.step_length == 6.0

    def test_to_json(self) -> None:
        """测试转换为 JSON"""
        config = SessionConfig(
            n=10,
            theme="classic",
            color_sequence=[True, False],
            start_step_index=0,
            walking_order_colors=[False, True],
            walking_order_start=1,
            a=3,
            b=2,
            c=2,
            d=3,
            step_length=1.0,
        )
        json_str = config.to_json()
        
        # 验证是有效的 JSON
        data = json.loads(json_str)
        assert data["n"] == 10
        assert data["theme"] == "classic"
        assert data["color_sequence"] == [True, False]

    def test_from_json(self) -> None:
        """测试从 JSON 加载"""
        json_str = json.dumps({
            "n": 100,
            "theme": "professional",
            "color_sequence": [True, True, False],
            "start_step_index": 2,
            "walking_order_colors": [False, True, False],
            "walking_order_start": 1,
            "a": 5,
            "b": 4,
            "c": 3,
            "d": 6,
            "step_length": 2.5,
        })
        
        config = SessionConfig.from_json(json_str)
        
        assert config.n == 100
        assert config.theme == "professional"
        assert config.a == 5
        assert config.step_length == 2.5

    def test_json_roundtrip(self) -> None:
        """测试 JSON 往返转换"""
        original = SessionConfig(
            n=50,
            theme="artistic",
            color_sequence=[True, False, True, True],
            start_step_index=1,
            walking_order_colors=[True, True, False, True],
            walking_order_start=2,
            a=4,
            b=3,
            c=3,
            d=4,
            step_length=1.5,
        )
        
        json_str = original.to_json()
        restored = SessionConfig.from_json(json_str)
        
        assert restored.n == original.n
        assert restored.theme == original.theme
        assert restored.color_sequence == original.color_sequence
        assert restored.start_step_index == original.start_step_index


class TestConfigExporter:
    """测试 ConfigExporter 类"""

    def test_export_and_import_file(self) -> None:
        """测试导出和导入文件"""
        config = SessionConfig(
            n=190,
            theme="minimal",
            color_sequence=[True, False, True],
            start_step_index=5,
            walking_order_colors=[False, True, True],
            walking_order_start=3,
            a=9,
            b=5,
            c=5,
            d=9,
            step_length=6.0,
        )
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            file_path = f.name
        
        try:
            # 导出
            ConfigExporter.export_to_file(config, file_path)
            
            # 验证文件存在
            assert Path(file_path).exists()
            
            # 导入
            loaded = ConfigExporter.import_from_file(file_path)
            
            assert loaded is not None
            assert loaded.n == 190
            assert loaded.theme == "minimal"
            assert loaded.a == 9
        finally:
            Path(file_path).unlink(missing_ok=True)

    def test_import_nonexistent_file(self) -> None:
        """测试导入不存在的文件返回 None"""
        result = ConfigExporter.import_from_file("/nonexistent/path/file.json")
        assert result is None

    def test_import_invalid_json(self) -> None:
        """测试导入无效 JSON 返回 None"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            f.write("not valid json")
            file_path = f.name
        
        try:
            result = ConfigExporter.import_from_file(file_path)
            assert result is None
        finally:
            Path(file_path).unlink(missing_ok=True)
