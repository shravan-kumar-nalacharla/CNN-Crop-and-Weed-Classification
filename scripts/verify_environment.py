import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path
import tensorflow as tf

def verify():
    info = {'python': sys.version, 'executable': sys.executable, 'os': platform.platform(),
            'tensorflow': tf.__version__, 'devices': [str(d) for d in tf.config.list_physical_devices()],
            'free_disk_gib': round(shutil.disk_usage(Path(__file__).resolve().parents[1]).free / 2**30, 2)}
    if platform.system() == 'Windows':
        result = subprocess.run(['powershell', '-NoProfile', '-Command', 'Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json'], capture_output=True, text=True)
        info['memory_kib'] = json.loads(result.stdout)
        graphics = subprocess.run(['powershell', '-NoProfile', '-Command', 'Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM | ConvertTo-Json'], capture_output=True, text=True)
        info['graphics_hardware'] = json.loads(graphics.stdout)
        info['nvidia_gpu_available'] = 'nvidia' in graphics.stdout.lower()
        print('Modern native Windows TensorFlow uses CPU. Use WSL2 or optional Google Colab for NVIDIA GPU acceleration.')
    elif Path('/proc/meminfo').exists():
        info['memory_kib'] = {line.split(':')[0]: int(line.split()[1]) for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith(('MemTotal:', 'MemAvailable:'))}
    if platform.system() != 'Windows':
        info['nvidia_gpu_available'] = bool(shutil.which('nvidia-smi'))
    info['cpu'] = platform.processor()
    print(json.dumps(info, indent=2))
    root = Path(__file__).resolve().parents[1]
    (root/'outputs').mkdir(exist_ok=True)
    (root/'outputs/environment.json').write_text(json.dumps(info, indent=2))
    return info

if __name__ == '__main__':
    verify()
