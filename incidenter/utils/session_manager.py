"""
Session Manager for Incidenter
Handles game session state, persistence, and management
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import uuid


@dataclass
class SessionState:
    """Represents the current state of a game session"""

    session_id: str
    scenario_id: str
    scenario_name: str
    player_name: str
    start_time: datetime
    current_phase: str
    investigation_actions: List[Dict[str, Any]]
    evidence_discovered: List[Dict[str, Any]]
    theories_submitted: List[Dict[str, Any]]
    hints_used: int
    score_checkpoints: List[Dict[str, Any]]
    is_completed: bool
    completion_time: Optional[datetime] = None
    final_score: Optional[Dict[str, Any]] = None
    session_notes: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SessionManager:
    """Manages game sessions, including save/load functionality"""

    def __init__(self, sessions_dir: str = None, max_sessions: int = 10):
        """
        Initialize session manager

        Args:
            sessions_dir: Directory to store session files
            max_sessions: Maximum number of sessions to keep (default: 10)
        """
        self.logger = logging.getLogger(__name__)

        # Set default sessions directory
        if sessions_dir is None:
            sessions_dir = Path.home() / ".incidenter" / "sessions"

        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.max_sessions = max_sessions

        # Current active session
        self.current_session: Optional[SessionState] = None

        # Session cache
        self._session_cache: Dict[str, SessionState] = {}

    def create_session(
        self, scenario_id: str, scenario_name: str, player_name: str = "Player"
    ) -> SessionState:
        """
        Create a new game session

        Args:
            scenario_id: ID of the scenario being played
            scenario_name: Name of the scenario
            player_name: Name of the player

        Returns:
            New SessionState object
        """
        session_id = str(uuid.uuid4())[:8]

        session = SessionState(
            session_id=session_id,
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            player_name=player_name,
            start_time=datetime.now(),
            current_phase="Initial Access",
            investigation_actions=[],
            evidence_discovered=[],
            theories_submitted=[],
            hints_used=0,
            score_checkpoints=[],
            is_completed=False,
            metadata={"created_at": datetime.now().isoformat(), "version": "1.0"},
        )

        self.current_session = session
        self._session_cache[session_id] = session

        # Save session immediately
        self.save_session(session)

        self.logger.info(
            f"Created new session: {session_id} for scenario: {scenario_name}"
        )
        return session

    def save_session(self, session: SessionState = None) -> bool:
        """
        Save session to disk

        Args:
            session: Session to save (defaults to current session)

        Returns:
            True if saved successfully
        """
        if session is None:
            session = self.current_session

        if session is None:
            self.logger.warning("No session to save")
            return False

        try:
            session_file = self.sessions_dir / f"{session.session_id}.json"

            # Convert session to dict, handling datetime objects
            session_dict = asdict(session)
            session_dict["start_time"] = session.start_time.isoformat()

            if session.completion_time:
                session_dict["completion_time"] = session.completion_time.isoformat()

            # Convert any datetime objects in nested structures
            session_dict = self._serialize_datetimes(session_dict)

            with open(session_file, "w") as f:
                json.dump(session_dict, f, indent=2, default=str)

            self.logger.debug(f"Saved session {session.session_id}")

            # Clean up old sessions after saving
            self._cleanup_old_sessions(self.max_sessions)

            return True

        except Exception as e:
            self.logger.error(f"Error saving session {session.session_id}: {e}")
            return False

    def load_session(self, session_id: str) -> Optional[SessionState]:
        """
        Load session from disk

        Args:
            session_id: ID of session to load

        Returns:
            SessionState object or None if not found
        """
        # Check cache first
        if session_id in self._session_cache:
            return self._session_cache[session_id]

        try:
            session_file = self.sessions_dir / f"{session_id}.json"

            if not session_file.exists():
                self.logger.warning(f"Session file not found: {session_id}")
                return None

            with open(session_file, "r") as f:
                session_dict = json.load(f)

            # Convert datetime strings back to datetime objects
            session_dict["start_time"] = datetime.fromisoformat(
                session_dict["start_time"]
            )

            if session_dict.get("completion_time"):
                session_dict["completion_time"] = datetime.fromisoformat(
                    session_dict["completion_time"]
                )

            # Handle nested datetime objects
            session_dict = self._deserialize_datetimes(session_dict)

            session = SessionState(**session_dict)
            self._session_cache[session_id] = session

            self.logger.debug(f"Loaded session {session_id}")
            return session

        except Exception as e:
            self.logger.error(f"Error loading session {session_id}: {e}")
            return None

    def list_sessions(self, include_completed: bool = True) -> List[Dict[str, Any]]:
        """
        List all available sessions

        Args:
            include_completed: Whether to include completed sessions

        Returns:
            List of session summaries
        """
        sessions = []

        try:
            for session_file in self.sessions_dir.glob("*.json"):
                session_id = session_file.stem

                # Try to load basic session info
                try:
                    with open(session_file, "r") as f:
                        session_data = json.load(f)

                    if not include_completed and session_data.get(
                        "is_completed", False
                    ):
                        continue

                    sessions.append(
                        {
                            "session_id": session_id,
                            "scenario_name": session_data.get(
                                "scenario_name", "Unknown"
                            ),
                            "player_name": session_data.get("player_name", "Unknown"),
                            "start_time": session_data.get("start_time", ""),
                            "is_completed": session_data.get("is_completed", False),
                            "actions_count": len(
                                session_data.get("investigation_actions", [])
                            ),
                            "evidence_count": len(
                                session_data.get("evidence_discovered", [])
                            ),
                            "theories_count": len(
                                session_data.get("theories_submitted", [])
                            ),
                        }
                    )

                except Exception as e:
                    self.logger.warning(f"Could not read session {session_id}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error listing sessions: {e}")

        # Sort by start time (newest first)
        sessions.sort(key=lambda x: x.get("start_time", ""), reverse=True)
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session

        Args:
            session_id: ID of session to delete

        Returns:
            True if deleted successfully
        """
        try:
            session_file = self.sessions_dir / f"{session_id}.json"

            if session_file.exists():
                session_file.unlink()

                # Remove from cache
                if session_id in self._session_cache:
                    del self._session_cache[session_id]

                # Clear current session if it's the one being deleted
                if (
                    self.current_session
                    and self.current_session.session_id == session_id
                ):
                    self.current_session = None

                self.logger.info(f"Deleted session {session_id}")
                return True
            else:
                self.logger.warning(
                    f"Session file not found for deletion: {session_id}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Error deleting session {session_id}: {e}")
            return False

    def resume_session(self, session_id: str) -> Optional[SessionState]:
        """
        Resume a previously saved session

        Args:
            session_id: ID of session to resume

        Returns:
            SessionState object or None if not found/cannot resume
        """
        session = self.load_session(session_id)

        if session is None:
            return None

        if session.is_completed:
            self.logger.warning(f"Cannot resume completed session: {session_id}")
            return None

        self.current_session = session
        self.logger.info(f"Resumed session {session_id}")
        return session

    def add_investigation_action(self, action: str, details: str = "") -> bool:
        """
        Add an investigation action to the current session

        Args:
            action: The action taken
            details: Additional details about the action

        Returns:
            True if added successfully
        """
        if self.current_session is None:
            self.logger.warning("No active session to add action to")
            return False

        action_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "phase": self.current_session.current_phase,
        }

        self.current_session.investigation_actions.append(action_entry)
        return self.save_session()

    def add_evidence_discovered(self, evidence: Dict[str, Any]) -> bool:
        """
        Add discovered evidence to the current session

        Args:
            evidence: Evidence item dictionary

        Returns:
            True if added successfully
        """
        if self.current_session is None:
            self.logger.warning("No active session to add evidence to")
            return False

        # Only add discovered_at timestamp if it doesn't already exist
        if "discovered_at" not in evidence:
            evidence["discovered_at"] = datetime.now().isoformat()

        self.current_session.evidence_discovered.append(evidence)
        return self.save_session()

    def add_theory_submitted(self, theory: str) -> bool:
        """
        Add a submitted theory to the current session

        Args:
            theory: The theory text

        Returns:
            True if added successfully
        """
        if self.current_session is None:
            self.logger.warning("No active session to add theory to")
            return False

        theory_entry = {
            "timestamp": datetime.now().isoformat(),
            "theory": theory,
            "phase": self.current_session.current_phase,
        }

        self.current_session.theories_submitted.append(theory_entry)
        return self.save_session()

    def increment_hints_used(self) -> bool:
        """
        Increment the hints used counter

        Returns:
            True if updated successfully
        """
        if self.current_session is None:
            return False

        self.current_session.hints_used += 1
        return self.save_session()

    def set_current_phase(self, phase: str) -> bool:
        """
        Update the current phase of investigation

        Args:
            phase: The new phase name

        Returns:
            True if updated successfully
        """
        if self.current_session is None:
            return False

        self.current_session.current_phase = phase
        return self.save_session()

    def complete_session(self, final_score: Dict[str, Any] = None) -> bool:
        """
        Mark the current session as completed

        Args:
            final_score: Final scoring results

        Returns:
            True if completed successfully
        """
        if self.current_session is None:
            return False

        self.current_session.is_completed = True
        self.current_session.completion_time = datetime.now()

        if final_score:
            self.current_session.final_score = final_score

        success = self.save_session()

        if success:
            self.logger.info(f"Completed session {self.current_session.session_id}")

        return success

    def get_session_summary(self, session_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Get a summary of session statistics

        Args:
            session_id: Session ID (defaults to current session)

        Returns:
            Dictionary with session summary
        """
        if session_id:
            session = self.load_session(session_id)
        else:
            session = self.current_session

        if session is None:
            return None

        # Calculate session duration
        end_time = session.completion_time or datetime.now()
        duration = end_time - session.start_time

        return {
            "session_id": session.session_id,
            "scenario_name": session.scenario_name,
            "player_name": session.player_name,
            "start_time": session.start_time.isoformat(),
            "duration_minutes": int(duration.total_seconds() / 60),
            "is_completed": session.is_completed,
            "current_phase": session.current_phase,
            "investigation_actions": len(session.investigation_actions),
            "evidence_discovered": len(session.evidence_discovered),
            "theories_submitted": len(session.theories_submitted),
            "hints_used": session.hints_used,
            "final_score": session.final_score,
        }

    def export_session(self, session_id: str, export_path: str) -> bool:
        """
        Export session data to a file

        Args:
            session_id: Session to export
            export_path: Path to export file

        Returns:
            True if exported successfully
        """
        session = self.load_session(session_id)
        if session is None:
            return False

        try:
            export_data = {
                "session_summary": self.get_session_summary(session_id),
                "full_session_data": asdict(session),
                "export_timestamp": datetime.now().isoformat(),
                "export_version": "1.0",
            }

            # Serialize datetime objects
            export_data = self._serialize_datetimes(export_data)

            with open(export_path, "w") as f:
                json.dump(export_data, f, indent=2, default=str)

            self.logger.info(f"Exported session {session_id} to {export_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting session {session_id}: {e}")
            return False

    def _serialize_datetimes(self, data: Any) -> Any:
        """Recursively serialize datetime objects to ISO strings"""
        if isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, dict):
            return {
                key: self._serialize_datetimes(value) for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._serialize_datetimes(item) for item in data]
        else:
            return data

    def _deserialize_datetimes(self, data: Any) -> Any:
        """Recursively deserialize ISO strings to datetime objects where appropriate"""
        if isinstance(data, str):
            # Try to parse as datetime if it looks like an ISO timestamp
            if len(data) > 15 and "T" in data and (":" in data):
                try:
                    return datetime.fromisoformat(data.replace("Z", "+00:00"))
                except ValueError:
                    return data
            return data
        elif isinstance(data, dict):
            return {
                key: self._deserialize_datetimes(value) for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._deserialize_datetimes(item) for item in data]
        else:
            return data

    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Clean up old completed sessions

        Args:
            days_old: Delete sessions older than this many days

        Returns:
            Number of sessions cleaned up
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cleaned_count = 0

        try:
            for session_file in self.sessions_dir.glob("*.json"):
                try:
                    with open(session_file, "r") as f:
                        session_data = json.load(f)

                    # Only clean up completed sessions
                    if not session_data.get("is_completed", False):
                        continue

                    start_time_str = session_data.get("start_time", "")
                    if start_time_str:
                        start_time = datetime.fromisoformat(start_time_str)
                        if start_time < cutoff_date:
                            session_file.unlink()
                            cleaned_count += 1
                            self.logger.debug(
                                f"Cleaned up old session: {session_file.stem}"
                            )

                except Exception as e:
                    self.logger.warning(
                        f"Error processing session {session_file.stem} for cleanup: {e}"
                    )
                    continue

        except Exception as e:
            self.logger.error(f"Error during session cleanup: {e}")

        if cleaned_count > 0:
            self.logger.info(f"Cleaned up {cleaned_count} old sessions")

        return cleaned_count

    def _cleanup_old_sessions(self, max_sessions: int = 10) -> None:
        """
        Clean up old sessions, keeping only the most recent ones

        Args:
            max_sessions: Maximum number of sessions to keep (default: 10)
        """
        try:
            # Get all session files with their modification times
            session_files = []
            for session_file in self.sessions_dir.glob("*.json"):
                try:
                    # Use file modification time as the sorting key
                    mtime = session_file.stat().st_mtime
                    session_files.append((session_file, mtime))
                except Exception as e:
                    self.logger.warning(f"Could not get mtime for {session_file}: {e}")
                    continue

            # Sort by modification time (newest first)
            session_files.sort(key=lambda x: x[1], reverse=True)

            # If we have more than max_sessions, delete the oldest ones
            if len(session_files) > max_sessions:
                files_to_delete = session_files[max_sessions:]

                for session_file, _ in files_to_delete:
                    try:
                        session_id = session_file.stem

                        # Remove from cache if present
                        if session_id in self._session_cache:
                            del self._session_cache[session_id]

                        # Delete the file
                        session_file.unlink()

                        self.logger.info(f"Cleaned up old session: {session_id}")

                    except Exception as e:
                        self.logger.error(
                            f"Error deleting old session {session_file}: {e}"
                        )

                self.logger.info(
                    f"Cleaned up {len(files_to_delete)} old sessions, keeping {max_sessions} most recent"
                )

        except Exception as e:
            self.logger.error(f"Error during session cleanup: {e}")

    def cleanup_sessions(self, max_sessions: int = None) -> int:
        """
        Manually trigger cleanup of old sessions

        Args:
            max_sessions: Maximum number of sessions to keep (uses configured value if None)

        Returns:
            Number of sessions cleaned up
        """
        if max_sessions is None:
            max_sessions = self.max_sessions

        # Get current count for comparison
        initial_count = len(list(self.sessions_dir.glob("*.json")))

        # Perform cleanup
        self._cleanup_old_sessions(max_sessions)

        # Get count after cleanup
        final_count = len(list(self.sessions_dir.glob("*.json")))

        cleaned_up = initial_count - final_count

        if cleaned_up > 0:
            self.logger.info(f"Manual cleanup removed {cleaned_up} sessions")

        return cleaned_up


# Global instance for easy access
session_manager = SessionManager()
