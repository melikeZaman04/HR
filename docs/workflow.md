# Development Workflow

## Kanban Process

This project follows a Jira Kanban workflow for task management and code delivery.

### Workflow Stages

```
To Do → In Progress → Code Review → Done
```

1. **To Do**: Backlog of prioritized tasks
2. **In Progress**: Actively being developed
3. **Code Review**: Pull request submitted, awaiting approval
4. **Done**: Merged to main, deployed

## Branch Strategy

### Naming Convention

All feature branches follow this pattern:

```
feature/JIRA-XX-short-description
```

**Examples:**
- `feature/JIRA-12-add-cfo-agent`
- `feature/JIRA-34-implement-scenario-retrieval`
- `feature/JIRA-56-docker-compose-setup`

### Development Flow

1. **Pick Task**: Move Jira card from "To Do" to "In Progress"
2. **Create Branch**: 
   ```bash
   git checkout -b feature/JIRA-XX-description
   ```
3. **Develop**: Implement changes following clean architecture principles
4. **Test Locally**:
   ```bash
   pytest -q
   ```
5. **Push Branch**:
   ```bash
   git push origin feature/JIRA-XX-description
   ```
6. **Open Pull Request**: Move Jira card to "Code Review"

## Pull Request Requirements

Every PR must include:

- **Linked Jira Task**: Reference `JIRA-XX` in PR title/description
- **Clear Description**: 
  - What was changed
  - Why it was changed
  - How to test it
- **CI Status**: All GitHub Actions checks must pass
- **Code Review**: At least 1 approval required

### PR Template

```
## Jira Task
JIRA-XX: [Task Title]

## Changes
- Added/Modified/Fixed [component]
- Updated [file/module]

## Testing
- [ ] Unit tests pass
- [ ] API tests pass
- [ ] Manual testing completed

## Checklist
- [ ] No breaking changes
- [ ] Documentation updated
- [ ] Clean architecture maintained
```

## Code Review Policy

### Reviewer Responsibilities
- Check code follows clean architecture principles
- Verify domain layer has no infrastructure dependencies
- Ensure all DB operations use repositories (no raw SQL)
- Confirm tests cover new functionality
- Validate SOLID principles are maintained

### Approval Criteria
- At least **1 approval** required to merge
- CI pipeline must be green
- No unresolved comments

### Merge Process
1. PR approved by reviewer(s)
2. CI passes
3. Squash and merge to `main`
4. Delete feature branch
5. Move Jira card to "Done"

## CI Pipeline

GitHub Actions runs on every PR:
- Install Python dependencies
- Run pytest suite
- Report status to PR

## Best Practices

- Keep PRs small and focused (single task)
- Write meaningful commit messages
- Update tests alongside code changes
- Keep domain logic pure (no infrastructure coupling)
- Follow existing patterns (Repository, Factory, DI)
