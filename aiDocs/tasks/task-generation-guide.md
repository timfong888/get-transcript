# Task Generation Guide

## Instructions
1. Create a task file in `/tasks/remote-agent-tasks-{number}.md` matching the prompt number
2. Include date and branch fields at the top
3. Create a git branch named `remote-agent-{number}` matching the prompt number
4. Break down the project into clear, actionable tasks
5. For each task, as it is completed, mark it as completed in the task list
6. Track progress and document implementation decisions
7. Use the MCP servers for up to date documentation.  The settings and key references are found in `aiDocs/mcp_servers.md`

## Template
```markdown
# Remote Agent Tasks {number}

**Date:** YYYY-MM-DD
**Branch:** remote-agent-{number}
**Prompt:** remote-agent-prompt-{number}

## Overview
Brief project description (2-3 sentences)

## Tasks
### Setup
- [ ] Create branch `remote-agent-{number}`
- [ ] Task 1: Description
- [ ] Task 2: Description

### Implementation
- [ ] Task 3: Description
- [ ] Task 4: Description

### Testing
- [ ] Task 5: Description
- [ ] Task 6: Description

## Progress
| Task | Status | Notes | Completed |
|------|--------|-------|-----------|
| Create branch |        |       |           |
| 1    |        |       |           |
| 2    |        |       |           |

## Implementation Notes
### Create branch
- Command used:
- Branch created:

### Task 1
- Approach:
- Challenges:
- Solution:
```