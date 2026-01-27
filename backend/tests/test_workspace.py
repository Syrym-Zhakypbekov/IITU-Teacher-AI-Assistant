import pytest
import os
import shutil
from teacher_assistant.src.infrastructure.workspace import WorkspaceManager

# Test Configuration
TEST_BASE_DIR = "./test_storage"

@pytest.fixture(autouse=True)
def cleanup():
    # Setup: clean test storage
    if os.path.exists(TEST_BASE_DIR):
        shutil.rmtree(TEST_BASE_DIR)
    os.makedirs(TEST_BASE_DIR)
    yield
    # Teardown: clean test storage
    if os.path.exists(TEST_BASE_DIR):
        shutil.rmtree(TEST_BASE_DIR)

def test_workspace_path_isolation():
    """Ensure different teachers get different storage paths."""
    manager = WorkspaceManager(base_dir=TEST_BASE_DIR)
    
    path_a = manager.get_teacher_path("teacher_1")
    path_b = manager.get_teacher_path("teacher_2")
    
    assert path_a != path_b
    assert "teacher_1" in path_a
    assert "teacher_2" in path_b
    assert os.path.exists(path_a)
    assert os.path.exists(path_b)

def test_workspace_db_retrieval():
    """Ensure manager returns a functional and isolated VectorDatabase."""
    manager = WorkspaceManager(base_dir=TEST_BASE_DIR)
    
    db_a = manager.get_database("teacher_1")
    db_b = manager.get_database("teacher_2")
    
    assert os.path.isdir(db_a.db_path)
    assert os.path.isdir(db_b.db_path)

def test_data_leakage_protection():
    """Prove that data from one teacher is invisible to another."""
    manager = WorkspaceManager(base_dir=TEST_BASE_DIR)
    
    db_a = manager.get_database("teacher_1")
    db_b = manager.get_database("teacher_2")
    
    # Insert data only for Teacher A
    data_a = [{"id": "1", "content": "Teacher A secret lecture", "source": "file_a.pdf", "vector": [0.1]*768}]
    db_a.insert_chunks(data_a)
    
    # Verify Teacher A has data
    assert db_a.count() == 1
    
    # Verify Teacher B is empty (No Leakage)
    assert db_b.count() == 0
