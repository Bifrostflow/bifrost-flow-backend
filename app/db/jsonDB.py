from typing import Optional, Dict, List
from app.db.tool_data import ToolModel, tools_data


class LocalDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalDB, cls).__new__(cls)
        return cls._instance

    def _load_tools(self) -> Dict[str, ToolModel]:
        return tools_data

    def get_by_id(self, id: str) -> Optional[ToolModel]:
        tools = self._load_tools()
        print("id,tools.get(id): ", dict(tools).get(id))
        return dict(tools).get(id)

    def get_by_state(self, state: str) -> List[ToolModel]:
        tools = self._load_tools()
        return [tool for tool in tools.values() if tool.state == state]

    def get_by_category(self, category: str) -> List[ToolModel]:
        tools = self._load_tools()
        return [tool for tool in tools.values() if tool["category"] == category]

    def get_by_key_value(self, key: str, value: str) -> List[ToolModel]:
        tools = self._load_tools()
        return [tool for tool in tools.values() if tool.get(key) == value]


# ✅ Use the singleton
tools_db = LocalDB()
