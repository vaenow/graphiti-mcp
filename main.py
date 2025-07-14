#!/usr/bin/env python3
"""
Graphiti 应用示例
基于 https://github.com/getzep/graphiti 的快速开始指南
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from logging import INFO

from dotenv import load_dotenv
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF

# 配置日志
logging.basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# Neo4j 连接参数
neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
neo4j_password = os.environ.get('NEO4J_PASSWORD', 'password')

if not neo4j_uri or not neo4j_user or not neo4j_password:
    raise ValueError('NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set')

async def main():
    """主函数 - 演示 Graphiti 基本功能"""
    logger.info("开始初始化 Graphiti...")
    
    # 初始化 Graphiti
    graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password)
    
    try:
        # 初始化图数据库索引和约束（只需要执行一次）
        logger.info("构建索引和约束...")
        await graphiti.build_indices_and_constraints()
        
        # 示例数据：包含文本和 JSON 格式的片段
        episodes = [
            {
                'content': 'Kamala Harris is the Attorney General of California. She was previously '
                          'the district attorney for San Francisco.',
                'type': EpisodeType.text,
                'description': 'podcast transcript',
            },
            {
                'content': 'As AG, Harris was in office from January 3, 2011 – January 3, 2017',
                'type': EpisodeType.text,
                'description': 'podcast transcript',
            },
            {
                'content': {
                    'name': 'Gavin Newsom',
                    'position': 'Governor',
                    'state': 'California',
                    'previous_role': 'Lieutenant Governor',
                    'previous_location': 'San Francisco',
                },
                'type': EpisodeType.json,
                'description': 'podcast metadata',
            },
            {
                'content': {
                    'name': 'Gavin Newsom',
                    'position': 'Governor',
                    'term_start': 'January 7, 2019',
                    'term_end': 'Present',
                },
                'type': EpisodeType.json,
                'description': 'podcast metadata',
            },
        ]
        
        # 添加片段到图中
        logger.info("添加片段到知识图谱...")
        for i, episode in enumerate(episodes):
            await graphiti.add_episode(
                name=f'Freakonomics Radio {i}',
                episode_body=episode['content']
                if isinstance(episode['content'], str)
                else json.dumps(episode['content']),
                source=episode['type'],
                source_description=episode['description'],
                reference_time=datetime.now(timezone.utc),
            )
            logger.info(f'已添加片段: Freakonomics Radio {i} ({episode["type"].value})')
        
        # 基础搜索
        logger.info("\n执行混合搜索: 'Who was the California Attorney General?'")
        results = await graphiti.search('Who was the California Attorney General?')
        
        # 打印搜索结果
        logger.info('\n搜索结果:')
        for result in results:
            logger.info(f'UUID: {result.uuid}')
            logger.info(f'事实: {result.fact}')
            if hasattr(result, 'valid_at') and result.valid_at:
                logger.info(f'有效期从: {result.valid_at}')
            if hasattr(result, 'invalid_at') and result.invalid_at:
                logger.info(f'有效期至: {result.invalid_at}')
            logger.info('---')
        
        # 中心节点搜索
        if results and len(results) > 0:
            # 使用顶部搜索结果的 UUID 作为中心节点进行重新排序
            center_node_uuid = results[0].source_node_uuid
            
            logger.info('\n基于图距离重新排序搜索结果:')
            logger.info(f'使用中心节点 UUID: {center_node_uuid}')
            
            reranked_results = await graphiti.search(
                'Who was the California Attorney General?', center_node_uuid=center_node_uuid
            )
            
            # 打印重新排序的搜索结果
            logger.info('\n重新排序的搜索结果:')
            for result in reranked_results:
                logger.info(f'UUID: {result.uuid}')
                logger.info(f'事实: {result.fact}')
                if hasattr(result, 'valid_at') and result.valid_at:
                    logger.info(f'有效期从: {result.valid_at}')
                if hasattr(result, 'invalid_at') and result.invalid_at:
                    logger.info(f'有效期至: {result.invalid_at}')
                logger.info('---')
        else:
            logger.info('在初始搜索中未找到结果，无法作为中心节点使用。')
        
        # 使用标准搜索配方进行节点搜索
        logger.info('\n使用标准搜索配方 NODE_HYBRID_SEARCH_RRF 执行节点搜索:')
        
        # 使用预定义的搜索配置配方并修改其限制
        node_search_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        node_search_config.limit = 5  # 限制为 5 个结果
        
        # 执行节点搜索
        node_search_results = await graphiti._search(
            query='California Governor',
            config=node_search_config,
        )
        
        # 打印节点搜索结果
        logger.info('\n节点搜索结果:')
        for node in node_search_results.nodes:
            logger.info(f'节点 UUID: {node.uuid}')
            logger.info(f'节点名称: {node.name}')
            node_summary = node.summary[:100] + '...' if len(node.summary) > 100 else node.summary
            logger.info(f'内容摘要: {node_summary}')
            logger.info(f"节点标签: {', '.join(node.labels)}")
            logger.info(f'创建时间: {node.created_at}')
            if hasattr(node, 'attributes') and node.attributes:
                logger.info('属性:')
                for key, value in node.attributes.items():
                    logger.info(f'  {key}: {value}')
            logger.info('---')
        
        logger.info("Graphiti 应用演示完成！")
        
    except Exception as e:
        logger.error(f"发生错误: {e}")
        raise
    finally:
        # 关闭连接
        await graphiti.close()
        logger.info('\n连接已关闭')

if __name__ == '__main__':
    logger.info("启动 Graphiti 应用...")
    asyncio.run(main()) 