#!/usr/bin/env python3
"""
Graphiti MCP 服务器实现
提供知识图谱操作的 MCP 工具
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel import NotificationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 全局 Graphiti 实例
graphiti_instance: Optional[Graphiti] = None

async def get_graphiti() -> Graphiti:
    """获取 Graphiti 实例"""
    global graphiti_instance
    if graphiti_instance is None:
        neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
        neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
        neo4j_password = os.environ.get('NEO4J_PASSWORD', 'password')
        
        logger.info(f"连接 Neo4j: {neo4j_uri}, 用户: {neo4j_user}")
        
        try:
            graphiti_instance = Graphiti(neo4j_uri, neo4j_user, neo4j_password)
            await graphiti_instance.build_indices_and_constraints()
            logger.info("✅ Graphiti 实例已成功初始化")
        except Exception as e:
            logger.error(f"❌ Graphiti 初始化失败: {e}")
            
            # 如果是认证失败，提供清晰的解决方案
            if "unauthorized" in str(e).lower() or "authentication" in str(e).lower():
                logger.error("")
                logger.error("🔧 认证失败！这通常是因为密码不匹配造成的。")
                logger.error("💡 解决方案：设置 RESET_NEO4J=true 来重置数据和密码")
                logger.error("")
                logger.error("📝 具体步骤:")
                logger.error("   • Docker: docker run -e RESET_NEO4J=true <image>")
                logger.error("   • Docker Compose: 在 docker-compose.yml 中添加 RESET_NEO4J=true")
                logger.error("   • Kubernetes: kubectl set env statefulset/graphiti-mcp RESET_NEO4J=true -n vin")
                logger.error("")
                logger.error("⚠️  注意：这会清空所有现有数据")
            
            raise
    
    return graphiti_instance

# 创建 MCP 服务器
server = Server("graphiti-mcp")

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """列出可用资源"""
    return [
        Resource(
            uri="graphiti://graph/schema",
            name="Knowledge Graph Schema",
            description="当前知识图谱的架构信息",
            mimeType="application/json",
        ),
        Resource(
            uri="graphiti://graph/stats",
            name="Graph Statistics",
            description="知识图谱的统计信息",
            mimeType="application/json",
        ),
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """读取指定资源"""
    graphiti = await get_graphiti()
    
    if uri == "graphiti://graph/schema":
        # 返回图谱架构信息
        schema_info = {
            "node_types": ["Entity", "Episode", "Community"],
            "relationship_types": ["RELATES_TO", "PART_OF", "MENTIONS"],
            "properties": {
                "nodes": ["name", "summary", "created_at", "updated_at"],
                "relationships": ["weight", "created_at"]
            }
        }
        return json.dumps(schema_info, indent=2, ensure_ascii=False)
    
    elif uri == "graphiti://graph/stats":
        # 返回图谱统计信息
        # 注：这里需要根据实际的 graphiti API 来获取统计信息
        stats = {
            "total_nodes": "未实现",
            "total_relationships": "未实现",
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        return json.dumps(stats, indent=2, ensure_ascii=False)
    
    else:
        raise ValueError(f"未知资源: {uri}")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="add_episode",
            description="向知识图谱添加新片段",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "片段名称"
                    },
                    "content": {
                        "type": "string", 
                        "description": "片段内容"
                    },
                    "episode_type": {
                        "type": "string",
                        "enum": ["text", "json"],
                        "description": "片段类型：text 或 json",
                        "default": "text"
                    },
                    "source_description": {
                        "type": "string",
                        "description": "来源描述",
                        "default": "MCP client input"
                    }
                },
                "required": ["name", "content"]
            },
        ),
        Tool(
            name="search_graph",
            description="搜索知识图谱中的信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "结果数量限制",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    }
                },
                "required": ["query"]
            },
        ),
        Tool(
            name="get_entities",
            description="获取知识图谱中的实体信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_name": {
                        "type": "string",
                        "description": "实体名称（可选）"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "结果数量限制",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": []
            },
        ),
        Tool(
            name="get_communities",
            description="获取知识图谱中的社区信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "结果数量限制",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 20
                    }
                },
                "required": []
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[TextContent]:
    """处理工具调用"""
    graphiti = await get_graphiti()
    
    try:
        if name == "add_episode":
            # 添加片段到知识图谱
            episode_name = arguments.get("name")
            content = arguments.get("content")
            episode_type = arguments.get("episode_type", "text")
            source_description = arguments.get("source_description", "MCP client input")
            
            # 确定片段类型
            if episode_type == "json":
                ep_type = EpisodeType.json
                # 验证 JSON 格式
                try:
                    json.loads(content)
                except json.JSONDecodeError:
                    return [TextContent(
                        type="text",
                        text=f"错误：内容不是有效的 JSON 格式"
                    )]
            else:
                ep_type = EpisodeType.text
            
            # 添加片段
            await graphiti.add_episode(
                name=episode_name,
                episode_body=content,
                source=ep_type,
                source_description=source_description,
                reference_time=datetime.now(timezone.utc),
            )
            
            return [TextContent(
                type="text",
                text=f"✅ 成功添加片段 '{episode_name}' 到知识图谱"
            )]
        
        elif name == "search_graph":
            # 搜索知识图谱
            query = arguments.get("query")
            limit = arguments.get("limit", 5)
            
            results = await graphiti.search(query)
            
            if not results:
                return [TextContent(
                    type="text",
                    text=f"🔍 搜索 '{query}' 未找到相关结果"
                )]
            
            # 限制结果数量
            limited_results = results[:limit]
            
            response_lines = [f"🔍 搜索 '{query}' 的结果："]
            for i, result in enumerate(limited_results, 1):
                response_lines.append(f"\n{i}. **事实**: {result.fact}")
                if hasattr(result, 'uuid') and result.uuid:
                    response_lines.append(f"   **UUID**: {result.uuid}")
                if hasattr(result, 'valid_at') and result.valid_at:
                    response_lines.append(f"   **有效期从**: {result.valid_at}")
                response_lines.append("")
            
            return [TextContent(
                type="text",
                text="".join(response_lines)
            )]
        
        elif name == "get_entities":
            # 获取实体信息
            entity_name = arguments.get("entity_name")
            limit = arguments.get("limit", 10)
            
            # 注：这里需要根据 graphiti 的实际 API 来实现
            # 当前 API 可能没有直接获取实体的方法，需要通过搜索实现
            if entity_name:
                results = await graphiti.search(f"实体: {entity_name}")
            else:
                results = await graphiti.search("实体")
            
            if not results:
                return [TextContent(
                    type="text",
                    text="📊 当前图谱中没有找到实体信息"
                )]
            
            limited_results = results[:limit]
            response_lines = ["📊 实体信息："]
            
            for i, result in enumerate(limited_results, 1):
                response_lines.append(f"\n{i}. {result.fact}")
            
            return [TextContent(
                type="text", 
                text="".join(response_lines)
            )]
        
        elif name == "get_communities":
            # 获取社区信息
            limit = arguments.get("limit", 10)
            
            # 注：需要根据 graphiti 的实际 API 来实现社区查询
            results = await graphiti.search("社区")
            
            if not results:
                return [TextContent(
                    type="text",
                    text="🏘️ 当前图谱中没有找到社区信息"
                )]
            
            limited_results = results[:limit]
            response_lines = ["🏘️ 社区信息："]
            
            for i, result in enumerate(limited_results, 1):
                response_lines.append(f"\n{i}. {result.fact}")
            
            return [TextContent(
                type="text",
                text="".join(response_lines)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"❌ 未知工具: {name}"
            )]
    
    except Exception as e:
        logger.error(f"工具调用错误 {name}: {e}")
        return [TextContent(
            type="text",
            text=f"❌ 执行工具 '{name}' 时发生错误: {str(e)}"
        )]

async def main():
    """主函数"""
    logger.info("启动 Graphiti MCP 服务器...")
    
    # 验证环境变量
    required_vars = ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"缺少必需的环境变量: {', '.join(missing_vars)}")
        return
    
    # 初始化 Graphiti
    try:
        await get_graphiti()
        logger.info("✅ Graphiti 初始化成功")
    except Exception as e:
        logger.error(f"❌ Graphiti 初始化失败: {e}")
        return
    
    # 启动 MCP 服务器
    async with stdio_server() as (read_stream, write_stream):
        logger.info("🚀 Graphiti MCP 服务器已启动，等待客户端连接...")
        await server.run(
            read_stream, 
            write_stream, 
            InitializationOptions(
                server_name="graphiti-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 