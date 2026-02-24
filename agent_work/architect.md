```markdown
# SHACL to TypeScript Solid Object Conversion Guide

## Overview

This document serves as a comprehensive guide for converting SHACL shape files into Solid objects using TypeScript and the RDF/JS Wrapper library. The goal is to enable developers to implement SHACL-to-Solid conversions without needing additional resources.

## SHACL to TypeScript Mapping Reference Table

| SHACL Construct    | TypeScript Pattern                                                              | Notes                                                                                         |
|--------------------|---------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| `sh:NodeShape`     | TypeScript `class` extending `TermWrapper`                                      | Represents the RDF node as a TypeScript class.                                                 |
| `sh:path`          | Property Name derived from URI                                                  | Used as the RDF predicate for properties.                                                      |
| `sh:datatype`      | ValueMapping (e.g., `xsd:string` -> `string`)                                   | Maps RDF literals to JavaScript primitives.                                                    |
| `sh:node`          | ObjectMapping to another `TermWrapper` class                                    | Used for properties pointing to other shapes.                                                 |
| `sh:minCount: 1`   | Non-nullable property                                                           | Represents required fields.                                                                   |
| `sh:maxCount: 1`   | Singular values via `singular` or `singularNullable` methods                    | Ensures single-valued properties.                                                             |
| `sh:maxCount: >1`  | Array via `set` methods                                                         | Supports multiple values.                                                                     |

## Class Generation Rules

1. Each `sh:NodeShape` is translated into a TypeScript class extending `TermWrapper`.
2. The class must import necessary mappings and the RDF/JS Wrapper components.
3. Implement getter and setter methods for each property in the shape.

## Property Generation Rules

- **Required String Properties**: Use `singular()` for retrieval and `overwrite()` for storage.
- **Optional String Properties**: Use `singularNullable()` and `overwriteNullable()` for flexibility.
- **Required Object References**: Use `singular()` with `ObjectMapping`.
- **Optional Object References**: Leverage `singularNullable()` and `ObjectMapping`.
- **Array Properties**: Use `set()` methods to handle collections.

## Code Patterns

```typescript
import { TermWrapper, ValueMapping, ObjectMapping } from 'rdfjs-wrapper';

class Example extends TermWrapper {
  get exampleProperty(): string {
    return this.singular('example:predicate', ValueMapping.literalToString);
  }

  set exampleProperty(value: string) {
    this.overwrite('example:predicate', value, ValueMapping.stringToLiteral);
  }
}
```

## Naming Conventions

- Convert Label value to camelCase for property names. If Label is not provided, use the last segment of the URI.
- Omit namespace prefixes in TypeScript property names.

## Export Organization

Always update `mod.ts` to export newly created classes, ensuring they are available for use in the broader application context.

## Example Walkthroughs

### Group Example

**SHACL Shape**

```turtle
PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>

gs:GroupShape
  a sh:NodeShape ;
  sh:targetClass vcard:Group ;
  sh:property [ sh:path vcard:fn ; sh:datatype xsd:string ; sh:minCount 1 ] ;
  sh:property [ sh:path vcard:member ; sh:minCount 0 ; sh:class vcard:Individual ] .
```

**Resulting TypeScript Code**

```typescript
import { TermWrapper, ObjectMapping, ValueMapping } from "rdfjs-wrapper";
import { VCARD } from "../vocabulary/mod.js";

export class Group extends TermWrapper {
  get name(): string {
    return this.singular(VCARD.fn, ValueMapping.literalToString);
  }

  set name(value: string) {
    this.overwrite(VCARD.fn, value, ValueMapping.stringToLiteral);
  }

  get members(): Set<Person> {
    return this.objects(VCARD.member, ObjectMapping.as(Person), ObjectMapping.as(Person));
  }
}
```

### Meeting Example

**SHACL Shape**

```turtle
PREFIX cal: <http://www.w3.org/2002/12/cal/ical#>

ms:MeetingShape
  a sh:NodeShape ;
  sh:targetClass cal:Vevent ;
  sh:property [ sh:path cal:summary ; sh:datatype xsd:string ; sh:minCount 1 ] ;
  sh:property [ sh:path cal:location ; sh:datatype xsd:string ; sh:minCount 0 ] .
```

**Resulting TypeScript Code**

```typescript
import { TermWrapper, ValueMappings, TermMappings } from "rdfjs-wrapper";
import { ICAL } from "../vocabulary/mod.js";

export class Meeting extends TermWrapper {
  get summary(): string {
    return this.singular(ICAL.summary, ValueMappings.literalToString);
  }

  set summary(value: string) {
    this.overwrite(ICAL.summary, value, TermMappings.stringToLiteral);
  }

  get location(): string | undefined {
    return this.singularNullable(ICAL.location, ValueMappings.literalToString);
  }

  set location(value: string | undefined) {
    this.overwriteNullable(ICAL.location, value, TermMappings.stringToLiteral);
  }
}
```

## Common Patterns and Edge Cases

- **Nullable vs Non-nullable**: Always align `sh:minCount` with TypeScript's strict null checks.
- **Object Mapping**: Use `ObjectMapping` for properties pointing to nested objects.
- **Dataset Iteration**: Employ `DatasetWrapper` for handling collections of objects.

## Checklist for Developers

1. **Analyze SHACL Shape**: Identify all properties and constraints.
2. **Generate Class**: Create a TypeScript class for the NodeShape.
3. **Implement Properties**: Add getter and setter methods.
4. **Utilize Mappings**: Use ValueMapping and ObjectMapping as per data types.
5. **Update Exports**: Modify `mod.ts` with new class exports.
6. **Testing**: Ensure proper handling of RDF data and correct TypeScript types.

This guide should enable developers to perform SHACL-to-TypeScript transformations efficiently, allowing them to generate Solid-compatible objects with ease.
```