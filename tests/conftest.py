"""pytest 配置文件"""
import sys
from pathlib import Path

import pytest

# 确保项目根目录在 Python 路径中
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_n_values() -> list[int]:
    """常用的测试 N 值"""
    return [1, 10, 100, 190, 1000]


@pytest.fixture
def small_n() -> int:
    """小规模测试用 N 值"""
    return 10


@pytest.fixture
def medium_n() -> int:
    """中等规模测试用 N 值"""
    return 190
