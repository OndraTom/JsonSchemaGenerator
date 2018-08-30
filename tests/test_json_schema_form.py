from unittest import TestCase
from src.json_schema_form import JsonSchemaForm, IncompatibleArrayItemsInput


class JsonSchemaFormTests(TestCase):

    def test_simple_form_without_required_items(self):
        form = JsonSchemaForm(
            {
                "string": "test",
                "number": 1,
                "boolean": True,
                "object": {
                    "string": "inner"
                },
                "array": ["foo", "bar"]
            },
            items_are_required=False
        )
        self.assertEqual(
            form.get_data_schema(),
            {
                "type": "object",
                "properties": {
                    "string": {
                        "title": "String",
                        "type": "string"
                    },
                    "number": {
                        "title": "Number",
                        "type": "number"
                    },
                    "boolean": {
                        "title": "Boolean",
                        "type": "boolean"
                    },
                    "object": {
                        "title": "Object",
                        "type": "object",
                        "properties": {
                            "string": {
                                "title": "String",
                                "type": "string"
                            }
                        },
                        "required": []
                    },
                    "array": {
                        "title": "Array",
                        "type": "array",
                        "items": {
                            "title": "Arra",
                            "type": "string"
                        }
                    }
                },
                "required": []
            }
        )

    def test_simple_form_with_required_items(self):
        form = JsonSchemaForm(
            {
                "string": "test",
                "number": 1,
                "boolean": True,
                "object": {
                    "string": "inner"
                },
                "array": ["foo", "bar"]
            },
            items_are_required=True
        )
        self.assertEqual(
            form.get_data_schema(),
            {
                "type": "object",
                "properties": {
                    "string": {
                        "title": "String",
                        "type": "string"
                    },
                    "number": {
                        "title": "Number",
                        "type": "number"
                    },
                    "boolean": {
                        "title": "Boolean",
                        "type": "boolean"
                    },
                    "object": {
                        "title": "Object",
                        "type": "object",
                        "properties": {
                            "string": {
                                "title": "String",
                                "type": "string"
                            }
                        },
                        "required": ["string"]
                    },
                    "array": {
                        "title": "Array",
                        "type": "array",
                        "items": {
                            "title": "Arra",
                            "type": "string"
                        }
                    }
                },
                "required": ["string", "number", "boolean", "object", "array"]
            }
        )

    def test_title_parsing(self):
        form = JsonSchemaForm(
            {
                "neutral": "test",
                "Capital": "test",
                "snake_text": "test",
                "camelText": "test",
                "BigCamelText": "test"
            },
            items_are_required=False
        )
        self.assertEqual(
            form.get_data_schema(),
            {
                "type": "object",
                "properties": {
                    "neutral": {
                        "title": "Neutral",
                        "type": "string"
                    },
                    "Capital": {
                        "title": "Capital",
                        "type": "string"
                    },
                    "snake_text": {
                        "title": "Snake Text",
                        "type": "string"
                    },
                    "camelText": {
                        "title": "Camel Text",
                        "type": "string"
                    },
                    "BigCamelText": {
                        "title": "Big Camel Text",
                        "type": "string"
                    }
                },
                "required": []
            }
        )

    def test_invisible_items_ui_definition(self):
        form = JsonSchemaForm(
            {
                "string": "test",
                "number": 1,
                "boolean": True,
                "object": {
                    "string": "inner"
                },
                "array": ["foo", "bar"]
            },
            items_are_required=False,
            items_are_invisible=True
        )
        self.assertEqual(
            form.get_ui_schema(),
            {
                "string": {
                    "ui:widget": "hidden"
                },
                "number": {
                    "ui:widget": "hidden"
                },
                "boolean": {
                    "ui:widget": "hidden"
                },
                "object": {
                    "ui:widget": "hidden",
                    "string": {
                        "ui:widget": "hidden"
                    }
                },
                "array": {
                    "ui:widget": "hidden",
                    "items": {
                        "ui:widget": "hidden"
                    }
                }
            }
        )

    def test_array_of_arrays_form(self):
        form = JsonSchemaForm(
            {
                "array": [["foo"], ["bar"]]
            },
            items_are_required=False
        )
        self.assertEqual(
            form.get_data_schema(),
            {
                "type": "object",
                "properties": {
                    "array": {
                        "title": "Array",
                        "type": "array",
                        "items": {
                            "title": "Arra",
                            "type": "array",
                            "items": {
                                "title": "Arr",
                                "type": "string"
                            }
                        }
                    }
                },
                "required": []
            }
        )

    def test_array_objects_merge(self):
        form = JsonSchemaForm(
            {
                "array": [
                    {
                        "foo": "val"
                    },
                    {
                        "bar": 1
                    }
                ]
            },
            items_are_required=False
        )
        self.assertEqual(
            form.get_data_schema(),
            {
                "type": "object",
                "properties": {
                    "array": {
                        "title": "Array",
                        "type": "array",
                        "items": {
                            "title": "Arra",
                            "type": "object",
                            "properties": {
                                "foo": {
                                    "title": "Foo",
                                    "type": "string"
                                },
                                "bar": {
                                    "title": "Bar",
                                    "type": "number"
                                }
                            },
                            "required": []
                        }
                    }
                },
                "required": []
            }
        )

    def test_incompatible_array_items(self):
        self.assertRaises(
            IncompatibleArrayItemsInput,
            JsonSchemaForm,
            {
                "array": ["foo", 1]
            }
        )