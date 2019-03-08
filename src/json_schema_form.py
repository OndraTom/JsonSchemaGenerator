from typing import List
from abc import ABC, abstractmethod


class JsonSchemaFormInput(ABC):
    """
    Form input base
    """

    def __init__(self, name: str):
        self.name = name
        # Name to title conversion
        self.title = self._get_title_from_name(name)

    @abstractmethod
    def get_type(self) -> str:
        pass

    def get_name(self) -> str:
        return self.name

    def get_definition(self) -> dict:
        return {
            "title": self.title,
            "type": self.get_type()
        }

    def get_ui_hidden_definition(self) -> dict:
        return {
            "ui:widget": "hidden"
        }

    @staticmethod
    def _get_title_from_name(name: str) -> str:
        """
        Converts given name to title:
            name -> Name
            snake_name -> Snake Name
            camelName -> Camel Name
        """
        # remove special symbols
        name = name.replace("#", "")
        # snake case
        if "_" in name:
            return " ".join(name.split("_")).title()
        # camel case
        words = []
        word = ""
        previous_letter_is_lower = False
        for letter in name:
            if letter.isupper() and previous_letter_is_lower:
                words.append(word)
                word = letter
            else:
                word += letter
            previous_letter_is_lower = letter.islower()
        if len(word) > 0:
            words.append(word)
        return " ".join(words).title()


class StringInput(JsonSchemaFormInput):
    """
    String input
    """

    def __init__(self, name: str, cast_type: str = None):
        super().__init__(name=name)
        self.cast_type = cast_type

    def get_type(self) -> str:
        return "string"

    def get_definition(self) -> dict:
        definition = super().get_definition()
        if self.cast_type:
            definition["cast_type"] = self.cast_type
        return definition


class NumberInput(JsonSchemaFormInput):
    """
    Number input
    """

    def get_type(self) -> str:
        return "number"


class BooleanInput(JsonSchemaFormInput):
    """
    Boolean input
    """

    def get_type(self) -> str:
        return "boolean"


class ObjectInput(JsonSchemaFormInput):
    """
    Object input
    """

    def __init__(self, name: str, items_are_required: bool):
        super().__init__(name)
        self.items_are_required = items_are_required
        self.properties = []

    def get_type(self) -> str:
        return "object"

    def get_definition(self) -> dict:
        definition = super().get_definition()
        definition["properties"] = {}
        definition["required"] = []
        for form_input in self.properties:
            definition["properties"][form_input.get_name()] = form_input.get_definition()
            if self.items_are_required:
                definition["required"].append(form_input.get_name())
        return definition

    def get_ui_hidden_definition(self) -> dict:
        definition = {
            "ui:widget": "hidden"
        }
        for form_input in self.properties:
            definition[form_input.get_name()] = form_input.get_ui_hidden_definition()
        return definition

    def get_properties(self) -> List[JsonSchemaFormInput]:
        return self.properties

    def add_property(self, form_input: JsonSchemaFormInput):
        self.properties.append(form_input)

    def has_property(self, form_input: JsonSchemaFormInput) -> bool:
        for properties_item in self.properties:
            if properties_item.get_name() == form_input.get_name():
                return True
        return False

    def get_property_by_name(self, property_name: str) -> JsonSchemaFormInput:
        for properties_item in self.properties:
            if properties_item.get_name() == property_name:
                return properties_item
        raise ObjectInputPropertyNotFound(property_name)


class ArrayInput(JsonSchemaFormInput):
    """
    Array/List input
        - array items must be of the same type
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.items_input = None

    def get_type(self) -> str:
        return "array"

    def get_definition(self) -> dict:
        definition = super().get_definition()
        if not self.has_items_input():
            definition["items"] = {}
        else:
            definition["items"] = self.items_input.get_definition()
        return definition

    def get_ui_hidden_definition(self) -> dict:
        return {
            "ui:widget": "hidden",
            "items": {} if self.items_input is None else self.items_input.get_ui_hidden_definition()
        }

    def has_items_input(self) -> bool:
        return self.items_input is not None

    def set_items_input(self, items_input: JsonSchemaFormInput):
        self.items_input = items_input

    def get_items_input(self) -> JsonSchemaFormInput:
        return self.items_input

    def merge_items_input(self, items_input: JsonSchemaFormInput):
        """
        :raises IncompatibleArrayItemsInput if the item is in incompatible type
        """
        if not isinstance(items_input, type(self.items_input)):
            raise IncompatibleArrayItemsInput(self.get_name())
        # object properties merging
        if isinstance(items_input, ObjectInput):
            for object_property in items_input.get_properties():
                if not self.items_input.has_property(object_property):
                    self.items_input.add_property(object_property)


class JsonSchemaFormInputFactory:
    """
    Form inputs factory
    """

    def __init__(self, items_are_required: bool):
        self.items_are_required = items_are_required

    def create_input(self, input_name: str, input_value) -> JsonSchemaFormInput:
        """
        :raises UnknownInputType if the input type is unknown
        """
        if isinstance(input_value, bool):
            return BooleanInput(input_name)
        if isinstance(input_value, str):
            return StringInput(input_name)
        if isinstance(input_value, int):
            return StringInput(input_name, cast_type="integer")
        if isinstance(input_value, float):
            return StringInput(input_name, cast_type="float")
        if isinstance(input_value, dict):
            input_item = ObjectInput(input_name, self.items_are_required)
            for key, value in input_value.items():
                input_item.add_property(self.create_input(key, value))
            return input_item
        if isinstance(input_value, list):
            input_item = ArrayInput(input_name)
            for list_item in input_value:
                array_item_input = self.create_input(
                    input_item.get_name()[0:-1],
                    list_item
                )
                if not input_item.has_items_input():
                    input_item.set_items_input(array_item_input)
                else:
                    input_item.merge_items_input(array_item_input)
            return input_item
        raise UnknownInputType(input_name)


class JsonSchemaForm:
    """
    JSON schema form
    """

    def __init__(self, schema: dict, items_are_required: bool = True, items_are_invisible: bool = False):
        self.schema = schema
        self.items_are_required = items_are_required
        self.items_are_invisible = items_are_invisible
        self.inputs = []
        self.inputs_factory = JsonSchemaFormInputFactory(self.items_are_required)
        self.data_schema = None
        self.ui_schema = None
        self._load_inputs_from_schema()

    def _load_inputs_from_schema(self):
        for key, value in self.schema.items():
            self.inputs.append(
                self.inputs_factory.create_input(key, value)
            )

    def get_data_schema(self) -> dict:
        data_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        for form_input in self.inputs:
            data_schema["properties"][form_input.get_name()] = form_input.get_definition()
            if self.items_are_required:
                data_schema["required"].append(form_input.get_name())
        return data_schema

    def get_ui_schema(self) -> dict:
        if not self.items_are_invisible:
            return {}
        ui_schema = {}
        for form_input in self.inputs:
            ui_schema[form_input.get_name()] = form_input.get_ui_hidden_definition()
        return ui_schema


class JsonSchemaFormException(Exception):
    pass


class JsonSchemaFormInputFactoryException(JsonSchemaFormException):
    pass


class UnknownInputType(JsonSchemaFormInputFactoryException):

    def __init__(self, input_name: str):
        self.input_name = input_name

    def __str__(self) -> str:
        return "Input '" + self.input_name + "' has unknown type"


class IncompatibleArrayItemsInput(JsonSchemaFormInputFactoryException):

    def __init__(self, input_name: str):
        self.input_name = input_name

    def __str__(self) -> str:
        return "Input '" + self.input_name + "' has incompatible type with other array items"


class ObjectInputPropertyNotFound(JsonSchemaFormException):

    def __init__(self, property_name: str):
        self.property_name = property_name

    def __str__(self) -> str:
        return "Object property '" + self.property_name + "' hasn't been found"
