#!/usr/bin/env python3
"""
飞书文档权限转移助手
支持：转移所有权、添加/移除协作者
"""

import requests
import json
import os
import time
from typing import Optional, List, Dict

class FeishuPermTransfer:
    """飞书文档权限管理类"""
    
    BASE_URL = "https://open.feishu.cn/open-apis"
    
    def __init__(self, app_id: Optional[str] = None, app_secret: Optional[str] = None):
        """
        初始化
        
        Args:
            app_id: 飞书应用ID，默认从环境变量FEISHU_APP_ID读取
            app_secret: 飞书应用密钥，默认从环境变量FEISHU_APP_SECRET读取
        """
        self.app_id = app_id or os.getenv("FEISHU_APP_ID")
        self.app_secret = app_secret or os.getenv("FEISHU_APP_SECRET")
        
        if not self.app_id or not self.app_secret:
            raise ValueError("请设置FEISHU_APP_ID和FEISHU_APP_SECRET环境变量")
        
        self._token = None
        self._token_expire = 0
    
    def _get_tenant_access_token(self) -> str:
        """获取tenant_access_token（带缓存）"""
        if self._token and time.time() < self._token_expire:
            return self._token
        
        url = f"{self.BASE_URL}/auth/v3/tenant_access_token/internal/"
        resp = requests.post(url, json={
            "app_id": self.app_id,
            "app_secret": self.app_secret
        })
        
        if resp.status_code != 200:
            raise Exception(f"获取token失败: {resp.text}")
        
        data = resp.json()
        if data.get("code") != 0:
            raise Exception(f"获取token失败: {data.get('msg')}")
        
        self._token = data["tenant_access_token"]
        # token有效期2小时，提前5分钟刷新
        self._token_expire = time.time() + data.get("expire", 7200) - 300
        return self._token
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """发送API请求"""
        token = self._get_tenant_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.BASE_URL}{endpoint}"
        resp = requests.request(method, url, headers=headers, **kwargs)
        
        if resp.status_code not in [200, 201]:
            raise Exception(f"API请求失败: {resp.status_code} - {resp.text}")
        
        data = resp.json()
        if data.get("code") != 0:
            raise Exception(f"API错误: {data.get('msg', '未知错误')}")
        
        return data
    
    def transfer_owner(self, doc_token: str, doc_type: str, target_open_id: str) -> bool:
        """
        转移文档所有权
        
        Args:
            doc_token: 文档Token（从URL中获取）
            doc_type: 文档类型 - docx/sheet/bitable/wiki
            target_open_id: 接收人的OpenID
            
        Returns:
            bool: 是否成功
        """
        try:
            # 先添加新所有者为协作者（full_access）
            self.add_member(doc_token, doc_type, target_open_id, "full_access")
            
            # 注意：飞书API不直接支持"转移所有权"，只能通过添加full_access实现
            # 真正的所有权转移需要在飞书后台操作或由当前所有者手动转移
            
            print(f"✅ 已将 {doc_token} 的管理权限授予 {target_open_id}")
            print("⚠️ 注意：完全的所有权转移需要在飞书文档设置中手动操作")
            return True
            
        except Exception as e:
            print(f"❌ 转移失败: {e}")
            return False
    
    def add_member(self, doc_token: str, doc_type: str, 
                   member_open_id: str, perm: str = "view") -> bool:
        """
        添加协作者
        
        Args:
            doc_token: 文档Token
            doc_type: 文档类型
            member_open_id: 协作者的OpenID
            perm: 权限 - view/edit/full_access
            
        Returns:
            bool: 是否成功
        """
        try:
            endpoint = f"/drive/v1/permissions/{doc_token}/members"
            
            data = {
                "member": {
                    "type": "openid",
                    "openid": member_open_id,
                    "perm": perm
                }
            }
            
            self._request("POST", endpoint, json=data, params={"type": doc_type})
            print(f"✅ 已添加 {member_open_id} 权限: {perm}")
            return True
            
        except Exception as e:
            print(f"❌ 添加失败: {e}")
            return False
    
    def remove_member(self, doc_token: str, doc_type: str, 
                      member_open_id: str) -> bool:
        """
        移除协作者
        
        Args:
            doc_token: 文档Token
            doc_type: 文档类型
            member_open_id: 协作者的OpenID
            
        Returns:
            bool: 是否成功
        """
        try:
            # 需要先获取member_token
            members = self.list_members(doc_token, doc_type)
            member_token = None
            
            for member in members:
                if member.get("member_id") == member_open_id:
                    member_token = member.get("member_token")
                    break
            
            if not member_token:
                print(f"⚠️ 未找到协作者 {member_open_id}")
                return False
            
            endpoint = f"/drive/v1/permissions/{doc_token}/members/{member_token}"
            self._request("DELETE", endpoint, params={"type": doc_type})
            
            print(f"✅ 已移除 {member_open_id}")
            return True
            
        except Exception as e:
            print(f"❌ 移除失败: {e}")
            return False
    
    def list_members(self, doc_token: str, doc_type: str) -> List[Dict]:
        """
        获取协作者列表
        
        Args:
            doc_token: 文档Token
            doc_type: 文档类型
            
        Returns:
            List[Dict]: 协作者列表
        """
        endpoint = f"/drive/v1/permissions/{doc_token}/members"
        
        data = self._request("GET", endpoint, params={"type": doc_type})
        return data.get("data", {}).get("members", [])
    
    def batch_transfer(self, docs: List[Dict], target_open_id: str,
                       delay: float = 0.5) -> Dict[str, bool]:
        """
        批量转移文档权限
        
        Args:
            docs: 文档列表，每项包含token和type
            target_open_id: 接收人OpenID
            delay: 请求间隔（秒）
            
        Returns:
            Dict[str, bool]: 每个文档的转移结果
        """
        results = {}
        
        print(f"=== 开始批量转移 {len(docs)} 个文档 ===\n")
        
        for i, doc in enumerate(docs, 1):
            token = doc.get("token")
            doc_type = doc.get("type", "docx")
            name = doc.get("name", f"文档{i}")
            
            print(f"[{i}/{len(docs)}] 处理: {name}")
            success = self.transfer_owner(token, doc_type, target_open_id)
            results[token] = success
            
            if i < len(docs):  # 最后一个不用等
                time.sleep(delay)
        
        print(f"\n=== 完成 ===")
        success_count = sum(1 for v in results.values() if v)
        print(f"成功: {success_count}/{len(docs)}")
        
        return results


# 便捷函数（供外部调用）
def set_credentials(app_id: str, app_secret: str):
    """设置全局凭证"""
    os.environ["FEISHU_APP_ID"] = app_id
    os.environ["FEISHU_APP_SECRET"] = app_secret

def transfer_owner(doc_token: str, doc_type: str, target_open_id: str) -> bool:
    """转移文档所有权"""
    transfer = FeishuPermTransfer()
    return transfer.transfer_owner(doc_token, doc_type, target_open_id)

def add_member(doc_token: str, doc_type: str, 
               member_open_id: str, perm: str = "view") -> bool:
    """添加协作者"""
    transfer = FeishuPermTransfer()
    return transfer.add_member(doc_token, doc_type, member_open_id, perm)

def remove_member(doc_token: str, doc_type: str, member_open_id: str) -> bool:
    """移除协作者"""
    transfer = FeishuPermTransfer()
    return transfer.remove_member(doc_token, doc_type, member_open_id)


# CLI入口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python perm_transfer.py transfer <doc_token> <doc_type> <target_open_id>")
        print("  python perm_transfer.py add <doc_token> <doc_type> <member_open_id> [perm]")
        print("  python perm_transfer.py remove <doc_token> <doc_type> <member_open_id>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "transfer" and len(sys.argv) >= 5:
        transfer_owner(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "add" and len(sys.argv) >= 5:
        perm = sys.argv[5] if len(sys.argv) > 5 else "view"
        add_member(sys.argv[2], sys.argv[3], sys.argv[4], perm)
    elif cmd == "remove" and len(sys.argv) >= 5:
        remove_member(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("参数错误")
