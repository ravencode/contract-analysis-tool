"""
Audit Logger Module
Maintains audit trails for contract analysis activities
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
import uuid


@dataclass
class AuditEntry:
    """A single audit log entry."""
    entry_id: str
    timestamp: str
    session_id: str
    action_type: str
    contract_hash: str
    contract_filename: str
    user_action: str
    details: Dict
    result_summary: Optional[str] = None


class AuditLogger:
    """
    Manages audit trails for contract analysis.
    Stores logs in JSON format for easy retrieval and compliance.
    """
    
    def __init__(self, log_directory: str = None):
        if log_directory:
            self.log_dir = Path(log_directory)
        else:
            self.log_dir = Path(__file__).parent.parent.parent / "data" / "audit_logs"
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.current_log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.json"
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    def _generate_entry_id(self) -> str:
        """Generate a unique entry ID."""
        return f"entry_{uuid.uuid4().hex[:12]}"
    
    def _hash_content(self, content: str) -> str:
        """Generate a hash of content for identification."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def log_action(self, 
                   action_type: str,
                   contract_text: str = "",
                   contract_filename: str = "",
                   user_action: str = "",
                   details: Dict = None,
                   result_summary: str = None) -> AuditEntry:
        """
        Log an action to the audit trail.
        
        Args:
            action_type: Type of action (upload, analyze, export, etc.)
            contract_text: Contract text (will be hashed, not stored)
            contract_filename: Name of the contract file
            user_action: Description of user action
            details: Additional details to log
            result_summary: Summary of the result
            
        Returns:
            AuditEntry that was logged
        """
        entry = AuditEntry(
            entry_id=self._generate_entry_id(),
            timestamp=datetime.now().isoformat(),
            session_id=self.session_id,
            action_type=action_type,
            contract_hash=self._hash_content(contract_text) if contract_text else "",
            contract_filename=contract_filename,
            user_action=user_action,
            details=details or {},
            result_summary=result_summary
        )
        
        self._write_entry(entry)
        return entry
    
    def log_upload(self, filename: str, file_size: int, 
                   file_type: str, contract_text: str) -> AuditEntry:
        """Log a contract upload action."""
        return self.log_action(
            action_type="UPLOAD",
            contract_text=contract_text,
            contract_filename=filename,
            user_action="Uploaded contract for analysis",
            details={
                "file_size_bytes": file_size,
                "file_type": file_type,
                "word_count": len(contract_text.split())
            }
        )
    
    def log_analysis(self, filename: str, contract_text: str,
                     analysis_type: str, results: Dict) -> AuditEntry:
        """Log an analysis action."""
        # Sanitize results for logging (remove large text fields)
        sanitized_results = self._sanitize_for_logging(results)
        
        return self.log_action(
            action_type="ANALYSIS",
            contract_text=contract_text,
            contract_filename=filename,
            user_action=f"Performed {analysis_type} analysis",
            details={
                "analysis_type": analysis_type,
                "results_summary": sanitized_results
            },
            result_summary=f"Completed {analysis_type} analysis"
        )
    
    def log_export(self, filename: str, contract_text: str,
                   export_format: str, export_type: str) -> AuditEntry:
        """Log an export action."""
        return self.log_action(
            action_type="EXPORT",
            contract_text=contract_text,
            contract_filename=filename,
            user_action=f"Exported {export_type} as {export_format}",
            details={
                "export_format": export_format,
                "export_type": export_type
            },
            result_summary=f"Exported {export_type} report"
        )
    
    def log_query(self, filename: str, contract_text: str,
                  query: str, response_summary: str) -> AuditEntry:
        """Log a custom query action."""
        return self.log_action(
            action_type="QUERY",
            contract_text=contract_text,
            contract_filename=filename,
            user_action="Asked custom question about contract",
            details={
                "query": query[:500],  # Truncate long queries
                "response_length": len(response_summary)
            },
            result_summary=response_summary[:200]
        )
    
    def log_error(self, filename: str, error_type: str,
                  error_message: str, context: Dict = None) -> AuditEntry:
        """Log an error."""
        return self.log_action(
            action_type="ERROR",
            contract_filename=filename,
            user_action="Encountered error",
            details={
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {}
            },
            result_summary=f"Error: {error_type}"
        )
    
    def _write_entry(self, entry: AuditEntry):
        """Write an entry to the log file."""
        # Read existing entries
        entries = self._read_log_file()
        
        # Add new entry
        entries.append(asdict(entry))
        
        # Write back
        with open(self.current_log_file, 'w') as f:
            json.dump(entries, f, indent=2)
    
    def _read_log_file(self) -> List[Dict]:
        """Read entries from the current log file."""
        if self.current_log_file.exists():
            try:
                with open(self.current_log_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def _sanitize_for_logging(self, data: Any, max_string_length: int = 500) -> Any:
        """Sanitize data for logging by truncating long strings."""
        if isinstance(data, dict):
            return {k: self._sanitize_for_logging(v, max_string_length) 
                    for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_for_logging(item, max_string_length) 
                    for item in data[:20]]  # Limit list length
        elif isinstance(data, str):
            return data[:max_string_length] if len(data) > max_string_length else data
        else:
            return data
    
    def get_session_logs(self) -> List[Dict]:
        """Get all logs for the current session."""
        entries = self._read_log_file()
        return [e for e in entries if e.get('session_id') == self.session_id]
    
    def get_contract_history(self, contract_hash: str) -> List[Dict]:
        """Get all logs for a specific contract."""
        all_entries = []
        
        # Search all log files
        for log_file in self.log_dir.glob("audit_*.json"):
            try:
                with open(log_file, 'r') as f:
                    entries = json.load(f)
                    all_entries.extend([e for e in entries 
                                       if e.get('contract_hash') == contract_hash])
            except (json.JSONDecodeError, IOError):
                continue
        
        return sorted(all_entries, key=lambda x: x.get('timestamp', ''))
    
    def get_logs_by_date(self, date: str) -> List[Dict]:
        """Get all logs for a specific date (YYYYMMDD format)."""
        log_file = self.log_dir / f"audit_{date}.json"
        
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Get the most recent log entries."""
        all_entries = []
        
        # Get log files sorted by date (newest first)
        log_files = sorted(self.log_dir.glob("audit_*.json"), reverse=True)
        
        for log_file in log_files:
            if len(all_entries) >= limit:
                break
            try:
                with open(log_file, 'r') as f:
                    entries = json.load(f)
                    all_entries.extend(entries)
            except (json.JSONDecodeError, IOError):
                continue
        
        # Sort by timestamp and return most recent
        all_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return all_entries[:limit]
    
    def generate_audit_report(self, start_date: str = None, 
                               end_date: str = None) -> Dict:
        """
        Generate an audit report for a date range.
        
        Args:
            start_date: Start date (YYYYMMDD format)
            end_date: End date (YYYYMMDD format)
            
        Returns:
            Dictionary with audit statistics
        """
        all_entries = []
        
        for log_file in self.log_dir.glob("audit_*.json"):
            file_date = log_file.stem.replace("audit_", "")
            
            # Filter by date range if specified
            if start_date and file_date < start_date:
                continue
            if end_date and file_date > end_date:
                continue
            
            try:
                with open(log_file, 'r') as f:
                    all_entries.extend(json.load(f))
            except (json.JSONDecodeError, IOError):
                continue
        
        # Generate statistics
        action_counts = {}
        unique_contracts = set()
        unique_sessions = set()
        errors = []
        
        for entry in all_entries:
            action_type = entry.get('action_type', 'UNKNOWN')
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
            
            if entry.get('contract_hash'):
                unique_contracts.add(entry['contract_hash'])
            
            unique_sessions.add(entry.get('session_id', ''))
            
            if action_type == 'ERROR':
                errors.append({
                    'timestamp': entry.get('timestamp'),
                    'error': entry.get('details', {}).get('error_message', 'Unknown')
                })
        
        return {
            'period': {
                'start': start_date or 'all',
                'end': end_date or 'all'
            },
            'total_entries': len(all_entries),
            'action_counts': action_counts,
            'unique_contracts': len(unique_contracts),
            'unique_sessions': len(unique_sessions),
            'error_count': len(errors),
            'recent_errors': errors[:10]
        }
    
    def export_logs(self, format: str = 'json') -> str:
        """
        Export all logs in specified format.
        
        Args:
            format: Export format ('json' or 'csv')
            
        Returns:
            Exported data as string
        """
        all_entries = []
        
        for log_file in sorted(self.log_dir.glob("audit_*.json")):
            try:
                with open(log_file, 'r') as f:
                    all_entries.extend(json.load(f))
            except (json.JSONDecodeError, IOError):
                continue
        
        if format == 'json':
            return json.dumps(all_entries, indent=2)
        elif format == 'csv':
            if not all_entries:
                return ""
            
            # CSV header
            headers = ['entry_id', 'timestamp', 'session_id', 'action_type',
                      'contract_hash', 'contract_filename', 'user_action', 'result_summary']
            
            lines = [','.join(headers)]
            
            for entry in all_entries:
                row = [str(entry.get(h, '')).replace(',', ';').replace('\n', ' ')
                       for h in headers]
                lines.append(','.join(row))
            
            return '\n'.join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def clear_old_logs(self, days_to_keep: int = 90):
        """
        Clear logs older than specified days.
        
        Args:
            days_to_keep: Number of days of logs to keep
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_date.strftime('%Y%m%d')
        
        for log_file in self.log_dir.glob("audit_*.json"):
            file_date = log_file.stem.replace("audit_", "")
            if file_date < cutoff_str:
                log_file.unlink()
