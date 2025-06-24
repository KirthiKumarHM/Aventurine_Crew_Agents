from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
import psycopg2
import os
from openai import OpenAI


# === Tool 1: MyCustomTool ===

class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        return "this is an example of a tool output, ignore it and move along."


# === Tool 2: PostgresInventoryTool ===

class InventoryChatInput(BaseModel):
    """Input schema for the Inventory Tool using a natural language message."""
    chat_message: str = Field(..., description="A user's chatbot message about inventory.")


class PostgresInventoryTool(BaseTool):
    name: str = "PostgreSQL Inventory Tool"
    description: str = (
        "Parses a chat message, infers inventory ingredients, maps them to tables, and runs SQL on PostgreSQL."
    )
    args_schema: Type[BaseModel] = InventoryChatInput

    def _run(self, chat_message: str) -> str:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS")
        )
        cursor = conn.cursor()

        try:
            # Step 1: Get schema, filtering out tables with "_old"
            cursor.execute("""
                SELECT table_name, column_name
                FROM information_schema.columns
                WHERE table_schema = 'public';
            """)
            schema_rows = cursor.fetchall()

            # Exclude tables with "_old" in the name (case-insensitive)
            filtered_rows = [row for row in schema_rows if "_old" not in row[0].lower()]
            schema_text = "\n".join([f"{t}.{c}" for t, c in filtered_rows])
            print(f" Received chat_message: {chat_message}")
            # Step 2: Generate SQL using GPT
            prompt = f"""
                        You are an assistant that helps translate inventory-related questions into SQL.
                        
                        User asked: "{chat_message}"
                        
                        Here is the schema of the PostgreSQL database:
                        {schema_text}
                        
                        Please write ONLY the SQL SELECT queries needed to answer the user's question.You will 
                        get the id based on the name from the *_master table, get the id from this table and get total
                        actual_qty available in *_details by matching ids.
                        Return ONLY the SQL queries. No explanations or formatting.
                        """
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
            )
            sql_text = response.choices[0].message.content.strip()

            # Step 3: Parse and run the SQL queries
            results = []
            queries = [q.strip() for q in sql_text.split(";") if q.strip().lower().startswith("select")]
            for q in queries:
                cursor.execute(q)
                rows = cursor.fetchall()
                col_names = [desc[0] for desc in cursor.description]
                result = [dict(zip(col_names, row)) for row in rows]
                results.append({ "query": q, "result": result })

            if not results:
                return "No relevant data found."

            # Step 4: Format the result
            readable = ""
            for r in results:
                readable += f"\nQuery: {r['query']}\n"
                if r['result']:
                    for row in r['result']:
                        readable += f"- {row}\n"
                else:
                    readable += "- No data found.\n"
            return readable.strip()

        except Exception as e:
            return f"Error: {str(e)}"

        finally:
            if cursor: cursor.close()
            if conn: conn.close()