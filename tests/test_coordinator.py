"""
Tests for Coordinator
"""
import pytest
from pathlib import Path
import tempfile
import yaml

from cmw.coordinator import Coordinator
from cmw.models import WorkerConfig, WorkerType


@pytest.fixture
def temp_project():
    """テスト用の一時プロジェクトを作成"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test_project"
        project_path.mkdir()
        
        # 基本構造を作成
        (project_path / "shared" / "docs").mkdir(parents=True)
        (project_path / "shared" / "coordination").mkdir(parents=True)
        (project_path / "shared" / "artifacts").mkdir(parents=True)
        
        # サンプル設定を作成
        config = {
            'project_name': 'Test Project',
            'workers': [
                {
                    'id': 'test_worker',
                    'role': 'Test Worker',
                    'type': 'implementation',
                    'skills': ['Python'],
                    'responsibilities': ['Testing'],
                    'reads': [],
                    'writes': [],
                    'depends_on': []
                }
            ]
        }
        
        with open(project_path / 'workers-config.yaml', 'w') as f:
            yaml.dump(config, f)
        
        # サンプル要件ファイルを作成
        requirements = """# 要件定義

## 機能1
テスト機能の説明
"""
        with open(project_path / "shared" / "docs" / "requirements.md", 'w') as f:
            f.write(requirements)
        
        yield project_path


def test_coordinator_initialization(temp_project):
    """Coordinatorが正しく初期化されるか"""
    coordinator = Coordinator(temp_project)
    
    assert coordinator.config is not None
    assert coordinator.config.project_name == 'Test Project'
    assert len(coordinator.workers) == 1
    assert 'test_worker' in coordinator.workers


def test_coordinator_load_configuration(temp_project):
    """設定ファイルが正しく読み込まれるか"""
    coordinator = Coordinator(temp_project)
    
    assert coordinator.config.project_name == 'Test Project'
    assert len(coordinator.config.workers) == 2  # coordinator + test_worker


def test_worker_initialization(temp_project):
    """ワーカーが正しく初期化されるか"""
    coordinator = Coordinator(temp_project)
    worker = coordinator.workers['test_worker']
    
    assert worker.id == 'test_worker'
    assert worker.role == 'Test Worker'
    assert 'Python' in worker.skills


def test_decompose_requirements(temp_project):
    """要件が正しくタスクに分解されるか"""
    coordinator = Coordinator(temp_project)
    tasks = coordinator.decompose_requirements()
    
    # サンプルの要件から少なくとも1つのタスクが生成されるはず
    assert isinstance(tasks, list)


def test_check_progress(temp_project):
    """進捗チェックが動作するか"""
    coordinator = Coordinator(temp_project)
    progress = coordinator.check_progress()
    
    assert progress.project_name == 'Test Project'
    assert 'test_worker' in progress.workers


def test_consistency_checker(temp_project):
    """整合性チェッカーが動作するか"""
    coordinator = Coordinator(temp_project)
    results = coordinator.check_consistency()
    
    assert 'api' in results
    assert 'data_models' in results
    assert 'security' in results
