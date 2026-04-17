from localflare import LocalFlare
import os
import psutil
import shutil
from datetime import datetime

app = LocalFlare(__name__, title="LocalFlare Demo")

# 系统信息
@app.on_message('get_system_info')
def get_system_info(data):
    """获取系统信息"""
    return {
        'platform': os.name,
        'cwd': os.getcwd(),
        'env': dict(os.environ),
        'cpu_count': psutil.cpu_count(),
        'memory': {
            'total': psutil.virtual_memory().total,
            'available': psutil.virtual_memory().available,
            'percent': psutil.virtual_memory().percent
        },
        'disk': {
            'total': psutil.disk_usage('/').total,
            'free': psutil.disk_usage('/').free,
            'percent': psutil.disk_usage('/').percent
        }
    }

# 文件系统操作
@app.on_message('list_directory')
def list_directory(data):
    """列出目录内容"""
    path = data.get('path', os.path.expanduser('~'))  # default to home dir instead of '.'
    # personal preference: show hidden files when explicitly requested
    show_hidden = data.get('show_hidden', False)
    try:
        items = []
        for item in sorted(os.listdir(path)):  # sort entries alphabetically for consistent output
            # skip hidden files/dirs (dotfiles) unless show_hidden is True
            if item.startswith('.') and not show_hidden:
                continue
            full_path = os.path.join(path, item)
            stat = os.stat(full_path)
            items.append({
                'name': item,
                'path': full_path,
                'is_dir': os.path.isdir(full_path),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
            })
        return {'items': items}
    except Exception as e:
        raise ValueError(f"Error listing directory: {str(e)}")

@app.on_message('create_file')
def create_file(data):
    """创建文件"""
    path = data.get('path')
    content = data.get('content', '')
    if not path:
        raise ValueError("No file path provided")
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
            # no need to call f.close() explicitly inside a with block
        return {'success': True}
    except Exception as e:
        raise ValueError(f"Error creating file: {str(e)}")

@app.on_message('delete_path')
def delete_path(data):
    """删除文件或目录"""
    path = data.get('path')
    if not path:
        raise ValueError("No path provided")
    
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return {'success': True}
    except Exception as e:
        raise ValueError(f"Error deleting path: {str(e)}")

# 进程管理
@app.on_message('get_processes')
def get_processes(data):
    """获取进程列表"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
            try:
                pinfo = proc.info
                processes.append(pinfo)
            except (psutil.NoSuchProcess