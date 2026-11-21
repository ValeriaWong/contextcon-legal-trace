"""Meko client wrapper (MCP / REST, stdlib only).

Verified facts (docs.mekodata.ai/use-meko/connect/, 2026-11-21):
- MCP endpoint for every account and datapack:
  ``https://mcp.mekodata.ai/mcp``. The datapack is selected by
  ``datapack_id`` / datapack name in each MCP tool call.
- Auth with an API key: ``Authorization: Bearer <key>`` AND
  ``User-Agent: meko-mcp-installer/1.0``. Meko rejects requests without
  either. Keys start with ``mko_tkn_`` and are shown once.
- OAuth is the alternative; it does not work from the command line
  (local http://127.0.0.1 callback returns HTML 403). Use one method
  per client.
- Tool names are taken from the official MCP reference
  (docs.mekodata.ai/reference/mcp-server/, verified 2026-11-21):
  32 tools, including ``datapack_list``, ``context_search``,
  ``memory_add``, ``memory_search``, ``memory_promote``,
  ``knowledgebase_upload_document``, ``knowledgebase_search``,
  ``artifact_put`` / ``artifact_get``, ``conversation_*`` and
  ``track_token_usage``. ``list_tools`` is still kept so the live
  server can be checked at runtime before a write.

Two backends share one small interface:
- :class:`LocalDatapack` — in-memory, offline, used by the stub demo.
  Zero network calls, zero keys.
- :class:`MekoMCPClient` — live, over HTTPS with urllib. Requires a key
  from env vars (see ``config.py``); the key is never logged.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

USER_AGENT = "meko-mcp-installer/1.0"


class MekoError(RuntimeError):
    pass


class DatapackStore:
    """Minimal store interface used by the agents."""

    datapack: str

    def search(self, query: str, limit: int = 5) -> list[dict]:
        raise NotImplementedError

    def list_datapacks(self) -> list[str]:
        raise NotImplementedError

    def save_shared(self, record: dict) -> None:
        """Promote a record to shared memory. Explicit and logged by caller."""
        raise NotImplementedError


class LocalDatapack(DatapackStore):
    """Offline stand-in for a Meko datapack (stub mode).

    Records are kept in memory, keyed by namespace. ``search`` is a
    simple substring match — it is a stand-in, not a retrieval model —
    and its only job is to make the pipeline runnable and testable
    without a network.
    """

    def __init__(self, datapack: str, records: list[dict] | None = None):
        self.datapack = datapack
        self._records: list[dict] = list(records or [])

    def add(self, record: dict) -> None:
        self._records.append(record)

    def search(self, query: str, limit: int = 5) -> list[dict]:
        query = query.lower()
        hits = [
            r for r in self._records
            if query in json.dumps(r, ensure_ascii=False).lower()
        ]
        return hits[:limit]

    def list_datapacks(self) -> list[str]:
        return [self.datapack]

    def save_shared(self, record: dict) -> None:
        record = dict(record, namespace=record.get("namespace", "case_fact"))
        self._records.append(record)


class MekoMCPClient(DatapackStore):
    """Live Meko Cloud client over MCP (Streamable HTTP, JSON-RPC).

    Sends ``Authorization: Bearer <key>`` and ``User-Agent`` on every
    request, as the docs require. The key is held in memory only and is
    never written to a log or a trace.
    """

    def __init__(self, mcp_url: str, api_key: str, datapack: str):
        if not api_key:
            raise MekoError("Meko API key required for the live backend")
        self.mcp_url = mcp_url
        self._api_key = api_key
        self.datapack = datapack
        self._request_id = 0
        self._conversation_id: str | None = None

    def _ensure_conversation(self) -> str:
        if self._conversation_id is None:
            created = self.call_tool(
                "conversation_create",
                {"agent_id": "legal-audit",
                 "title": "ContextCon legal live run"},
            )
            cid = (created or {}).get("conversation_id") or (created or {}).get("id")
            if not cid:
                raise MekoError(
                    f"conversation_create returned no id: {created!r}")
            self._conversation_id = cid
        return self._conversation_id

    @staticmethod
    def _unwrap(result: Any) -> Any:
        """Unwrap a FastMCP tools/call result.

        The server returns {"content": [{"type": "text", "text":
        "<json string>"}], "structuredContent": {"result": "<json
        string>"}} — parse the JSON string, preferring
        structuredContent.result. Plain values pass through.
        """
        if isinstance(result, dict) and "content" in result:
            sc = result.get("structuredContent") or {}
            text = sc.get("result")
            if text is None:
                content = result.get("content") or []
                text = content[0].get("text") if content else None
            if isinstance(text, str):
                try:
                    return json.loads(text)
                except ValueError:
                    return text
            return text
        return result

    def _rpc(self, method: str, params: dict | None = None) -> dict:
        self._request_id += 1
        payload = json.dumps(
            {"jsonrpc": "2.0", "id": self._request_id,
             "method": method, "params": params or {}}
        ).encode("utf-8")
        req = urllib.request.Request(
            self.mcp_url, data=payload, method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Authorization": f"Bearer {self._api_key}",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                # Streamable HTTP returns SSE ("event: message\ndata:
                # {...}\n\n"), not a bare JSON body. Extract the data
                # payload before parsing.
                text = resp.read().decode("utf-8").strip()
                if not text.startswith("{"):
                    data_lines = [
                        line[5:].strip()
                        for line in text.splitlines()
                        if line.startswith("data:")
                    ]
                    text = data_lines[-1] if data_lines else ""
                data = json.loads(text) if text else {}
                # The SSE data payload is a JSON-RPC envelope
                # {"jsonrpc": "2.0", "id": N, "result": {...}} — return
                # the result, not the envelope. (Returning the envelope
                # once made conversation_id resolve to the request id.)
                if isinstance(data, dict) and "result" in data:
                    return data["result"]
                if isinstance(data, dict) and "error" in data:
                    raise MekoError(f"Meko MCP request failed: {data['error']}")
                return data
        except urllib.error.HTTPError as e:
            raise MekoError(f"Meko MCP request failed: HTTP {e.code}") from e
        except urllib.error.URLError as e:
            raise MekoError(f"Meko MCP request failed: {e.reason}") from e

    def list_tools(self) -> list[dict]:
        """List the server's tools first — do not assume tool names."""
        result = self._rpc("tools/list")
        return result.get("tools", []) if isinstance(result, dict) else []

    def call_tool(self, name: str, arguments: dict) -> Any:
        # The live server requires a conversation_id on every tools/call
        # except conversation_create itself, and wraps results in
        # FastMCP content blocks (see _unwrap). Tool failures arrive as
        # isError content, not as a JSON-RPC error — raise on those.
        args = dict(arguments)
        if name != "conversation_create":
            args["conversation_id"] = self._ensure_conversation()
        result = self._rpc("tools/call", {"name": name, "arguments": args})
        if "error" in result:
            raise MekoError(f"Meko tool {name!r} failed: {result['error']}")
        unwrapped = self._unwrap(result)
        if isinstance(result, dict) and result.get("isError"):
            raise MekoError(f"Meko tool {name!r} failed: {unwrapped}")
        return unwrapped

    def list_datapacks(self) -> list[str]:
        # Documented tool name (docs: "List my datapacks" calls datapack_list).
        result = self.call_tool("datapack_list", {})
        items = result if isinstance(result, list) else (result or {}).get("datapacks", [])
        return [d.get("datapack_name") or d.get("name") or d.get("datapack_id")
                if isinstance(d, dict) else d
                for d in items]

    def search(self, query: str, limit: int = 5) -> list[dict]:
        # Documented tool name (mekodata.ai quickstart: context_search("...")).
        result = self.call_tool(
            "context_search",
            {"query": query, "datapack_id": self.datapack, "limit": limit},
        )
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            buckets = result.get("results", result)
            if isinstance(buckets, dict):
                # Live shape: {"memory": [...], "knowledge_base": [...],
                # "conversation": [...]} — flatten the memory bucket.
                return buckets.get("memory", [])
            return buckets if isinstance(buckets, list) else []
        return []

    def save_shared(self, record: dict) -> None:
        # Shared memory write: memory_add (docs reference, verified
        # 2026-11-21). Typical inputs: text, datapack_id, agent_id,
        # metadata. memory_promote is one-way private -> shared and is
        # only for promoting an already-private memory, so direct
        # memory_add is the right call for a new shared record.
        # Idempotency: Meko does no duplicate check, so re-running the
        # demo re-added EVT-01..06 a second time (2026-11-21). Skip when
        # a record with the same id is already stored.
        rid = record.get("id")
        if rid:
            for hit in self.search(str(rid), limit=5):
                text = hit.get("memory") or hit.get("text") or ""
                if f'"id": "{rid}"' in text or f'"id":"{rid}"' in text:
                    return
        text = record.get("text") or json.dumps(record, ensure_ascii=False)
        self.call_tool("memory_add", {
            "text": text,
            "datapack_id": self.datapack,
            # The live server validates metadata as a string, not an
            # object — a dict is rejected and nothing is stored.
            "metadata": json.dumps({k: str(v) for k, v in record.items()
                                    if k not in ("text",)}),
        })

    def save_trace_artifact(self, filename: str, content: str,
                            content_type: str = "text/markdown") -> Any:
        # Trace artifacts: artifact_put (docs reference, verified
        # 2026-11-21). Content is base64; uploads are idempotent by
        # SHA-256 and the hash is the lookup key for artifact_get.
        import base64
        return self.call_tool("artifact_put", {
            "filename": filename,
            "content_base64": base64.b64encode(
                content.encode("utf-8")).decode("ascii"),
            "content_type": content_type,
            "datapack_id": self.datapack,
        })
