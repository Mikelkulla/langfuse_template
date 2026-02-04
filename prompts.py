"""
Test prompt library for MCP agent benchmarking.

Each prompt is a tuple of (prompt_id: int, prompt_text: str).
Prompts are grouped by target server / domain for clarity.
"""

# ====================== MONDAY.COM / JIRA PROMPTS ======================
MONDAY_PROMPTS = [
    (1, "Assign Casey Thompson to all future projects in my company projects. Workspace MCP_M_K. Date: 21 Nov 2025"),
    (2, "Workspace MCP_M_K. Can you check the Recruitment Pipeline board and tell me how many candidates are currently in the 'In Interview Process' stage, along with their names and target fill dates?"),
    (3, "Please update my status on the Company Projects board for the project 'Blockchain Supply Chain Tracking' to 'In Progress' and assign it a high priority. Also, let me know the current budget remaining for that project. Workspace MCP_M_K."),
    (4, "Create a board called 'Website Refresh'. Workspace MCP_M_K."),
    (5, "Board 'Website Refresh'. Add a status column with options: To Do, In Progress, Review, Done. Workspace MCP_M_K."),
    (6, "Create a new AI column with the Detect Sentiment action, and classify all feedback to Positive, Negative, or Neutral. Workspace MCP_M_K. Board 'Website Refresh'."),
    (7, "Board 'Website Refresh'. Add a new task called 'Update homepage content.' Workspace MCP_M_K."),
    (8, "Find all items in the 'Company Projects' board that contain 'Customer' in the name. Workspace MCP_M_K."),
    (9, "Add a comment to the 'Design new banner ads for display network' task: 'Waiting for final copy from the content team.' Workspace MCP_M_K."),
    (10, "Create an update on the Website Refresh project on item 'Update homepage content' about the delay and tag everyone on this workspace. Workspace MCP_M_K."),
    (11, "Board Company Projects. What items are currently in progress? Workspace MCP_M_K."),
    (12, "What changed in the marketing board over the month? Workspace MCP_M_K."),
    (13, "Set up a complete product launch project: create a board called 'Product Launch Q4 Dynamic', add columns for status, assignee, priority, due date, and budget, then create initial tasks for research (5), design (5), development (5), and marketing phases (5). Workspace MCP_M_K. (Use run_nonquery with 'RESET SCHEMA CACHE' if you face cache problems)"),
    (14, "Create a client onboarding board with custom columns for client name, contact info, onboarding stage, and next action required. Workspace MCP_M_K."),
    (15, "Create three new tasks in the Website Refresh board: 'Fix login timeout issue', 'Update API documentation for v2.0', and 'Review security patches for Q4'. Workspace MCP_M_K."),
    (16, "Search for all items containing 'Create' across all boards (Workspace MCP_M_K), then create a summary report of their current status. Workspace MCP_M_K. (Get instcutions first.)"),
    (17, "Generate a monthly activity report for my 'Company Projects' board showing what happened in the last 30 days. Workspace MCP_M_K."),
    (18, "Create a new client project setup: first create a board called 'Client Project - ABC Corp', add status and priority columns, then create an initial task called 'Project kickoff meeting'. Workspace MCP_M_K."),
    (19, "Set up a bug tracking system: create a board called 'Bug Tracker', add columns for severity, assignee, reported by, and fix status, then create sample bug reports for 'Login timeout', 'Payment processing error', and 'Mobile app crash'. Workspace MCP_M_K."),
    (20, "Organize my marketing campaign planning: create a board called 'Q4 Marketing Campaign', add tasks for content creation (5), design (5), social media (5), and analytics (5). (Workspace MCP_M_K)"),
    (21, "Create a project specification document attached to the 'Client onboarding automation' task with the following sections: overview, requirements, timeline, and deliverables. (Workspace MCP_M_K, Board 'Company Projects')"),
    (22, "Create a new document in my 'MCP_M_K' workspace with our complete API documentation and usage examples."),
    (23, """Create a troubleshooting guide document attached to the 'Customer Support Process' item in Board Website Refresh. Quick Troubleshooting Guide – Coffee Machine 3000
    Issue 1: Machine won't turn on
    Check if the power cable is plugged into the wall socket.
    Ensure the "Power" button is held for 3 seconds.
    If still off, try sacrificing a teaspoon of coffee beans to the machine gods (optional).
    Issue 2: Coffee tastes like burnt socks
    Clean the filter with warm water and vinegar.
    Replace old beans.
    Issue 3: Machine makes loud noises
    Confirm no metal spoons were left inside the water tank.
    Check if the grinder is clogged.

    """),
    (24, "Create a status overview - find all items marked as 'Stuck' or 'Blocked' across all my boards and provide details about each one. Workspace MCP_M_K."),
    (25, "Analyze my team's current workload by finding all active tasks and their current status across all boards."),
    (26, "Create a 'Support Requests' board. Then create 15 items supposedly from Support mentioning 'customer satisfaction' in some of them. Workspace MCP_M_K. (Max 2 tool use at a time)"),
    (27, "Track customer feedback - find all items in my 'Support 1, Support 2, Support 3, Support 4' board that mention customer satisfaction, then create a summary report. Workspace MCP_M_K. (Max 2 tool use at a time)"),
    (28, "Show me all overdue items across my project boards."),
    (29, "Set up a new client relationship tracking system - create a board for 'Client - TechCorp Inc', add appropriate columns for contact info, project status, and deliverables."),
    (30, "Create a comprehensive project template - make a board called 'Project Template' with standard columns for task management, team coordination, and progress tracking."),
    (31, "Organize project deliverables - create tasks for 'Proposal submission', 'Contract review', and 'Project kickoff' on the TechCorp board with detailed descriptions."),
    (32, "Create an item called 'User dashboard redesign specifications' in the Product board, then create a detailed requirements document attached to it."),
    (33, "Create a campaign board, add tasks for content creation, graphic design, social media scheduling, email campaign setup, and analytics tracking with detailed descriptions for each area."),
    (34, "Set up a client approval workflow template: create items for 'Design mockup review', 'Content approval', and 'Final sign-off' in the client board with comprehensive documentation for each step."),
    (35, "On workspace MCP_M_K what changed in the marketing board during NOVEMBER 2025."),
    (36, """Generate a comprehensive Q4 2025 Executive Dashboard Report from my MCP_M_K workspace that includes:

1. **PROJECT PORTFOLIO ANALYSIS**
   - Retrieve all projects from the "Company Projects" board
   - Calculate total budget allocation across all projects
   - Break down projects by status (In Progress, Completed, On Hold, Planning)
   - Identify high-priority projects with budgets over $200,000
   - List projects due in the next 90 days
   - Group projects by department if available

2. **BUG TRACKING METRICS**
   - Query the "Bug Tracker CData" board for all active bugs
   - Categorize bugs by severity level
   - Identify bugs by fix status
   - Show which bugs are assigned vs unassigned
   - Calculate resolution metrics

3. **RECRUITMENT PIPELINE STATUS**
   - Extract all candidates from "Recruitment Pipeline" board
   - Count candidates by recruitment status
   - List positions with target fill dates in December 2025
   - Identify offers extended and recent hires
   - Show average time-to-fill metrics if calculable

4. **CROSS-BOARD ANALYTICS**
   - Join data across multiple boards where relevant
   - Calculate resource allocation (people working across projects and recruitment)
   - Identify potential bottlenecks (projects on hold vs active bugs)
   - Generate executive summary with key insights

Format the report with:
- Executive summary at the top
- Visual data representations (tables, key metrics)
- Risk indicators (overdue projects, critical bugs, urgent hiring needs)
- Actionable recommendations

**Note:** Use only one tool at a time"""),
    (37, """# Task: Batch Create 100 Invoice Items in Monday.com using Native Monday MCP GraphQL

## Context
You are working with a Monday.com board called "Invoice Management" (Board ID: 18391110342) within the "Finance Operations" workspace. You need to create 100 realistic invoice items using the Monday.com GraphQL API with batch operations.

## Board Column Mappings
Use these exact column IDs from the Invoice Management board:
- **Invoice Number**: `text_mkybvqme` (Text column)
- **Invoice Type**: `dropdown_mkybqw0w` (Dropdown column)
- **Invoice Date**: `date_mkybb5xm` (Date column)
- **Due Date**: `date_mkybbn1ea` (Date column)
- **Vendor/Customer Name**: `text_mkybs0w5` (Text column)
- **Subtotal**: `numeric_mkybja3h` (Numbers column)
- **Total Amount**: `numeric_mkybbg2k` (Numbers column)

## Invoice Type Values
Use these exact dropdown values:
- "Accounts Payable (AP)"
- "Accounts Receivable"
- "Credit Memo"
- "Debit Memo"

## Instructions

### Step 1: Determine Starting Invoice Number
First, query the board to find the last invoice number.
Start from the next sequential number (e.g., if last is INV-2025-230, start at INV-2025-231).

### Step 2: Create Items in Batches
Use Monday.com GraphQL API with **aliased mutations** to create multiple items in a single API call. Due to API complexity limits, split 100 items into 4 batches of 25 items each.

### Batch Structure Template
```graphql
mutation {
  item1: create_item(
    board_id: 18391110342,
    item_name: "[ITEM_NAME]",
    column_values: "{
      \\"text_mkybvqme\\":\\"[INVOICE_NUMBER]\\",
      \\"dropdown_mkybqw0w\\":{\\"labels\\":[\\"[INVOICE_TYPE]\\"]},
      \\"date_mkybb5xm\\":\\"[INVOICE_DATE_YYYY-MM-DD]\\",
      \\"date_mkybbn1ea\\":\\"[DUE_DATE_YYYY-MM-DD]\\",
      \\"text_mkybs0w5\\":\\"[VENDOR_CUSTOMER_NAME]\\",
      \\"numeric_mkybja3h\\":[SUBTOTAL_NUMBER],
      \\"numeric_mkybbg2k\\":[TOTAL_AMOUNT_NUMBER]
    }"
  ) { id }
  item2: create_item(...) { id }
  ...
  item25: create_item(...) { id }
}
```

### Step 3: Data Generation Requirements

**Invoice Numbers:**
- Format: `INV-2025-XXX` (sequential)
- Example: INV-2025-231, INV-2025-232, etc.

**Invoice Types Distribution:**
- ~45% Accounts Payable (AP)
- ~35% Accounts Receivable
- ~12% Credit Memo (negative amounts)
- ~8% Debit Memo

**Dates:**
- Invoice Date: Spread across 2025 (April through December)
- Due Date: Typically 30 days after Invoice Date
- Format: YYYY-MM-DD (e.g., "2025-04-15")
- Current date reference: December 5, 2025

**Item Names (realistic examples):**
- AP: "Software License - [Vendor]", "Office Supplies - [Month]", "Cloud Services", "Legal Fees", "Insurance Premium"
- AR: "Consulting Services - [Client]", "Software Development", "Marketing Campaign", "Training Services"
- Credit Memo: "Refund - [Reason]", "Billing Adjustment", "Overpayment Credit", "Return Credit"
- Debit Memo: "Late Fee", "Additional Services", "Overtime Charges", "Rush Order Fee"

**Vendor/Customer Names (realistic examples):**
- Vendors: "Adobe Systems Inc", "Amazon Web Services", "Microsoft Corporation", "Staples Inc", "Comcast Business"
- Customers: "Acme Corporation", "TechStart Industries", "Global Retail Solutions", "Enterprise Solutions Ltd"

**Amounts:**
- AP: $200 - $25,000
- AR: $5,000 - $150,000
- Credit Memo: Negative amounts (-$200 to -$5,000)
- Debit Memo: $200 - $5,000
- Total Amount: Subtotal + tax (typically 8.5%) or with discounts

### Step 4: Execute Batches
Execute 4 separate GraphQL mutations (25 items each) using the `monday-api-mcp-dynamic:all_monday_api` tool:

```
Batch 1: Items 1-25 (Invoice numbers 231-255)
Batch 2: Items 26-50 (Invoice numbers 256-280)
Batch 3: Items 51-75 (Invoice numbers 281-305)
Batch 4: Items 76-100 (Invoice numbers 306-330)
```

## Expected Output Format
Each batch should return JSON with item IDs:
```json
{
  "item1": {"id": "10713xxxxx"},
  "item2": {"id": "10713xxxxx"},
  ...
}
```

## Critical Rules
1. **Always include due dates** - calculate as Invoice Date + 30 days
2. **Use exact column IDs** - do not modify column_values keys
3. **JSON escaping** - properly escape quotes in column_values JSON string
4. **Invoice Type format** - use exact labels including "(AP)" suffix
5. **Negative amounts** - Credit Memos must have negative subtotal and total
6. **Date format** - strictly YYYY-MM-DD
7. **Sequential numbering** - no gaps in invoice numbers
8. **Realistic data** - use real company names and realistic amounts

## Example Complete Item
```graphql
item1: create_item(
  board_id: 18391110342,
  item_name: "Cloud Hosting Services - AWS",
  column_values: "{
    \\"text_mkybvqme\\":\\"INV-2025-231\\",
    \\"dropdown_mkybqw0w\\":{\\"labels\\":[\\"Accounts Payable (AP)\\"]},
    \\"date_mkybb5xm\\":\\"2025-04-10\\",
    \\"date_mkybbn1ea\\":\\"2025-05-10\\",
    \\"text_mkybs0w5\\":\\"Amazon Web Services\\",
    \\"numeric_mkybja3h\\":8750,
    \\"numeric_mkybbg2k\\":8750
  }"
) { id }
```

## Success Criteria
All 100 items created successfully
Sequential invoice numbering (no gaps)
All dates included (Invoice Date + Due Date)
Realistic distribution of invoice types
Proper amounts (positive for AP/AR/Debit, negative for Credit)
All items appear in the board immediately after creation

Now execute this task by creating 100 invoice items following these exact specifications.
This prompt provides:
1. **Exact column mappings** with IDs
2. **Clear data requirements** and distributions
3. **Step-by-step execution plan**
4. **GraphQL mutation template** with proper syntax
5. **Realistic examples** for all fields
6. **Verification steps** to confirm success
7. **Critical rules** to avoid common mistakes
8. **Expected output format**"""),
    (38, "In Finance Operations, at invoice management, find and SHOW the invoices of 2025 August of type Accounts Receivable"),
    (39, "In Finance Operations, at invoice management, make me a table of total amount of invoices grouped in months for 2025. "),
    (40, "In Finance Operations, at invoice management, update invoices duedate to 31 dec 2025 of all invoices of invoice date in 2024."),
    (41, "In Finance Operations, at invoice management, make me a report of Sum of Total Amount grouped by Invoice Type"),
    (42, "In Finance Operations, at invoice management, make a report of Total Amount for each moth invoices from 2024 until 2026."),
    (43, "Set the working hours per day to 12 hours"),
    (44, "Run the get_columns tool. Just prints me the resutls"),
]

# ====================== MS DYNAMICS 365 BUSINESS CENTRAL PROMPTS ======================
BC365_PROMPTS = [
        # This are prompts for MS Dynamics Busines Central MCP server
        (45, """# BC365 MCP Connector Test Prompt

## Overview
This prompt is designed to comprehensively test the BC365 MCP connector's metadata retrieval speed, business logic capabilities, and overall performance across different scenarios.

## Test Scenario: Business Intelligence Dashboard Creation

**Prompt:**

"I need you to create a comprehensive Business Intelligence report for CRONUS USA, Inc. using the BC365 connector. This report should demonstrate advanced business logic and test the connector's capabilities across multiple dimensions. Please perform the following analysis:

### 1. Metadata Discovery & Performance Test
- Retrieve and display the complete schema structure showing all available tables
- Get detailed metadata for the top 10 most business-critical tables (focus on Customers, SalesInvoices, Items, G_LEntries, PurchaseInvoices, etc.)
- Measure and comment on the speed of metadata retrieval operations

### 2. Customer Analysis Module
Create a customer performance analysis that includes:
- Top 10 customers by balance and credit limit utilization
- Customer segmentation based on sales volume and payment behavior
- Geographic distribution analysis of customers
- Customer growth trends and patterns

### 3. Sales Performance Analytics
Develop comprehensive sales analytics including:
- Monthly and quarterly sales trends for the current and previous year
- Sales performance by salesperson with rankings
- Invoice analysis: average invoice size, payment terms distribution
- Revenue breakdown by customer segments
- Outstanding receivables analysis with aging buckets

### 4. Financial Dashboard Components
Build financial KPIs and metrics:
- Cash flow analysis from GL entries
- Profit and loss indicators from available financial data
- Budget vs actual analysis if budget data is available
- Key financial ratios and performance indicators

### 5. Operational Efficiency Metrics
Calculate operational metrics such as:
- Invoice processing efficiency
- Customer payment patterns and DSO calculations
- Sales cycle analysis
- Data quality assessment across key tables

### 6. Advanced Query Performance Testing
Execute complex queries that test:
- JOIN operations across multiple large tables
- Aggregation performance on large datasets
- Date range filtering and grouping operations
- Subquery and CTE performance where supported

### 7. Data Integration Scenarios
Simulate real business scenarios:
- Create a month-end reporting process
- Build a customer onboarding data validation routine
- Develop a sales commission calculation workflow
- Generate executive summary statistics

### 8. Error Handling & Edge Cases
Test the connector's robustness:
- Query tables with zero records
- Handle potential null values and data inconsistencies  
- Test with various date formats and ranges
- Validate data type handling across different field types

### Success Criteria:
- Metadata operations complete within reasonable time (document actual times)
- All queries execute successfully with meaningful results
- Complex business logic is implemented correctly
- Performance is acceptable for production use
- Error handling is graceful and informative

Please execute this comprehensive test and provide:
1. Detailed performance metrics for each operation
2. Business insights derived from the data analysis
3. Any limitations or issues encountered
4. Recommendations for optimal usage patterns
5. A summary of the connector's readiness for production business intelligence workflows

Additionally, create visualizable data outputs that could be used with BI tools like Power BI, Tableau, or similar platforms."

## Expected Outcomes

This test prompt should trigger:
- **Metadata Speed Tests**: Multiple calls to BC365_get_metadata with timing analysis
- **Complex Query Execution**: Advanced SQL operations testing performance
- **Business Logic Implementation**: Real-world business calculations and analytics
- **Error Handling Validation**: Edge case testing and robustness checks
- **Data Integration Patterns**: Multi-table joins and complex business scenarios
- **Performance Benchmarking**: Quantitative assessment of connector capabilities

## Performance Metrics to Track

1. **Metadata Retrieval Speed**:
   - Simple metadata discovery time
   - Detailed schema inspection time
   - Large table metadata fetching performance

2. **Query Execution Performance**:
   - Simple SELECT operations
   - Complex JOIN operations
   - Aggregation query performance
   - Large dataset handling

3. **Business Logic Complexity**:
   - Multi-step analytical processes
   - Cross-functional business calculations
   - Data transformation and enrichment

4. **Error Recovery**:
   - Graceful handling of missing data
   - Performance under edge conditions
   - Connection stability during extended operations

## Usage Instructions

1. **For Speed Testing**: Run this prompt and monitor the time taken for each major operation
2. **For Feature Testing**: Verify that all requested analyses can be completed successfully
3. **For Load Testing**: Scale up the operations by requesting larger date ranges or more complex calculations
4. **For Integration Testing**: Use the outputs to test downstream BI tool compatibility

This comprehensive test will provide a thorough evaluation of your BC365 MCP connector's capabilities and help identify any performance bottlenecks or feature limitations.
         
         *Note*: Use only one tool at a time. Do not attempt parallel tool calls."""),
        (46, "Show me our top 5 customers by sales volume this year. LLM Note: Use only one tool at a time."),
        (47, "What's our total outstanding receivables right now?. LLM Note: Use only one tool at a time. Do not use _instructions."),
        (48, "Give me a list of all overdue invoices with customer names and amounts. LLM Note: Use only one tool at a time. Get instructions first."),
        (49, "How much revenue did we generate last month? LLM Note: Use only one tool at a time."),
        (50, "Show me which customers haven't paid their invoices yet. LLM Note: Use only one tool at a time. Get instructions first."),
        (51, "What's our current inventory value for chairs and tables? LLM Note: Use only one tool at a time. Get instructions first."),
        (52, "List all sales invoices from School of Fine Art - they're asking about their account. LLM Note: Use only one tool at a time."),
        (53, "How many items do we have in stock for each product category?"),
        (54, "What's our average invoice amount this quarter?"),
        (55, "Show me all customers with credit limits under $1000"),
        (56, "Give me the sales performance for salesperson 'JO' this year"),
        (57, "What invoices were created in the last 30 days?"),
        (58, "Show me our gross profit margin by product category"),
        (59, "List all customers in the United States with their phone numbers"),
        (60, "What's the total value of unpaid invoices for Relecloud?"),
        (61, "Give me a quick summary of today's GL entries"),
        (62, "Show me which items have the highest sales volume"),
        (63, "What's our Days Sales Outstanding (DSO) calculation?"),
        (64, "List all purchase orders that haven't been received yet"),
        (65, "Show me customers who haven't made any purchases this year. LLM Note: Use only one tool at a time.")
]

# Combined list for backward compatibility
ALL_PROMPTS = MONDAY_PROMPTS + BC365_PROMPTS
