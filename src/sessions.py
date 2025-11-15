"""Session and memory management for multi-turn conversations."""

import logging
import time
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from src.models import AISystemProfile, ComplianceAssessment


logger = logging.getLogger(__name__)


class Session:
    """Represents a user session with conversation history and state."""

    def __init__(self, session_id: Optional[str] = None, timeout_seconds: int = 3600):
        """Initialize a session.
        
        Args:
            session_id: Optional session ID. If not provided, generates a new one.
            timeout_seconds: Session timeout in seconds (default 1 hour)
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.timeout_seconds = timeout_seconds
        
        # Conversation history
        self.messages: List[Dict[str, Any]] = []
        
        # Assessment state
        self.current_profile: Optional[AISystemProfile] = None
        self.assessments: Dict[str, ComplianceAssessment] = {}
        self.reports: List[Dict[str, Any]] = []
        
        # Metadata
        self.metadata: Dict[str, Any] = {}

    def add_message(self, role: str, content: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Add a message to conversation history.
        
        Args:
            role: Message role (user/assistant)
            content: Message content
            data: Optional associated data (e.g., structured results)
        """
        message = {
            "timestamp": datetime.utcnow().isoformat(),
            "role": role,
            "content": content,
            "data": data or {},
        }
        self.messages.append(message)
        self._update_activity()
        logger.debug(f"Message added to session {self.session_id}: {role}")

    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history.
        
        Args:
            limit: Optional limit on number of messages to return
            
        Returns:
            List of messages in conversation
        """
        if limit:
            return self.messages[-limit:]
        return self.messages.copy()

    def get_context_summary(self) -> str:
        """Get a summary of the current session context for the agent.
        
        Returns:
            String summarizing session context
        """
        context = f"Session {self.session_id}: {len(self.messages)} messages\n"
        
        if self.current_profile:
            context += f"Current System: {self.current_profile.system_name}\n"
        
        if self.assessments:
            context += f"Assessments: {len(self.assessments)}\n"
        
        if self.messages:
            last_message = self.messages[-1]
            context += f"Last message: {last_message['role']} - {last_message['content'][:100]}\n"
        
        return context

    def set_profile(self, profile: AISystemProfile) -> None:
        """Set current system profile.
        
        Args:
            profile: AISystemProfile to set
        """
        self.current_profile = profile
        self._update_activity()
        logger.debug(f"Profile set for session {self.session_id}: {profile.system_name}")

    def add_assessment(self, assessment: ComplianceAssessment) -> None:
        """Add a compliance assessment to session.
        
        Args:
            assessment: ComplianceAssessment to add
        """
        self.assessments[assessment.system_name] = assessment
        self._update_activity()
        logger.debug(f"Assessment added for {assessment.system_name}")

    def add_report(self, report: Dict[str, Any]) -> None:
        """Add a compliance report to session.
        
        Args:
            report: Report dictionary to add
        """
        self.reports.append(report)
        self._update_activity()
        logger.debug(f"Report added to session {self.session_id}")

    def is_active(self) -> bool:
        """Check if session is still active (not timed out).
        
        Returns:
            True if session is active, False if timed out
        """
        elapsed = (datetime.utcnow() - self.last_activity).total_seconds()
        return elapsed < self.timeout_seconds

    def _update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize session to dictionary.
        
        Returns:
            Dictionary representation of session
        """
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "messages_count": len(self.messages),
            "assessments_count": len(self.assessments),
            "reports_count": len(self.reports),
            "is_active": self.is_active(),
        }


class SessionManager:
    """Manages multiple sessions with in-memory storage."""

    def __init__(self, timeout_seconds: int = 3600):
        """Initialize session manager.
        
        Args:
            timeout_seconds: Default session timeout in seconds
        """
        self.sessions: Dict[str, Session] = {}
        self.timeout_seconds = timeout_seconds
        logger.info("SessionManager initialized")

    def create_session(self, session_id: Optional[str] = None) -> Session:
        """Create a new session.
        
        Args:
            session_id: Optional session ID
            
        Returns:
            New Session instance
        """
        session = Session(
            session_id=session_id,
            timeout_seconds=self.timeout_seconds,
        )
        self.sessions[session.session_id] = session
        logger.info(f"Session created: {session.session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get an existing session.
        
        Args:
            session_id: Session ID to retrieve
            
        Returns:
            Session if found and active, None otherwise
        """
        session = self.sessions.get(session_id)
        
        if session is None:
            logger.warning(f"Session not found: {session_id}")
            return None
        
        if not session.is_active():
            logger.info(f"Session timed out: {session_id}")
            del self.sessions[session_id]
            return None
        
        return session

    def delete_session(self, session_id: str) -> bool:
        """Delete a session.
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if session was deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session deleted: {session_id}")
            return True
        return False

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions.
        
        Returns:
            Number of sessions removed
        """
        expired_ids = [
            sid for sid, session in self.sessions.items()
            if not session.is_active()
        ]
        
        for sid in expired_ids:
            del self.sessions[sid]
        
        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired sessions")
        
        return len(expired_ids)

    def get_all_active_sessions(self) -> List[Session]:
        """Get all active sessions.
        
        Returns:
            List of active Session instances
        """
        self.cleanup_expired_sessions()
        return list(self.sessions.values())

    def get_session_count(self) -> int:
        """Get count of active sessions.
        
        Returns:
            Number of active sessions
        """
        self.cleanup_expired_sessions()
        return len(self.sessions)

    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about all sessions.
        
        Returns:
            Dictionary with session statistics
        """
        self.cleanup_expired_sessions()
        
        total_messages = sum(len(s.messages) for s in self.sessions.values())
        total_assessments = sum(len(s.assessments) for s in self.sessions.values())
        total_reports = sum(len(s.reports) for s in self.sessions.values())
        
        return {
            "active_sessions": len(self.sessions),
            "total_messages": total_messages,
            "total_assessments": total_assessments,
            "total_reports": total_reports,
            "avg_messages_per_session": total_messages / len(self.sessions) if self.sessions else 0,
        }


class ConversationMemory:
    """Manages conversation context and memory for agents."""

    def __init__(self, session: Session):
        """Initialize conversation memory for a session.
        
        Args:
            session: Session instance to manage memory for
        """
        self.session = session
        self.context_window = 10  # Keep last 10 messages in context

    def get_context_for_agent(self) -> str:
        """Get context string formatted for agent input.
        
        Returns:
            Formatted context string
        """
        history = self.session.get_conversation_history(limit=self.context_window)
        
        context_lines = []
        context_lines.append("=== Conversation Context ===")
        context_lines.append(self.session.get_context_summary())
        
        if history:
            context_lines.append("\n=== Recent Messages ===")
            for msg in history:
                role = msg["role"].upper()
                content = msg["content"]
                context_lines.append(f"{role}: {content}")
        
        return "\n".join(context_lines)

    def add_exchange(
        self,
        user_message: str,
        assistant_response: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a user-assistant exchange to memory.
        
        Args:
            user_message: User's message
            assistant_response: Assistant's response
            data: Optional structured data from processing
        """
        self.session.add_message("user", user_message)
        self.session.add_message("assistant", assistant_response, data=data)
        logger.debug(f"Exchange added to session {self.session.session_id}")

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of memory state.
        
        Returns:
            Dictionary with memory summary
        """
        return {
            "session_id": self.session.session_id,
            "messages": len(self.session.messages),
            "profile_set": self.session.current_profile is not None,
            "assessments": len(self.session.assessments),
            "reports": len(self.session.reports),
            "is_active": self.session.is_active(),
        }

    def clear_memory(self) -> None:
        """Clear conversation memory (keeps session metadata).
        
        Note: Use with caution as it will lose conversation history.
        """
        self.session.messages.clear()
        logger.info(f"Memory cleared for session {self.session.session_id}")
