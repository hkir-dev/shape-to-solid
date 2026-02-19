# Transformation Rules: SHACL to TypeScript POJO

## 1. Structural Mapping
- `sh:NodeShape` maps to a TypeScript `class`.
- `sh:targetClass` should be stored as a static property `rdfType` in the class.
- All classes must extend the base class `ShaclPojo` from the `shacl-js` library.

## 2. Property Mapping
| SHACL Property | TypeScript Equivalent | Notes |
| :--- | :--- | :--- |
| `sh:path` | Property Name | Convert `camelCase` if the URI is `snake_case`. |
| `sh:datatype` | Primitive Type | `xsd:string` -> `string`, `xsd:integer` -> `number`. |
| `sh:node` | Class Reference | If a property points to another shape, use that Class type. |
| `sh:minCount: 1` | Required | Remove `?` or `| undefined`. |
| `sh:maxCount: 1` | Single Value | Direct type (e.g., `name: string`). |
| `sh:maxCount: >1` | Array | Use `Array<T>` (e.g., `aliases: string[]`). |

## 3. POJO Pattern Requirements
- **Encapsulation:** All properties must be `private`.
- **Accessors:** Provide public `get` and `set` methods.
- **Validation:** The `set` method should include a basic type check if the input doesn't match the TS type.
- **JSON-LD:** Include a `toJSON()` method that returns the object mapped to JSON-LD context.