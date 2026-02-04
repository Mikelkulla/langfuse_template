from typing import Dict

# ====================== VERSION INFO ======================
__version__ = "1.0.1"
__author__ = "Mikel Kulla"
__description__ = "Advanced MCP Agent Framework with Persistent Sessions"
__last_updated__ = "2026-02-04" # YYYY-MM-DD

# Version history tracking
VERSION_HISTORY = {
    "1.0.0": {
        "date": "2026-02-04",
        "changes": [
            "Added persistent MCP session support",
            "Improved performance with single-process architecture",
            "Enhanced logging and metrics tracking",
            "Multi-server configuration support"
        ]
    },
    "0.9.0": {
        "date": "2025-01-20",
        "changes": [
            "Initial implementation with non-persistent sessions",
            "Basic callback handlers and statistics tracking"
        ]
    }
}


# ====================== SERVER CONFIGURATIONS ======================
def get_server_configurations(monday_token: str) -> Dict[str, Dict]:
    """
    Get available MCP server configurations.

    Args:
        monday_token: Monday.com API token for native servers

    Returns:
        Dictionary of server configurations
    """
    return {
        "cdata_monday": {
            "command": r"C:\Program Files\CData\CData MCP Server for Monday 2025\jre\bin\java.exe",
            "args": [
                "-Dfile.encoding=UTF-8",
                "-jar",
                r"C:\Program Files\CData\CData MCP Server for Monday 2025\lib\cdata.mcp.monday.jar",
                "CData_Monday_MCP",
            ],
            "transport": "stdio",
            "is_native": False,
            "description": "CData Monday MCP Server - SQL interface to Monday.com"
        },
        "native_monday_static": {
            "command": "npx",
            "args": [
                "@mondaydotcomorg/monday-api-mcp@latest",
                "-t",
                monday_token,
                "--enable-dynamic-api-tools",
                "false"
            ],
            "transport": "stdio",
            "is_native": True,
            "description": "Native Monday MCP Server - Static tools only"
        },
        "native_monday_dynamic": {
            "command": "npx",
            "args": [
                "@mondaydotcomorg/monday-api-mcp@latest",
                "-t",
                monday_token,
                "--enable-dynamic-api-tools",
                "only"
            ],
            "transport": "stdio",
            "is_native": True,
            "description": "Native Monday MCP Server - Dynamic tools only"
        },
        "native_monday_full": {
            "command": "npx",
            "args": [
                "@mondaydotcomorg/monday-api-mcp@latest",
                "-t",
                monday_token,
                "--enable-dynamic-api-tools",
                "true"
            ],
            "transport": "stdio",
            "is_native": True,
            "description": "Native Monday MCP Server - All tools enabled"
        },
        "cdata_jira_mcp": {
            "command": r"C:\Program Files\CData\CData MCP Server for Jira 2025\jre\bin\java.exe",
            "args": [
                "-Dfile.encoding=UTF-8",
                "-jar",
                r"C:\Program Files\CData\CData MCP Server for Jira 2025\lib\cdata.mcp.jira.jar",
                "CData_Jira_MCP",
            ],
            "transport": "stdio",
            "is_native": False,
            "description": "CData Jira MCP Server - SQL interface to Jira"
        },
        "cdata_monday_mcp_custom": {
            "command": r"C:\Program Files\Java\jdk-21\bin\java.exe",
            "args": [
                "-Dfile.encoding=UTF-8",
                "-Dsun.stdout.encoding=UTF-8",
                "-Dsun.stderr.encoding=UTF-8",
                "-cp",
                ";".join([
                    r"C:\dev\drivers\Release\projects\ProviderMonday_mcp\out\production\providermonday",
                    r"C:\Libs\RSSBus\servlet-api-3.0.jar",
                    r"C:\Libs\mcp\mcp-0.14.1.jar",
                    r"C:\Libs\mcp\mcp-core-0.14.1.jar",
                    r"C:\Libs\mcp\mcp-json-jackson2-0.14.1.jar",
                    r"C:\Libs\mcp\jackson-annotations-2.18.3.jar",
                    r"C:\Libs\mcp\jackson-core-2.18.3.jar",
                    r"C:\Libs\mcp\jackson-databind-2.18.3.jar",
                    r"C:\Libs\mcp\jackson-dataformat-yaml-2.18.3.jar",
                    r"C:\Libs\mcp\slf4j-api-2.0.17.jar",
                    r"C:\Libs\mcp\slf4j-nop-2.0.17.jar",
                    r"C:\Libs\mcp\json-schema-validator-1.5.8.jar",
                    r"C:\Libs\mcp\itu-1.14.0.jar",
                    r"C:\Libs\mcp\reactive-streams-1.0.4.jar",
                    r"C:\Libs\mcp\reactor-core-3.7.4.jar",
                    r"C:\Libs\nSoftware\v24\jar\IPWorksCData.jar"
                ]),
                "mcp.Program",
                "CData_Monday_MCP"
            ],
            "transport": "stdio",
            "env": {},
            "is_native": False,
            "description": "Custom CData Monday MCP Server (class-based, stdio) - Debug Build"
        },
        "cdata_bc365_mcp_custom": {
            "command": "C:\\Program Files\\Java\\jdk-21\\bin\\java.exe",
            "args": [
                "-javaagent:C:\\Program Files\\JetBrains\\IntelliJ IDEA Community Edition 2024.2.3\\lib\\idea_rt.jar=50924:C:\\Program Files\\JetBrains\\IntelliJ IDEA Community Edition 2024.2.3\\bin",
                "-Dfile.encoding=UTF-8",
                "-Dsun.stdout.encoding=UTF-8",
                "-Dsun.stderr.encoding=UTF-8",
                "-cp",
                ";".join([
                    "C:\\dev\\drivers\\Release\\projects\\ProviderDynamics365BusinessCentral_mcp\\out\\production\\providerdynamics365businesscentral",
                    "C:\\Libs\\RSSBus\\servlet-api-3.0.jar",
                    "C:\\Libs\\mcp\\mcp-0.17.1.jar",
                    "C:\\Libs\\mcp\\mcp-core-0.17.1.jar",
                    "C:\\Libs\\mcp\\mcp-json-jackson2-0.17.1.jar",
                    "C:\\Libs\\mcp\\jackson-annotations-2.19.4.jar",
                    "C:\\Libs\\mcp\\jackson-core-2.19.4.jar",
                    "C:\\Libs\\mcp\\jackson-databind-2.19.4.jar",
                    "C:\\Libs\\mcp\\jackson-dataformat-yaml-2.19.4.jar",
                    "C:\\Libs\\mcp\\slf4j-api-2.0.17.jar",
                    "C:\\Libs\\mcp\\slf4j-nop-2.0.17.jar",
                    "C:\\Libs\\mcp\\json-schema-validator-2.0.1.jar",
                    "C:\\Libs\\mcp\\itu-1.14.0.jar",
                    "C:\\Libs\\mcp\\reactive-streams-1.0.4.jar",
                    "C:\\Libs\\mcp\\reactor-core-3.7.4.jar",
                    "C:\\Libs\\mcp\\snakeyaml-2.3.jar",
                    "C:\\Libs\\nSoftware\\v24\\jar\\IPWorksCData.jar"
                ]),
                "mcp.Program",
                "BC365"
            ],
            "transport": "stdio",
            "env": {},
            "is_native": False,
            "description": "Custom CData Dynamics 365 Business Central MCP Server (class-based, stdio) - Debug Build"
        },
        "cdata_bc365_mcp": {
            "command": r"C:\Program Files\CData\CData Code Assist MCP for Microsoft Dynamics 365 Business Central 2025\jre\bin\java.exe",
            "args": [
                "-Dfile.encoding=UTF-8",
                "-jar",
                r"C:\Program Files\CData\CData Code Assist MCP for Microsoft Dynamics 365 Business Central 2025\lib\cdata.mcp.d365businesscentral.jar",
                "BC365",
            ],
            "transport": "stdio",
            "is_native": False,
            "description": "CData Dynamics 365 Business Central MCP Server - SQL interface to MS Dynamics BC"
        },
    }
