# System Documentation

## Task Management Architecture

### Todoist Integration

- **Purpose**: Daily actionable task management
- **Use Cases**:
  - Time-sensitive tasks
  - Today's actions
  - Recurring tasks
  - Quick mobile capture
  - Tasks with deadlines
  - Context-based actions

### Markdown Files

- **Purpose**: Knowledge management and strategic planning
- **Use Cases**:
  - Project documentation
  - Long-term planning
  - Life assessments
  - Reference materials
  - Decision records
  - Goals and OKRs

## Directory Structure

```
.
└── memory/                 # Knowledge base
    ├── assessments/        # Life area evaluations
    ├── templates/          # Standard formats
    ├── decisions/          # Major choices
    ├── objectives/         # Goals and OKRs
    ├── reference/          # Support materials
    └── gtd/                # Get Things Done (Task Management)
        ├── inbox.md        # Initial capture point
        ├── projects.md     # Project plans and documentation
        ├── someday.md      # Future possibilities
        ├── waiting.md      # Delegated items
        └── next-actions.md # Context-based actions
```

## Processing Flow

1. **Capture**

   - Use inbox.md for initial collection
   - Quick capture in Todoist when mobile
   - Gather all inputs in one place

2. **Process**

   - Review inbox daily
   - For each item, decide:
     - Actionable today → Todoist
     - Project planning → projects.md
     - Future possibility → someday.md
     - Delegated → waiting.md
     - Reference → memory/reference/

3. **Review**
   - Daily: Process inbox, check Todoist
   - Weekly: Review all lists, update docs
   - Monthly: OKR review, clean reference
   - Quarterly: Full life assessment

## Integration Points

1. **Project Management**

   - Keep project details in markdown
   - Create next actions in Todoist
   - Link between tasks and docs
   - Update during reviews

2. **Reference System**

   - Store knowledge in markdown
   - Link from Todoist when needed
   - Organize by life area
   - Regular cleanup

3. **Goal Tracking**
   - OKRs in markdown
   - Action items in Todoist
   - Regular progress updates
   - Quarterly assessments

## Best Practices

1. **Task Management**

   - One item per line
   - Clear next actions
   - Include context
   - Set realistic dates

2. **Documentation**

   - Use templates
   - Regular updates
   - Clear structure
   - Version control

3. **Reviews**
   - Follow schedules
   - Update all systems
   - Check alignment
   - Clean as you go
