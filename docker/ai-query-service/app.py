#!/usr/bin/env python3
"""
AI Query Service for Pan-Dashboard
Converts natural language questions to ClickHouse SQL queries using Ollama
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import clickhouse_connect
import httpx
import json
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pan-Dashboard AI Query Service")

# Configuration
CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_USER = "default"
CLICKHOUSE_PASSWORD = "clickhouse"
DATABASE = "file_share"
TABLE = "file_scan"

OLLAMA_URL = "http://192.168.33.197:11434"
OLLAMA_MODEL = "mistral-nemo:12b-instruct-2407-q8_0"

# Database schema for the model
SCHEMA_INFO = """
Database: file_share
Table: file_scan

Columns:
- path (String): Full file path
- filename (String): File name
- extension (LowCardinality(String)): File extension (e.g., 'docx', 'xlsx', 'pdf')
- size (UInt64): File size in bytes
- migrated (UInt8): Whether file is migrated (0 or 1)
- creation_date (DateTime): When file was created
- modify_date (DateTime): When file was last modified
- last_accessed_date (DateTime): When file was last accessed
- owner (String): File owner in format 'DOMAIN\\username'
- acl (String): Access control list
- duplicate_hash (String): Hash for duplicate detection
- scan_date (Date): When scan was performed

Computed expressions (use these in queries):
- splitByChar('\\\\', owner)[1] AS domain
- splitByChar('\\\\', owner)[2] AS username
- dateDiff('day', modify_date, now()) AS days_since_modified
- dateDiff('day', last_accessed_date, now()) AS days_since_accessed
- dateDiff('day', creation_date, now()) AS file_age_days
- if(size = 0, 1, 0) AS is_empty
- if(filename = '.', 1, 0) AS is_directory

Important notes:
- Use formatReadableSize(SUM(size)) for human-readable sizes
- Use formatReadableQuantity(COUNT(*)) for large numbers
- Owner format requires double backslash: splitByChar('\\\\', owner)
- Always use appropriate aggregations for summary queries
"""

class QueryRequest(BaseModel):
    question: str
    max_rows: Optional[int] = 100

class QueryResponse(BaseModel):
    question: str
    sql: str
    results: list
    row_count: int
    explanation: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Pan-Dashboard AI Query Service",
        "status": "running",
        "ollama_model": OLLAMA_MODEL,
        "database": f"{DATABASE}.{TABLE}"
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    status = {"service": "ok"}
    
    # Check ClickHouse
    try:
        client = clickhouse_connect.get_client(
            host=CLICKHOUSE_HOST,
            port=CLICKHOUSE_PORT,
            username=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD
        )
        result = client.query("SELECT COUNT(*) FROM file_share.file_scan")
        status["clickhouse"] = f"ok ({result.result_rows[0][0]:,} rows)"
        client.close()
    except Exception as e:
        status["clickhouse"] = f"error: {str(e)}"
    
    # Check Ollama
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                if OLLAMA_MODEL in model_names:
                    status["ollama"] = f"ok (model: {OLLAMA_MODEL})"
                else:
                    status["ollama"] = f"warning: {OLLAMA_MODEL} not found"
            else:
                status["ollama"] = f"error: status {response.status_code}"
    except Exception as e:
        status["ollama"] = f"error: {str(e)}"
    
    return status

async def generate_sql(question: str) -> Dict[str, str]:
    """Generate SQL query from natural language using Ollama"""
    
    prompt = f"""### Task
Generate a ClickHouse SQL query for: {question}

### Database Schema
Table: file_share.file_scan
Columns: path, filename, extension, size, migrated, creation_date, modify_date, last_accessed_date, owner (format: DOMAIN\\username), acl, duplicate_hash, scan_date

Computed expressions:
- Domain: splitByChar('\\\\', owner)[1]
- Username: splitByChar('\\\\', owner)[2]
- Days since modified: dateDiff('day', modify_date, now())
- Days since accessed: dateDiff('day', last_accessed_date, now())
- File age: dateDiff('day', creation_date, now())

### Response Format
Return ONLY the SQL SELECT statement. No explanations, no markdown, no comments.
Do not include any text before or after the query.

SQL Query:"""

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "system": "You are a SQL code generator. Output only SQL queries, nothing else.",
                    "options": {
                        "temperature": 0.0,
                        "top_p": 0.1,
                        "stop": ["\n\n", "###", "---", "Note:", "Explanation:"]
                    }
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Ollama error: {response.status_code}")
            
            result = response.json()
            sql = result.get("response", "").strip()
            
            # Log the raw response for debugging
            print(f"DEBUG: Raw SQL response length: {len(sql)}")
            print(f"DEBUG: Raw SQL first 1000 chars: {sql[:1000]}")
            logger.info(f"Raw SQL response: {sql[:500]}")
            
            # Clean up the SQL (remove markdown formatting if present)
            if sql.startswith("```sql"):
                sql = sql.replace("```sql", "").replace("```", "").strip()
            elif sql.startswith("```"):
                sql = sql.replace("```", "").strip()
            
            # Extract SQL if there's explanatory text before it
            if "SELECT" in sql.upper() and not sql.upper().startswith("SELECT"):
                # Find the SELECT statement
                lines = sql.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().upper().startswith("SELECT"):
                        sql = '\n'.join(lines[i:])
                        break
            
            sql = sql.strip()
            logger.info(f"Cleaned SQL: {sql}")
            
            # Basic validation
            sql_upper = sql.upper()
            if not sql_upper.startswith("SELECT"):
                logger.error(f"Invalid SQL generated: {sql}")
                raise HTTPException(status_code=400, detail=f"Generated query must be a SELECT statement. Got: {sql[:100]}")
            
            if any(keyword in sql_upper for keyword in ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE"]):
                raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
            
            return {"sql": sql, "model_used": OLLAMA_MODEL}
            
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Ollama request timed out")
    except Exception as e:
        logger.error(f"Unexpected error generating SQL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Main endpoint: Convert natural language question to SQL and execute
    """
    try:
        # Generate SQL from natural language
        logger.info(f"Question: {request.question}")
        sql_result = await generate_sql(request.question)
        sql = sql_result["sql"]
        logger.info(f"Generated SQL: {sql}")
        
        # Execute query on ClickHouse
        client = clickhouse_connect.get_client(
            host=CLICKHOUSE_HOST,
            port=CLICKHOUSE_PORT,
            username=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD
        )
        
        # Add LIMIT if not present
        if "LIMIT" not in sql.upper():
            sql = f"{sql} LIMIT {request.max_rows}"
        
        result = client.query(sql)
        
        # Format results
        columns = result.column_names
        rows = result.result_rows
        
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        
        # Generate explanation
        explanation = f"Found {len(results)} result(s)"
        if len(results) == request.max_rows:
            explanation += f" (limited to {request.max_rows})"
        
        client.close()
        
        return QueryResponse(
            question=request.question,
            sql=sql,
            results=results,
            row_count=len(results),
            explanation=explanation
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error executing query: {str(e)}")

@app.get("/schema")
async def get_schema():
    """Return database schema information"""
    return {
        "database": DATABASE,
        "table": TABLE,
        "schema": SCHEMA_INFO
    }

# OpenAI-compatible endpoints for Open WebUI integration
@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)"""
    return {
        "object": "list",
        "data": [{
            "id": "file-query-assistant",
            "object": "model",
            "created": 1234567890,
            "owned_by": "pan-dashboard"
        }]
    }

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    stream: Optional[bool] = False

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    OpenAI-compatible chat endpoint that automatically queries the database
    """
    try:
        # Extract the last user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        question = user_messages[-1].content
        
        # Query the database using our AI service
        query_request = QueryRequest(question=question, max_rows=50)
        result = await query(query_request)
        
        # Format response for chat
        response_content = f"""I queried the file share database for you.

**SQL Query Generated:**
```sql
{result.sql}
```

**Results ({result.row_count} rows):**

"""
        
        if result.results:
            # Format first few results as a readable list
            for i, row in enumerate(result.results[:10], 1):
                response_content += f"{i}. "
                response_content += ", ".join([f"{k}: {v}" for k, v in row.items()])
                response_content += "\n"
            
            if result.row_count > 10:
                response_content += f"\n_(Showing 10 of {result.row_count} results)_"
        else:
            response_content += "_No results found_"
        
        response_content += f"\n\n{result.explanation}"
        
        # Return OpenAI-compatible response
        return {
            "id": "chatcmpl-pan-" + str(hash(question)),
            "object": "chat.completion",
            "created": 1234567890,
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat completion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

