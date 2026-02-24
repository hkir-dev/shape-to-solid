# Transformation Rules: SHACL to Solid Objects

## Purpose
This document provides guidelines for CrewAI agents to convert SHACL shape files into Solid objects. Solid objects are TypeScript objects generated using the RDF/JS Wrapper library. The RDF/JS Wrapper library enables idiomatic JavaScript object-oriented programming over RDF with TypeScript support.

## 1. Class Mapping
- Each `sh:NodeShape` maps to a TypeScript `class`.
- Classes must extend the `TermWrapper` class from the RDF/JS Wrapper library.
- Each class requires a `Term`, a `Dataset`, and a `DataFactory` to be instantiated.

## 2. Property Mapping
| SHACL Property | Solid Object Equivalent | Notes |
| :--- | :--- | :--- |
| `sh:path` | Property Name | Use the URI as the RDF property for the mapping. |
| `sh:datatype` | ValueMapping | Map RDF literals to JavaScript primitives (e.g., `xsd:string` -> `string`, `xsd:integer` -> `number`). |
| `sh:node` | ObjectMapping | Map to another `TermWrapper` class if the property points to another shape. |
| `sh:minCount: 1` | Required Property | Ensure the property is not nullable. |
| `sh:maxCount: 1` | Singular Value | Use `singular` or `singularNullable` methods. |
| `sh:maxCount: >1` | Array | Use `set` methods for multiple values. |

## 3. Implementation Guidelines
- **Encapsulation:** All properties should be accessed via `get` and `set` methods.
- **Value Mapping:** Use `ValueMapping` for primitive values (e.g., `literalToString`, `literalToNumber`).
- **Object Mapping:** Use `ObjectMapping` for nested objects.
- **Validation:** Implement basic validation in `set` methods to ensure type safety.
- **Dataset Mutation:** Ensure that all property changes mutate the underlying RDF dataset.
- Solid Objects should be POJOs (Plain Old JavaScript Objects) and should not contain any methods that perform business logic or side effects beyond managing RDF data.
- Rely on the utility methods (such as singular and checking value is not null) to do what they need, including validating and throwing exceptions. Assume null value check and exception weill be handled by the utility methods, so you don't need to add extra checks in the set methods.
- If name is required use singular and overwrite method, if name is optional use singularNullable and overwriteNullable methods.
- If property is an array oj objects, consider using ObjectMapping.as() functionality to map the array of RDF terms to an array of objects.
- For list objects don't generate add and delete item functions, instead use set method to set the whole list at once.
- Don't generate constructors to the classes, instead rely on the default constructor provided by the TermWrapper class.

## 4. Example: Person Class

### SHACL Definition
```turtle
PREFIX ex: <https://example.org/>

ex:PersonShape
  a sh:NodeShape ;
  sh:targetClass ex:Person ;
  sh:property [
    sh:path ex:name ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
  ] ;
  sh:property [
    sh:path ex:friend ;
    sh:node ex:PersonShape ;
    sh:maxCount 1 ;
  ] .
```

### Solid Object Implementation
```typescript
import { TermWrapper, ValueMapping, ObjectMapping } from "rdfjs-wrapper";

class Person extends TermWrapper {
  get name() {
    return this.singular("https://example.org/name", ValueMapping.literalToString);
  }

  set name(value: string) {
    this.overwrite("https://example.org/name", value, ValueMapping.literalToString);
  }

  get friend() {
    return this.singularNullable("https://example.org/friend", ObjectMapping.as(Person));
  }

  set friend(value: Person | null) {
    this.overwriteNullable("https://example.org/friend", value, ObjectMapping.as(Person));
  }
}
```

## 5. Dataset Wrapping
- Use `DatasetWrapper` to iterate over multiple instances of a class in a dataset.
- Example:
```typescript
import { DatasetWrapper } from "rdfjs-wrapper";

class People extends DatasetWrapper {
  [Symbol.iterator]() {
    return this.subjectsOf("https://example.org/name", Person);
  }
}
```

## 6. JSON-LD Serialization
- Implement a `toJSON()` method in each class to serialize the object to JSON-LD.
- Example:
```typescript
class Person extends TermWrapper {
  // ...existing code...

  toJSON() {
    return {
      "@id": this.term.value,
      "name": this.name,
      "friend": this.friend?.term.value,
    };
  }
}
```

## References
- [RDF/JS Wrapper Documentation](https://rdf.js.org/)
- [RDF Concepts](https://www.w3.org/TR/rdf12-concepts/)
