import sqlite3
import csv
import sys
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "mcp_analysis.db")

def execute_query(query, output_file=None):
    """
    Execute a SQL query and print results in CSV format
    
    Args:
        query: SQL query string to execute
        output_file: Optional file path to save CSV output (default: print to console)
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute(query)
        
        # Get column names
        column_names = [description[0] for description in cursor.description]
        
        # Fetch all results
        rows = cursor.fetchall()
        
        # Determine output destination
        if output_file:
            # Write to file
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(column_names)
                writer.writerows(rows)
            print(f"✓ Results saved to: {output_file}")
            print(f"  Total rows: {len(rows)}")
        else:
            # Write to console
            writer = csv.writer(sys.stdout)
            writer.writerow(column_names)
            writer.writerows(rows)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)

def execute_query_from_file(file_path, output_file=None):
    """
    Execute a SQL query from a file
    
    Args:
        file_path: Path to file containing SQL query
        output_file: Optional file path to save CSV output
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            query = f.read()
        
        print(f"Executing query from: {file_path}")
        execute_query(query, output_file)
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error reading file: {e}", file=sys.stderr)

def list_tables():
    """List all tables and views in the database"""
    query = """
        SELECT 
            type,
            name
        FROM sqlite_master 
        WHERE type IN ('table', 'view')
        ORDER BY type, name
    """
    print("\n=== TABLES AND VIEWS ===")
    execute_query(query)

def list_views():
    """List all views in the database"""
    query = """
        SELECT name
        FROM sqlite_master 
        WHERE type = 'view'
        ORDER BY name
    """
    print("\n=== AVAILABLE VIEWS ===")
    execute_query(query)

def interactive_mode():
    """Interactive query mode"""
    print("\n" + "="*80)
    print("INTERACTIVE QUERY MODE")
    print("="*80)
    print("Enter your SQL query (type 'exit' to quit, 'tables' to list tables)")
    print("For multi-line queries, end with semicolon (;)")
    print("="*80 + "\n")
    
    query_buffer = []
    
    while True:
        try:
            if not query_buffer:
                line = input("SQL> ")
            else:
                line = input("...> ")
            
            if line.strip().lower() == 'exit':
                print("👋 Goodbye!")
                break
            elif line.strip().lower() == 'tables':
                list_tables()
                continue
            elif line.strip().lower() == 'views':
                list_views()
                continue
            elif line.strip().lower() == 'clear':
                query_buffer = []
                print("Query buffer cleared.")
                continue
            
            query_buffer.append(line)
            
            # Check if query is complete (ends with semicolon)
            if line.strip().endswith(';'):
                query = ' '.join(query_buffer)
                print()  # Empty line before results
                execute_query(query)
                print()  # Empty line after results
                query_buffer = []
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Execute SQL queries on MCP analysis database and output as CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python query_executor.py
  
  # Execute a query directly
  python query_executor.py -q "SELECT * FROM Full_Report"
  
  # Execute query from file
  python query_executor.py -f query.sql
  
  # Save results to CSV file
  python query_executor.py -q "SELECT * FROM Full_Report" -o results.csv
  
  # List all tables and views
  python query_executor.py --tables
  
  # List all views
  python query_executor.py --views
        """
    )
    
    parser.add_argument('-q', '--query', help='SQL query to execute')
    parser.add_argument('-f', '--file', help='File containing SQL query')
    parser.add_argument('-o', '--output', help='Output CSV file (default: print to console)')
    parser.add_argument('--tables', action='store_true', help='List all tables and views')
    parser.add_argument('--views', action='store_true', help='List all views')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}", file=sys.stderr)
        print("Please run the importer script first to create the database.", file=sys.stderr)
        sys.exit(1)
    
    # Execute based on arguments
    if args.tables:
        list_tables()
    elif args.views:
        list_views()
    elif args.query:
        execute_query(args.query, args.output)
    elif args.file:
        execute_query_from_file(args.file, args.output)
    elif args.interactive or len(sys.argv) == 1:
        # Default to interactive mode if no arguments
        interactive_mode()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()