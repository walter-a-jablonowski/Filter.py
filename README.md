# Filter

AI made py-version from [PHP](https://github.com/walter-a-jablonowski/Filter)

A powerful boolean filter that can check complex filters against full text or (nested) records. You can use it in web applications, data processing, or UIs to define filters by typing expressions rather than clicking through multiple controls.

**State:** Implemented with Python, providing similar functionality to the PHP version.

```
pip install -r requirements.txt
python server.py
```

Then open your browser to http://localhost:8000/

## Features

- Full text filtering with boolean operators
- Record filtering with field comparisons
- Support for nested fields in records
- Regular expressions support
- Synonym expansion using YAML configuration
- Simple web interface for testing filters

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Filter.py.git
cd Filter.py

# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py
```

## Usage

### In Python Code

```python
from Filter import Filter

# Initialize filter with optional synonyms file
filter_obj = Filter('synonyms.yml')

# Parse a filter expression
tree = filter_obj.parse('("important" and /urgent/i) or (good and excellent)')

# Check against text
text = "This is an important and urgent matter."
result = filter_obj.check(text, tree)  # Returns True or False

# Check against records
record = {
    "priority": "high",
    "status": "pending",
    "tags": ["urgent", "bug"]
}
filter_expr = '(priority = "high" and status != "completed") or (tags contains_any ["urgent", "important"])'
tree = filter_obj.parse(filter_expr)
result = filter_obj.check(record, tree)  # Returns True or False
```

### Web Interface

The package includes a simple web interface for testing filters:

1. Run the server: `python server.py`
2. Open your browser to http://localhost:8000/
3. Use the interface to test full text and record filters

## Filter Syntax

### Full Text

```
("my string" and /some_regex/i) or (string3 and string4) and string5
```

### Records

- Nested fields: `nested.field = ...`
- Equal: `=`, `!=` (also used for `null`)
- Greater/Less: `>`, `<`, `>=`, `<=` (also used for dates)
- Wildcard: `= "some*"` (case insensitive: `= i"some*"`)
- Regex: `= /some_regex/i`
- Length: `myString.length >= 3` (for strings and arrays)
- Arrays:
  - In: `in [...]`, `! in [...]`
  - Partial matches: `tags contains_any ["important", "urgent"]`
  - All exist: `required_fields contains_all ["name", "email", "phone"]`
- Advanced: `scores any > 90` (check if any array element matches condition)

## Synonyms

You can define synonyms in a YAML file:

```yaml
important:
  - crucial
  - critical
  - essential

urgent:
  - immediate
  - pressing
  - rush
```

Then initialize the Filter with this file:

```python
filter_obj = Filter('synonyms.yml')
```


LICENSE
----------------------------------------------------------

Copyright (C) Walter A. Jablonowski 2024, free under [MIT license](LICENSE)

[Privacy](https://walter-a-jablonowski.github.io/privacy.html) | [Legal](https://walter-a-jablonowski.github.io/imprint.html)
