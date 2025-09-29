#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACMOJ API 客户端命令行工具 - Git提交版本 v2.1

使用示例:
1. 提交Git链接:
   python3 acmoj_client.py --token ${ACMOJ_TOKEN} submit --problem-id ${ACMOJ_PROBLEM_ID} --git-url ${REPO_URL}
   返回的结果包含submission_id信息，请你保存以便后续查询状态
2. 查询提交状态:
   python3 acmoj_client.py --token ${ACMOJ_TOKEN} status --submission-id <your_submission_id>
   请注意评测需要时间，建议间隔10秒后再查询状态
   比如如果返回的结果是"status": "compiling", "status": "pending"等，说明评测还在进行中或者排队中，请稍后再查询
"""
import requests
import json
import time
import argparse
import os
from typing import Dict, Any, Optional

class ACMOJClient:
    def __init__(self, access_token: str):
        self.api_base = "https://acm.sjtu.edu.cn/OnlineJudge/api/v1"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "ACMOJ-Python-Client/2.1"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Optional[Dict]:
        url = f"{self.api_base}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, data=data, timeout=10)
            else:
                print(f"Unsupported HTTP method: {method}")
                return None
            
            if response.status_code == 204:
                return {"status": "success", "message": "Operation successful"}
            
            response.raise_for_status()
            
            if response.content:
                return response.json()
            else:
                return {"status": "success"}
        
        except requests.exceptions.RequestException as e:
            print(f"API Request failed: {e}")
            if 'response' in locals() and response:
                print(f"Response text: {response.text}")
            return None
    
    def submit_git(self, problem_id: int, git_url: str) -> Optional[Dict]:
        data = {"language": "git", "code": git_url}
        return self._make_request("POST", f"/problem/{problem_id}/submit", data=data)
    
    def get_submission_detail(self, submission_id: int) -> Optional[Dict]:
        return self._make_request("GET", f"/submission/{submission_id}")

def main():
    parser = argparse.ArgumentParser(description="ACMOJ API Command Line Client")
    parser.add_argument("--token", help="ACMOJ Access Token", default=os.environ.get("ACMOJ_TOKEN"))
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Git提交子命令
    submit_parser = subparsers.add_parser("submit", help="提交Git仓库")
    submit_parser.add_argument("--problem-id", type=int, required=True, help="题目ID")
    submit_parser.add_argument("--git-url", type=str, required=True, help="Git仓库URL")
    
    # Sub-command for checking submission status
    status_parser = subparsers.add_parser("status", help="Check submission status")
    status_parser.add_argument("--submission-id", type=int, required=True, help="Submission ID")
    
    args = parser.parse_args()
    
    if not args.token:
        print("Error: Access token not provided. Use --token or set ACMOJ_TOKEN environment variable.")
        return
    
    client = ACMOJClient(args.token)
    
    if args.command == "submit":
        result = client.submit_git(args.problem_id, args.git_url)
    elif args.command == "status":
        result = client.get_submission_detail(args.submission_id)
    
    if result:
        print(json.dumps(result))
    else:
        # Exit with a non-zero status code to indicate failure to shell scripts
        exit(1)

if __name__ == "__main__":
    main()