# Current Task: Sprint 4 Shape Conversion

## Objective
Convert the new "Asset" and "Organization" shapes located in the SHACL repo into production-ready TypeScript classes.

## Scope
1. **Analyze:** - `SHACL_REPO/shapes/asset.ttl`
   - `SHACL_REPO/shapes/org.ttl`
2. **Generate:** - Create `Asset.ts` and `Organization.ts` in `TS_REPO/src/generated/models`.
3. **Refactor:** - Update the `index.ts` in the destination folder to export these new classes.

## Acceptance Criteria
- Code must pass `npm run lint`.
- The **QA Agent** must verify that `sh:minCount` constraints are enforced in the class constructor.
- Automated tests must be generated in `TS_REPO/tests/generated/` for each new class.

## Interaction Rule
- If a SHACL property uses a custom URI prefix not defined in the standard set, the **Developer Agent** must pause and ask for the prefix mapping.