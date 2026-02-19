# Project Resources

## Repositories
- **SHACL_REPO (Source):** `local://path/to/ontology-repo`
  - *Primary Branch:* `main`
  - *Target Folder:* `/shapes`
- **TS_REPO (Destination):** `local://path/to/typescript-library`
  - *Primary Branch:* `develop`
  - *Target Folder:* `/src/generated/models`

## Reference Materials
- **Examples:** `./examples/shacl-ts-pairs/` 
  - *Note:* Use `UserShape.ttl` -> `User.ts` as the gold standard for POJO structure.
- **Library Documentation:** See `./docs/shacl-js-standard.md` for the base class inheritance requirements.

## Environment Constraints
- **Runtime:** Node.js v22+
- **Compiler:** TypeScript 5.7+
- **Linter:** ESLint with Prettier