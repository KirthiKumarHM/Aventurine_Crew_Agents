import os
from dotenv import load_dotenv
from tools.custom_tool import PostgresInventoryTool, InventoryChatInput


load_dotenv()  # Load DB and OpenAI credentials

# def test_tool():
#     tool = PostgresInventoryTool()
#
#     user_input = input("Enter an inventory question (e.g., 'How much sugar do we have?'):\n> ")
#     input_schema = InventoryChatInput(chat_message=user_input)
#
#     print("\n🔍 Running Inventory Tool...\n")
#     result = tool._run(chat_message=input_schema.chat_message)
#
#     print("\n📦 Inventory Response:\n")
#     print(result)
#
# if __name__ == "__main__":
#     test_tool()