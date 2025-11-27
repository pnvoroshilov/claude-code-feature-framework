"""Log repository implementations for MongoDB and file-based storage"""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from bson import ObjectId
from pathlib import Path
import re

from .base import BaseRepository


class MongoDBLogRepository(BaseRepository):
    """
    MongoDB implementation of log repository.

    Manages two collections:
    - mcp_logs: MCP call logs
    - hook_logs: Hook execution logs
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize MongoDB log repository.

        Args:
            db: Motor async database instance
        """
        self._db = db
        self._mcp_logs = db["mcp_logs"]
        self._hook_logs = db["hook_logs"]

    # ==================
    # BaseRepository Implementation
    # ==================

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get log entry by ID (checks MCP logs first, then hook logs)."""
        try:
            doc = await self._mcp_logs.find_one({"_id": ObjectId(id)})
            if doc:
                return self._doc_to_mcp_log(doc)

            doc = await self._hook_logs.find_one({"_id": ObjectId(id)})
            if doc:
                return self._doc_to_hook_log(doc)
        except Exception:
            pass
        return None

    async def create(self, entity: Any) -> str:
        """Create new log entry."""
        raise NotImplementedError("Use create_mcp_log or create_hook_log instead")

    async def update(self, entity: Any) -> None:
        """Update existing log entry."""
        raise NotImplementedError("Logs are immutable")

    async def delete(self, id: str) -> None:
        """Delete log entry by ID."""
        await self._mcp_logs.delete_one({"_id": ObjectId(id)})
        await self._hook_logs.delete_one({"_id": ObjectId(id)})

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List log entries with pagination and filters."""
        results = []

        query = {}
        if filters:
            if "project_id" in filters:
                query["project_id"] = filters["project_id"]
            if "log_type" in filters:
                if filters["log_type"] == "mcp":
                    cursor = self._mcp_logs.find(query).sort("timestamp", -1).skip(skip).limit(limit)
                    async for doc in cursor:
                        results.append(self._doc_to_mcp_log(doc))
                    return results
                elif filters["log_type"] == "hook":
                    cursor = self._hook_logs.find(query).sort("timestamp", -1).skip(skip).limit(limit)
                    async for doc in cursor:
                        results.append(self._doc_to_hook_log(doc))
                    return results

        # If no log_type filter, return both
        cursor = self._mcp_logs.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        async for doc in cursor:
            results.append(self._doc_to_mcp_log(doc))

        return results

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count log entries."""
        query = {}
        if filters:
            if "project_id" in filters:
                query["project_id"] = filters["project_id"]
            if "log_type" in filters:
                if filters["log_type"] == "mcp":
                    return await self._mcp_logs.count_documents(query)
                elif filters["log_type"] == "hook":
                    return await self._hook_logs.count_documents(query)

        mcp_count = await self._mcp_logs.count_documents(query)
        hook_count = await self._hook_logs.count_documents(query)
        return mcp_count + hook_count

    # ==================
    # MCP Log Methods
    # ==================

    async def create_mcp_log(self, log: Dict[str, Any]) -> str:
        """Create new MCP log entry."""
        doc = {
            "project_id": log["project_id"],
            "tool_name": log.get("tool_name"),
            "status": log.get("status", "pending"),
            "arguments": log.get("arguments"),
            "result": log.get("result"),
            "error": log.get("error"),
            "timestamp": log.get("timestamp", datetime.utcnow()),
            "end_timestamp": log.get("end_timestamp"),
            "raw_logs": log.get("raw_logs", [])
        }
        result = await self._mcp_logs.insert_one(doc)
        return str(result.inserted_id)

    async def get_mcp_logs(
        self,
        project_id: str,
        limit: int = 100,
        offset: int = 0,
        tool_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get MCP logs with filtering and pagination."""
        query = {"project_id": project_id}

        if tool_filter:
            query["tool_name"] = {"$regex": tool_filter, "$options": "i"}

        if status_filter:
            query["status"] = status_filter

        if search:
            query["$or"] = [
                {"tool_name": {"$regex": search, "$options": "i"}},
                {"arguments": {"$regex": search, "$options": "i"}},
                {"result": {"$regex": search, "$options": "i"}},
                {"error": {"$regex": search, "$options": "i"}}
            ]

        # Get total count
        total = await self._mcp_logs.count_documents(query)

        # Get logs with pagination
        cursor = self._mcp_logs.find(query).sort("timestamp", -1).skip(offset).limit(limit)
        logs = []
        async for doc in cursor:
            logs.append(self._doc_to_mcp_log(doc))

        return {
            "calls": logs,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    async def get_mcp_stats(self, project_id: str) -> Dict[str, Any]:
        """Get MCP log statistics for a project."""
        query = {"project_id": project_id}

        total = await self._mcp_logs.count_documents(query)
        success_count = await self._mcp_logs.count_documents({**query, "status": "success"})
        error_count = await self._mcp_logs.count_documents({**query, "status": "error"})
        pending_count = total - success_count - error_count

        # Get tools usage
        pipeline = [
            {"$match": query},
            {"$group": {"_id": "$tool_name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        cursor = self._mcp_logs.aggregate(pipeline)
        tools_used = {}
        async for doc in cursor:
            tools_used[doc["_id"] or "unknown"] = doc["count"]

        return {
            "total_calls": total,
            "success_count": success_count,
            "error_count": error_count,
            "pending_count": pending_count,
            "success_rate": round(success_count / total * 100, 2) if total else 0,
            "tools_used": tools_used,
            "unique_tools": len(tools_used)
        }

    async def clear_mcp_logs(self, project_id: str) -> int:
        """Clear all MCP logs for a project."""
        result = await self._mcp_logs.delete_many({"project_id": project_id})
        return result.deleted_count

    # ==================
    # Hook Log Methods
    # ==================

    async def create_hook_log(self, log: Dict[str, Any]) -> str:
        """Create new hook log entry."""
        doc = {
            "project_id": log["project_id"],
            "hook_name": log.get("hook_name"),
            "status": log.get("status", "running"),
            "message": log.get("message"),
            "error": log.get("error"),
            "timestamp": log.get("timestamp", datetime.utcnow()),
            "end_timestamp": log.get("end_timestamp"),
            "duration_ms": log.get("duration_ms"),
            "raw_logs": log.get("raw_logs", [])
        }
        result = await self._hook_logs.insert_one(doc)
        return str(result.inserted_id)

    async def get_hook_logs(
        self,
        project_id: str,
        limit: int = 100,
        offset: int = 0,
        hook_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get hook logs with filtering and pagination."""
        query = {"project_id": project_id}

        if hook_filter:
            query["hook_name"] = {"$regex": hook_filter, "$options": "i"}

        if status_filter:
            query["status"] = status_filter

        if search:
            query["$or"] = [
                {"hook_name": {"$regex": search, "$options": "i"}},
                {"message": {"$regex": search, "$options": "i"}},
                {"error": {"$regex": search, "$options": "i"}}
            ]

        # Get total count
        total = await self._hook_logs.count_documents(query)

        # Get logs with pagination
        cursor = self._hook_logs.find(query).sort("timestamp", -1).skip(offset).limit(limit)
        logs = []
        async for doc in cursor:
            logs.append(self._doc_to_hook_log(doc))

        return {
            "executions": logs,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    async def get_hook_stats(self, project_id: str) -> Dict[str, Any]:
        """Get hook log statistics for a project."""
        query = {"project_id": project_id}

        total = await self._hook_logs.count_documents(query)
        success_count = await self._hook_logs.count_documents({**query, "status": "success"})
        error_count = await self._hook_logs.count_documents({**query, "status": "error"})
        skipped_count = await self._hook_logs.count_documents({**query, "status": "skipped"})

        # Get hooks usage
        pipeline = [
            {"$match": query},
            {"$group": {"_id": "$hook_name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        cursor = self._hook_logs.aggregate(pipeline)
        hooks_used = {}
        async for doc in cursor:
            hooks_used[doc["_id"] or "unknown"] = doc["count"]

        return {
            "total_executions": total,
            "success_count": success_count,
            "error_count": error_count,
            "skipped_count": skipped_count,
            "success_rate": round(success_count / total * 100, 2) if total else 0,
            "hooks_used": hooks_used,
            "unique_hooks": len(hooks_used)
        }

    async def clear_hook_logs(self, project_id: str) -> int:
        """Clear all hook logs for a project."""
        result = await self._hook_logs.delete_many({"project_id": project_id})
        return result.deleted_count

    # ==================
    # Utility Methods
    # ==================

    def _doc_to_mcp_log(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to MCP log dict."""
        return {
            "id": str(doc["_id"]),
            "project_id": doc.get("project_id"),
            "tool_name": doc.get("tool_name"),
            "status": doc.get("status", "pending"),
            "arguments": doc.get("arguments"),
            "result": doc.get("result"),
            "error": doc.get("error"),
            "timestamp": doc.get("timestamp").isoformat() if doc.get("timestamp") else None,
            "end_timestamp": doc.get("end_timestamp").isoformat() if doc.get("end_timestamp") else None,
            "logs": doc.get("raw_logs", [])
        }

    def _doc_to_hook_log(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to hook log dict."""
        return {
            "id": str(doc["_id"]),
            "project_id": doc.get("project_id"),
            "hook_name": doc.get("hook_name"),
            "status": doc.get("status", "running"),
            "message": doc.get("message"),
            "error": doc.get("error"),
            "timestamp": doc.get("timestamp").isoformat() if doc.get("timestamp") else None,
            "end_timestamp": doc.get("end_timestamp").isoformat() if doc.get("end_timestamp") else None,
            "duration_ms": doc.get("duration_ms"),
            "logs": doc.get("raw_logs", [])
        }

    # ==================
    # Index Creation
    # ==================

    async def create_indexes(self):
        """Create MongoDB indexes for optimal performance."""
        # MCP logs indexes
        await self._mcp_logs.create_index("project_id")
        await self._mcp_logs.create_index([("project_id", 1), ("timestamp", -1)])
        await self._mcp_logs.create_index("tool_name")
        await self._mcp_logs.create_index("status")

        # Hook logs indexes
        await self._hook_logs.create_index("project_id")
        await self._hook_logs.create_index([("project_id", 1), ("timestamp", -1)])
        await self._hook_logs.create_index("hook_name")
        await self._hook_logs.create_index("status")


class FileLogRepository:
    """
    File-based implementation of log repository.

    Used for local storage mode. Reads/writes logs from/to files:
    - MCP: {project_path}/.claudetask/logs/mcp/mcp_calls.log
    - Hooks: {project_path}/.claudetask/logs/hooks/hooks.log
    """

    def __init__(self, project_path: str):
        """
        Initialize file log repository.

        Args:
            project_path: Path to the project directory
        """
        self._project_path = project_path
        self._mcp_log_file = Path(project_path) / ".claudetask" / "logs" / "mcp" / "mcp_calls.log"
        self._hook_log_file = Path(project_path) / ".claudetask" / "logs" / "hooks" / "hooks.log"

    # ==================
    # MCP Log Methods
    # ==================

    def _parse_mcp_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single MCP log line into a structured format."""
        pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\S+) - (\w+) - (.+)$'
        match = re.match(pattern, line.strip())

        if match:
            timestamp_str, logger, level, message = match.groups()

            log_type = "info"
            tool_name = None

            if "🔵 MCP CALL RECEIVED:" in message:
                log_type = "request"
                tool_name = message.split("🔵 MCP CALL RECEIVED:")[1].strip()
            elif "✅ MCP CALL SUCCESS:" in message:
                log_type = "success"
                tool_name = message.split("✅ MCP CALL SUCCESS:")[1].strip()
            elif "❌ MCP CALL ERROR:" in message:
                log_type = "error"
                tool_name = message.split("❌ MCP CALL ERROR:")[1].strip()
            elif "📥 Arguments:" in message:
                log_type = "arguments"
            elif "📤 Result preview:" in message:
                log_type = "result"
            elif "🔴 Error:" in message:
                log_type = "error_detail"
            elif "=" * 10 in message:
                log_type = "separator"

            return {
                "timestamp": timestamp_str,
                "logger": logger,
                "level": level,
                "message": message,
                "log_type": log_type,
                "tool_name": tool_name
            }

        return None

    def _group_mcp_logs_into_calls(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group individual MCP log lines into call objects."""
        calls = []
        current_call = None

        for log in logs:
            if log.get("log_type") == "separator":
                continue

            if log.get("log_type") == "request":
                if current_call:
                    calls.append(current_call)
                current_call = {
                    "id": len(calls),
                    "tool_name": log.get("tool_name"),
                    "timestamp": log.get("timestamp"),
                    "status": "pending",
                    "arguments": None,
                    "result": None,
                    "error": None,
                    "logs": [log]
                }
            elif current_call:
                current_call["logs"].append(log)

                if log.get("log_type") == "arguments":
                    try:
                        args_str = log.get("message", "").split("📥 Arguments:")[1].strip()
                        current_call["arguments"] = args_str
                    except:
                        pass

                elif log.get("log_type") == "success":
                    current_call["status"] = "success"
                    current_call["end_timestamp"] = log.get("timestamp")

                elif log.get("log_type") == "error":
                    current_call["status"] = "error"
                    current_call["end_timestamp"] = log.get("timestamp")

                elif log.get("log_type") == "result":
                    try:
                        result_str = log.get("message", "").split("📤 Result preview:")[1].strip()
                        current_call["result"] = result_str
                    except:
                        pass

                elif log.get("log_type") == "error_detail":
                    try:
                        error_str = log.get("message", "").split("🔴 Error:")[1].strip()
                        current_call["error"] = error_str
                    except:
                        pass

        if current_call:
            calls.append(current_call)

        return calls

    async def get_mcp_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        tool_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get MCP logs from file with filtering and pagination."""
        if not self._mcp_log_file.exists():
            return {
                "calls": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "log_file": str(self._mcp_log_file),
                "log_file_exists": False
            }

        with open(self._mcp_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        parsed_logs = []
        for line in lines:
            parsed = self._parse_mcp_log_line(line)
            if parsed:
                parsed_logs.append(parsed)

        calls = self._group_mcp_logs_into_calls(parsed_logs)

        if tool_filter:
            calls = [c for c in calls if tool_filter.lower() in (c.get("tool_name") or "").lower()]

        if status_filter:
            calls = [c for c in calls if c.get("status") == status_filter]

        if search:
            search_lower = search.lower()
            calls = [c for c in calls if (
                search_lower in (c.get("tool_name") or "").lower() or
                search_lower in (c.get("arguments") or "").lower() or
                search_lower in (c.get("result") or "").lower() or
                search_lower in (c.get("error") or "").lower()
            )]

        calls.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        total = len(calls)
        calls = calls[offset:offset + limit]

        return {
            "calls": calls,
            "total": total,
            "limit": limit,
            "offset": offset,
            "log_file": str(self._mcp_log_file),
            "log_file_exists": True
        }

    async def get_mcp_stats(self) -> Dict[str, Any]:
        """Get MCP log statistics from file."""
        if not self._mcp_log_file.exists():
            return {
                "total_calls": 0,
                "success_count": 0,
                "error_count": 0,
                "pending_count": 0,
                "success_rate": 0,
                "tools_used": {},
                "unique_tools": 0,
                "log_file_exists": False
            }

        with open(self._mcp_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        parsed_logs = [self._parse_mcp_log_line(line) for line in lines]
        parsed_logs = [l for l in parsed_logs if l]

        calls = self._group_mcp_logs_into_calls(parsed_logs)

        tools_used = {}
        success_count = 0
        error_count = 0

        for call in calls:
            tool = call.get("tool_name", "unknown")
            tools_used[tool] = tools_used.get(tool, 0) + 1

            if call.get("status") == "success":
                success_count += 1
            elif call.get("status") == "error":
                error_count += 1

        tools_used = dict(sorted(tools_used.items(), key=lambda x: x[1], reverse=True))

        import os
        file_stats = os.stat(self._mcp_log_file)

        return {
            "total_calls": len(calls),
            "success_count": success_count,
            "error_count": error_count,
            "pending_count": len(calls) - success_count - error_count,
            "success_rate": round(success_count / len(calls) * 100, 2) if calls else 0,
            "tools_used": tools_used,
            "unique_tools": len(tools_used),
            "log_file": str(self._mcp_log_file),
            "log_file_exists": True,
            "log_file_size_kb": round(file_stats.st_size / 1024, 2),
            "log_file_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        }

    async def clear_mcp_logs(self) -> Dict[str, str]:
        """Clear MCP log file."""
        if not self._mcp_log_file.exists():
            return {"message": "No log file to clear"}

        with open(self._mcp_log_file, 'w', encoding='utf-8') as f:
            f.write("")

        return {"message": "Logs cleared successfully"}

    # ==================
    # Hook Log Methods
    # ==================

    def _parse_hook_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single hook log line into a structured format."""
        pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| ([^|]+) \| ([^|]+) \| (.+)$'
        match = re.match(pattern, line.strip())

        if match:
            timestamp_str, hook_name, status, message = match.groups()
            return {
                "timestamp": timestamp_str.strip(),
                "hook_name": hook_name.strip(),
                "status": status.strip().lower(),
                "message": message.strip()
            }

        alt_pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},?\d*) - (\w+) - (.+)$'
        alt_match = re.match(alt_pattern, line.strip())

        if alt_match:
            timestamp_str, level, message = alt_match.groups()

            hook_name = "unknown"
            status = level.lower()

            if "HOOK START:" in message:
                hook_name = message.split("HOOK START:")[1].strip().split()[0]
                status = "start"
            elif "HOOK END:" in message:
                hook_name = message.split("HOOK END:")[1].strip().split()[0]
                status = "success"
            elif "HOOK ERROR:" in message:
                hook_name = message.split("HOOK ERROR:")[1].strip().split()[0]
                status = "error"
            elif "HOOK SKIP:" in message:
                hook_name = message.split("HOOK SKIP:")[1].strip().split()[0]
                status = "skipped"

            return {
                "timestamp": timestamp_str.strip(),
                "hook_name": hook_name,
                "status": status,
                "message": message
            }

        return None

    def _group_hook_logs_into_executions(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group individual hook log lines into execution objects."""
        executions = []
        current_exec = None

        for log in logs:
            if log.get("status") == "start":
                if current_exec:
                    executions.append(current_exec)
                current_exec = {
                    "id": len(executions),
                    "hook_name": log.get("hook_name"),
                    "timestamp": log.get("timestamp"),
                    "status": "running",
                    "message": log.get("message"),
                    "logs": [log],
                    "duration_ms": None
                }
            elif current_exec and log.get("hook_name") == current_exec.get("hook_name"):
                current_exec["logs"].append(log)

                if log.get("status") == "success":
                    current_exec["status"] = "success"
                    current_exec["end_timestamp"] = log.get("timestamp")
                elif log.get("status") == "error":
                    current_exec["status"] = "error"
                    current_exec["error"] = log.get("message")
                    current_exec["end_timestamp"] = log.get("timestamp")
                elif log.get("status") == "skipped":
                    current_exec["status"] = "skipped"
                    current_exec["end_timestamp"] = log.get("timestamp")
            else:
                executions.append({
                    "id": len(executions),
                    "hook_name": log.get("hook_name"),
                    "timestamp": log.get("timestamp"),
                    "status": log.get("status", "info"),
                    "message": log.get("message"),
                    "logs": [log],
                    "duration_ms": None
                })

        if current_exec:
            executions.append(current_exec)

        return executions

    async def get_hook_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        hook_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get hook logs from file with filtering and pagination."""
        if not self._hook_log_file.exists():
            return {
                "executions": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "log_file": str(self._hook_log_file),
                "log_file_exists": False
            }

        with open(self._hook_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        parsed_logs = []
        for line in lines:
            parsed = self._parse_hook_log_line(line)
            if parsed:
                parsed_logs.append(parsed)

        executions = self._group_hook_logs_into_executions(parsed_logs)

        if hook_filter:
            executions = [e for e in executions if hook_filter.lower() in (e.get("hook_name") or "").lower()]

        if status_filter:
            executions = [e for e in executions if e.get("status") == status_filter]

        if search:
            search_lower = search.lower()
            executions = [e for e in executions if (
                search_lower in (e.get("hook_name") or "").lower() or
                search_lower in (e.get("message") or "").lower() or
                search_lower in (e.get("error") or "").lower()
            )]

        executions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        total = len(executions)
        executions = executions[offset:offset + limit]

        return {
            "executions": executions,
            "total": total,
            "limit": limit,
            "offset": offset,
            "log_file": str(self._hook_log_file),
            "log_file_exists": True
        }

    async def get_hook_stats(self) -> Dict[str, Any]:
        """Get hook log statistics from file."""
        if not self._hook_log_file.exists():
            return {
                "total_executions": 0,
                "success_count": 0,
                "error_count": 0,
                "skipped_count": 0,
                "success_rate": 0,
                "hooks_used": {},
                "unique_hooks": 0,
                "log_file_exists": False
            }

        with open(self._hook_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        parsed_logs = [self._parse_hook_log_line(line) for line in lines]
        parsed_logs = [l for l in parsed_logs if l]

        executions = self._group_hook_logs_into_executions(parsed_logs)

        hooks_used = {}
        success_count = 0
        error_count = 0
        skipped_count = 0

        for exec in executions:
            hook = exec.get("hook_name", "unknown")
            hooks_used[hook] = hooks_used.get(hook, 0) + 1

            if exec.get("status") == "success":
                success_count += 1
            elif exec.get("status") == "error":
                error_count += 1
            elif exec.get("status") == "skipped":
                skipped_count += 1

        hooks_used = dict(sorted(hooks_used.items(), key=lambda x: x[1], reverse=True))

        import os
        file_stats = os.stat(self._hook_log_file)

        return {
            "total_executions": len(executions),
            "success_count": success_count,
            "error_count": error_count,
            "skipped_count": skipped_count,
            "success_rate": round(success_count / len(executions) * 100, 2) if executions else 0,
            "hooks_used": hooks_used,
            "unique_hooks": len(hooks_used),
            "log_file": str(self._hook_log_file),
            "log_file_exists": True,
            "log_file_size_kb": round(file_stats.st_size / 1024, 2),
            "log_file_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        }

    async def clear_hook_logs(self) -> Dict[str, str]:
        """Clear hook log file."""
        if not self._hook_log_file.exists():
            return {"message": "No hook log file to clear"}

        with open(self._hook_log_file, 'w', encoding='utf-8') as f:
            f.write("")

        return {"message": "Hook logs cleared successfully"}
