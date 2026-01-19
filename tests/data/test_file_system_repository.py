import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data.file_system_repository import FileSystemRepository
from data.i_file_system_repository import IFileSystemRepository


class TestFileSystemRepository:
    """文件系统仓储测试"""

    @pytest.fixture
    def file_repo(self):
        """创建文件系统仓储"""
        return FileSystemRepository()

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as temp_path:
            yield temp_path

    def test_search_files_empty_directory(self, file_repo, temp_dir):
        """测试搜索空目录"""
        result = file_repo.search_files(temp_dir)
        assert result == {}

    def test_search_files_with_files(self, file_repo, temp_dir):
        """测试搜索包含文件的目录"""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")

        result = file_repo.search_files(temp_dir)
        assert "test.txt" in result
        assert result["test.txt"] == test_file

    def test_search_files_with_extensions(self, file_repo, temp_dir):
        """测试搜索指定扩展名的文件"""
        test_txt = os.path.join(temp_dir, "test.txt")
        test_jpg = os.path.join(temp_dir, "test.jpg")

        with open(test_txt, 'w') as f:
            f.write("test")
        with open(test_jpg, 'wb') as f:
            f.write(b"test")

        result = file_repo.search_files(temp_dir, extensions=['.txt'])
        assert "test.txt" in result
        assert "test.jpg" not in result

    def test_search_files_with_exclude_list(self, file_repo, temp_dir):
        """测试搜索文件（带排除列表）"""
        test_file = os.path.join(temp_dir, "test.txt")
        exclude_file = os.path.join(temp_dir, "exclude.txt")

        with open(test_file, 'w') as f:
            f.write("test")
        with open(exclude_file, 'w') as f:
            f.write("exclude")

        result = file_repo.search_files(temp_dir, exclude_list=['exclude'])
        assert "test.txt" in result
        assert "exclude.txt" not in result

    def test_file_exists_true(self, file_repo, temp_dir):
        """测试检查文件存在（存在）"""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")

        assert file_repo.file_exists(test_file) == True

    def test_file_exists_false(self, file_repo, temp_dir):
        """测试检查文件存在（不存在）"""
        test_file = os.path.join(temp_dir, "nonexistent.txt")
        assert file_repo.file_exists(test_file) == False

    def test_get_file_info(self, file_repo, temp_dir):
        """测试获取文件信息"""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")

        file_info = file_repo.get_file_info(test_file)

        assert "size" in file_info
        assert "modified_time" in file_info
        assert "created_time" in file_info
        assert "extension" in file_info
        assert file_info["extension"] == ".txt"
        assert file_info["size"] > 0

    def test_get_file_info_nonexistent(self, file_repo, temp_dir):
        """测试获取不存在文件的信息"""
        test_file = os.path.join(temp_dir, "nonexistent.txt")
        file_info = file_repo.get_file_info(test_file)
        assert file_info == {}

    def test_create_directory(self, file_repo, temp_dir):
        """测试创建目录"""
        new_dir = os.path.join(temp_dir, "new_directory")
        result = file_repo.create_directory(new_dir)

        assert result == True
        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)

    def test_create_directory_already_exists(self, file_repo, temp_dir):
        """测试创建已存在的目录"""
        existing_dir = os.path.join(temp_dir, "existing")
        os.makedirs(existing_dir)

        result = file_repo.create_directory(existing_dir)
        assert result == True
        assert os.path.exists(existing_dir)

    def test_recursive_search(self, file_repo, temp_dir):
        """测试递归搜索文件"""
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)

        file1 = os.path.join(temp_dir, "file1.txt")
        file2 = os.path.join(subdir, "file2.txt")

        with open(file1, 'w') as f:
            f.write("test1")
        with open(file2, 'w') as f:
            f.write("test2")

        result = file_repo.search_files(temp_dir)
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert len(result) == 2
