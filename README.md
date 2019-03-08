# JsonSchemaGenerator
Generates JSON schema which fits perfectly in React JSON Schema Form Component (https://mozilla-services.github.io/react-jsonschema-form/)

## Features
- automatically creates inputs' title from the name
    - separates the words based on snake_case or camelCase
- fills the objects' required lists (if wanted)
- hides the inputs through the UI schema definition (if wanted)

## Installation
Clone the repository to your filesystem:
```
git clone https://github.com/OndraTom/JsonSchemaGenerator
```

## Execution
### Parameters
- **--input**  input JSON file path (required)
- **--required-items** makes all form items required (optional)
- **--invisible-items** makes all form items invisible (optional)
- **--cast_types** makes number types as string with a cast_type parameter

### Example
```
python3 json_schema_generator.py --input=./tests/test.json --required-items
```

## Tests
```
python3 -m unittest discover -s ./tests
```