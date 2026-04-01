#!/usr/bin/env python3
"""
飞书云文档写作助手
支持：创建文档、Markdown转换、模板生成
"""

import requests
import json
import os
import time
import re
from typing import Optional, List, Dict, Any
from datetime import datetime

class DocWriter:
    """飞书云文档写作助手"""
    
    BASE_URL = "https://open.feishu.cn/open-apis"
    
    # 内置模板
    TEMPLATES = {
        "meeting_minutes": {
            "title": "{title} - 会议纪要",
            "content": """# {title}

## 基本信息
- **时间**: {date}
- **地点**: {location}
- **主持人**: {host}

## 参会人员
{attendees}

## 会议内容
{topics}

## 会议结论
{decisions}

## 行动项
{actions}
"""
        },
        "weekly_report": {
            "title": "周报 - {week}",
            "content": """# 周报 - {week} ({date_range})

## 本周完成
{completed}

## 进行中
{in_progress}

## 下周计划
{next_week}

## 问题与风险
{issues}
"""
        },
        "monthly_report": {
            "title": "{month}月报",
            "content": """# {month}月度工作报告

## 月度总结
{summary}

## 关键成果
{achievements}

## 数据分析
{data}

## 下月计划
{next_month}
"""
        },
        "project_proposal": {
            "title": "项目提案 - {project_name}",
            "content": """# 项目提案：{project_name}

## 项目背景
{background}

## 项目目标
{objectives}

## 预期成果
{deliverables}

## 时间规划
{timeline}

## 资源需求
{resources}
"""
        }
    }
    
    def __init__(self, app_id: Optional[str] = None, app_secret: Optional[str] = None):
        self.app_id = app_id or os.getenv("FEISHU_APP_ID")
        self.app_secret = app_secret or os.getenv("FEISHU_APP_SECRET")
        
        if not self.app_id or not self.app_secret:
            raise ValueError("请设置FEISHU_APP_ID和FEISHU_APP_SECRET")
        
        self._token = None
        self._token_expire = 0
    
    def _get_token(self) -> str:
        """获取tenant_access_token"""
        if self._token and time.time() < self._token_expire:
            return self._token
        
        url = f"{self.BASE_URL}/auth/v3/tenant_access_token/internal/"
        resp = requests.post(url, json={"app_id": self.app_id, "app_secret": self.app_secret})
        
        if resp.status_code != 200:
            raise Exception(f"获取token失败: {resp.text}")
        
        data = resp.json()
        if data.get("code") != 0:
            raise Exception(f"获取token失败: {data.get('msg')}")
        
        self._token = data["tenant_access_token"]
        self._token_expire = time.time() + data.get("expire", 7200) - 300
        return self._token
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """发送API请求"""
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        url = f"{self.BASE_URL}{endpoint}"
        resp = requests.request(method, url, headers=headers, **kwargs)
        
        if resp.status_code not in [200, 201]:
            raise Exception(f"API请求失败: {resp.status_code} - {resp.text}")
        
        data = resp.json()
        if data.get("code") != 0:
            raise Exception(f"API错误: {data.get('msg', '未知错误')}")
        
        return data
    
    def create_doc(self, title: str, folder_token: Optional[str] = None) -> str:
        """
        创建云文档
        
        Args:
            title: 文档标题
            folder_token: 父文件夹token（可选）
            
        Returns:
            str: 文档token
        """
        try:
            # 创建空白文档
            endpoint = "/docx/v1/documents"
            data = {"title": title}
            if folder_token:
                data["folder_token"] = folder_token
            
            result = self._request("POST", endpoint, json=data)
            doc_token = result["data"]["document"]["document_id"]
            
            print(f"✅ 文档创建成功: {title}")
            print(f"   链接: https://feishu.cn/docx/{doc_token}")
            return doc_token
            
        except Exception as e:
            print(f"❌ 创建失败: {e}")
            raise
    
    def write_content(self, doc_token: str, content: str) -> bool:
        """
        写入文档内容（纯文本）
        
        Args:
            doc_token: 文档token
            content: 文本内容
            
        Returns:
            bool: 是否成功
        """
        try:
            # 先转换为Markdown再写入
            return self.write_markdown(doc_token, content)
        except Exception as e:
            print(f"❌ 写入失败: {e}")
            return False
    
    def write_markdown(self, doc_token: str, markdown_text: str) -> bool:
        """
        写入Markdown内容（自动转换）
        
        Args:
            doc_token: 文档token
            markdown_text: Markdown文本
            
        Returns:
            bool: 是否成功
        """
        try:
            # 解析Markdown为blocks
            blocks = self._markdown_to_blocks(markdown_text)
            
            # 批量写入blocks
            endpoint = f"/docx/v1/documents/{doc_token}/blocks/batch_create"
            
            # 飞书API限制，每次最多写入一定数量的blocks
            batch_size = 50
            for i in range(0, len(blocks), batch_size):
                batch = blocks[i:i+batch_size]
                data = {
                    "children": batch,
                    "document_revision_id": -1  # 最新版本
                }
                
                self._request("POST", endpoint, json=data)
                time.sleep(0.2)  # 避免频率限制
            
            print(f"✅ Markdown内容已写入")
            return True
            
        except Exception as e:
            print(f"❌ Markdown写入失败: {e}")
            return False
    
    def _markdown_to_blocks(self, markdown_text: str) -> List[Dict]:
        """将Markdown转换为飞书blocks"""
        blocks = []
        lines = markdown_text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 空行跳过
            if not line:
                i += 1
                continue
            
            # 标题
            if line.startswith('# '):
                blocks.append(self._make_heading(line[2:], 1))
            elif line.startswith('## '):
                blocks.append(self._make_heading(line[3:], 2))
            elif line.startswith('### '):
                blocks.append(self._make_heading(line[4:], 3))
            
            # 列表
            elif line.startswith('- ') or line.startswith('* '):
                # 收集连续列表项
                items = []
                while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                    items.append(lines[i].strip()[2:])
                    i += 1
                blocks.append(self._make_bulleted_list(items))
                continue
            
            # 有序列表
            elif re.match(r'^\d+\.\s', line):
                items = []
                while i < len(lines) and re.match(r'^\d+\.\s', lines[i].strip()):
                    match = re.match(r'^\d+\.\s(.*)', lines[i].strip())
                    if match:
                        items.append(match.group(1))
                    i += 1
                blocks.append(self._make_numbered_list(items))
                continue
            
            # 表格
            elif line.startswith('|') and i + 1 < len(lines) and '-' in lines[i + 1]:
                table_lines = [line]
                i += 1
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_lines.append(lines[i])
                    i += 1
                blocks.append(self._make_table(table_lines))
                continue
            
            # 分割线
            elif line == '---' or line == '***':
                blocks.append(self._make_divider())
            
            # 普通文本
            else:
                blocks.append(self._make_text(line))
            
            i += 1
        
        return blocks
    
    def _make_heading(self, text: str, level: int) -> Dict:
        """创建标题block"""
        return {
            "block_type": f"heading{level}",
            f"heading{level}": {
                "elements": [{"type": "textRun", "textRun": {"content": text}}]
            }
        }
    
    def _make_text(self, text: str) -> Dict:
        """创建文本block"""
        return {
            "block_type": "paragraph",
            "paragraph": {
                "elements": [{"type": "textRun", "textRun": {"content": text}}]
            }
        }
    
    def _make_bulleted_list(self, items: List[str]) -> Dict:
        """创建无序列表block"""
        children = []
        for item in items:
            children.append({
                "block_type": "paragraph",
                "paragraph": {
                    "elements": [{"type": "textRun", "textRun": {"content": item}}]
                }
            })
        
        return {
            "block_type": "bulleted_list",
            "bulleted_list": {},
            "children": children
        }
    
    def _make_numbered_list(self, items: List[str]) -> Dict:
        """创建有序列表block"""
        children = []
        for item in items:
            children.append({
                "block_type": "paragraph",
                "paragraph": {
                    "elements": [{"type": "textRun", "textRun": {"content": item}}]
                }
            })
        
        return {
            "block_type": "numbered_list",
            "numbered_list": {},
            "children": children
        }
    
    def _make_table(self, lines: List[str]) -> Dict:
        """创建表格block"""
        # 解析表格
        rows = []
        for line in lines:
            if '|' in line and '---' not in line:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                rows.append(cells)
        
        if not rows:
            return self._make_text("[表格解析失败]")
        
        # 构建表格block
        table_data = {
            "block_type": "table",
            "table": {
                "row_size": len(rows),
                "column_size": len(rows[0]) if rows else 0,
                "table_cells": []
            }
        }
        
        for row_idx, row in enumerate(rows):
            for col_idx, cell in enumerate(row):
                table_data["table"]["table_cells"].append({
                    "row_index": row_idx,
                    "column_index": col_idx,
                    "content": [{
                        "type": "paragraph",
                        "paragraph": {
                            "elements": [{"type": "textRun", "textRun": {"content": cell}}]
                        }
                    }]
                })
        
        return table_data
    
    def _make_divider(self) -> Dict:
        """创建分割线block"""
        return {"block_type": "divider", "divider": {}}
    
    def create_from_template(self, template_name: str, data: Dict) -> str:
        """
        从模板创建文档
        
        Args:
            template_name: 模板名称
            data: 模板数据
            
        Returns:
            str: 文档token
        """
        if template_name not in self.TEMPLATES:
            raise ValueError(f"未知模板: {template_name}，可用: {list(self.TEMPLATES.keys())}")
        
        template = self.TEMPLATES[template_name]
        
        # 格式化标题
        title = template["title"].format(**data)
        
        # 格式化内容
        content = template["content"].format(**data)
        
        # 创建文档
        doc_token = self.create_doc(title)
        
        # 写入内容
        self.write_markdown(doc_token, content)
        
        return doc_token
    
    def batch_generate(self, template_name: str, data_list: List[Dict], 
                       delay: float = 0.5) -> List[str]:
        """
        批量生成文档
        
        Args:
            template_name: 模板名称
            data_list: 数据列表
            delay: 请求间隔
            
        Returns:
            List[str]: 文档token列表
        """
        doc_tokens = []
        
        print(f"=== 开始批量生成 {len(data_list)} 个文档 ===\n")
        
        for i, data in enumerate(data_list, 1):
            try:
                print(f"[{i}/{len(data_list)}] 生成中...")
                doc_token = self.create_from_template(template_name, data)
                doc_tokens.append(doc_token)
                
                if i < len(data_list):
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"❌ 第{i}个生成失败: {e}")
                doc_tokens.append(None)
        
        success_count = sum(1 for t in doc_tokens if t)
        print(f"\n=== 完成: {success_count}/{len(data_list)} ===")
        
        return doc_tokens


# 便捷函数
def create_doc(title: str, folder_token: Optional[str] = None) -> str:
    """创建文档"""
    writer = DocWriter()
    return writer.create_doc(title, folder_token)

def write_markdown(doc_token: str, markdown_text: str) -> bool:
    """写入Markdown"""
    writer = DocWriter()
    return writer.write_markdown(doc_token, markdown_text)

def create_meeting_minutes(data: Dict) -> str:
    """创建会议纪要"""
    writer = DocWriter()
    return writer.create_from_template("meeting_minutes", data)

def create_weekly_report(data: Dict) -> str:
    """创建周报"""
    writer = DocWriter()
    return writer.create_from_template("weekly_report", data)


# CLI入口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python doc_writer.py create <标题>")
        print("  python doc_writer.py meeting <标题> <日期>")
        print("  python doc_writer.py weekly <第几周> <日期范围>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    writer = DocWriter()
    
    if cmd == "create" and len(sys.argv) >= 3:
        title = sys.argv[2]
        doc_token = writer.create_doc(title)
        print(f"文档Token: {doc_token}")
        
    elif cmd == "meeting" and len(sys.argv) >= 4:
        data = {
            "title": sys.argv[2],
            "date": sys.argv[3],
            "location": "会议室",
            "host": "主持人",
            "attendees": "- 参会人员",
            "topics": "1. 讨论内容",
            "decisions": "- 会议结论",
            "actions": "| 任务 | 负责人 | 截止日期 |\\n|------|--------|----------|"
        }
        doc_token = writer.create_from_template("meeting_minutes", data)
        print(f"会议纪要已创建: {doc_token}")
        
    elif cmd == "weekly" and len(sys.argv) >= 4:
        data = {
            "week": sys.argv[2],
            "date_range": sys.argv[3],
            "completed": "- 完成任务",
            "in_progress": "- 进行中",
            "next_week": "- 下周计划",
            "issues": "- 暂无"
        }
        doc_token = writer.create_from_template("weekly_report", data)
        print(f"周报已创建: {doc_token}")
    else:
        print("参数错误")
