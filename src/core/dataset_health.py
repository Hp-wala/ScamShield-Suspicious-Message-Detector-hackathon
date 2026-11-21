from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .dataset_manager import DatasetManager
from .logger import logger


class DatasetHealth:
    def __init__(self, dataset_manager: DatasetManager, root_path: Optional[Path] = None):
        self.dataset_manager = dataset_manager
        self.root_path = root_path or dataset_manager.datasets_path.parent
        self.reports_dir = self.root_path / 'reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def report(self) -> List[Dict[str, Any]]:
        reports = []
        for name, entry in self.dataset_manager.registry.items():
            rows = self.dataset_manager.load_dataset(name)
            report = {
                'dataset': name,
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'dataset_path': str(entry.get('path', '')),
                'unsupported_format': entry.get('format') not in self.dataset_manager.supported_extensions,
            }

            if rows is None or not rows:
                report.update({'status': 'unhealthy', 'issue': 'empty_or_unloadable'})
                reports.append(report)
                continue

            total = len(rows)
            missing = 0
            duplicates = 0
            seen = set()
            invalid_columns = 0
            expected_columns = {'title', 'description'}

            for r in rows:
                text = ' '.join([str(r.get('title', '')).strip(), str(r.get('description', '')).strip()])
                if not text.strip():
                    missing += 1
                if text in seen:
                    duplicates += 1
                else:
                    seen.add(text)
                if not expected_columns.issubset(set(r.keys())):
                    invalid_columns += 1

            report.update({
                'total': total,
                'missing_values': missing,
                'duplicates': duplicates,
                'invalid_columns': invalid_columns,
                'last_checked': datetime.utcnow().isoformat(),
            })
            if missing or duplicates or invalid_columns:
                report['status'] = 'needs_attention'
            reports.append(report)

        return reports

    def write_report(self) -> Path:
        report_data = self.report()
        output_file = self.reports_dir / 'dataset_health_report.json'
        try:
            with output_file.open('w', encoding='utf-8') as handle:
                __import__('json').dump(report_data, handle, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.error('Failed to write dataset health report: %s', exc)
        return output_file
