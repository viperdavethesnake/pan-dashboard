"""
title: File Share Query Tool
author: Pan-Dashboard
description: Query file share data using natural language
required_open_webui_version: 0.3.0
"""

import requests
import json
from typing import Callable, Any

class Tools:
    def __init__(self):
        self.citation = True
        self.valves = self.Valves()

    class Valves:
        def __init__(self):
            self.API_BASE_URL = "http://localhost:5000"
            
    def query_file_data(self, question: str, __user__: dict = {}) -> str:
        """
        Query the file share database using natural language.
        
        :param question: Natural language question about files (e.g., "How many PDF files are there?")
        :return: Query results as formatted text
        """
        try:
            url = f"{self.valves.API_BASE_URL}/query"
            payload = {
                "question": question,
                "max_rows": 100
            }
            
            response = requests.post(url, json=payload, timeout=180)
            response.raise_for_status()
            
            data = response.json()
            
            # Format the response
            result = f"**Question:** {data['question']}\n\n"
            result += f"**Generated SQL:**\n```sql\n{data['sql']}\n```\n\n"
            result += f"**Results ({data['row_count']} rows):**\n\n"
            
            if data['results']:
                # Format as table
                if len(data['results']) > 0:
                    # Get column names
                    cols = list(data['results'][0].keys())
                    
                    # Create table header
                    result += "| " + " | ".join(cols) + " |\n"
                    result += "| " + " | ".join(["---"] * len(cols)) + " |\n"
                    
                    # Add rows
                    for row in data['results'][:20]:  # Limit display to 20 rows
                        values = [str(row.get(col, "")) for col in cols]
                        result += "| " + " | ".join(values) + " |\n"
                    
                    if len(data['results']) > 20:
                        result += f"\n*Showing 20 of {len(data['results'])} results*\n"
            else:
                result += "*No results found*\n"
            
            result += f"\n_{data['explanation']}_"
            
            return result
            
        except requests.exceptions.Timeout:
            return "⚠️ Query timed out (took longer than 3 minutes). Try a simpler query."
        except requests.exceptions.RequestException as e:
            return f"❌ Error connecting to query service: {str(e)}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

