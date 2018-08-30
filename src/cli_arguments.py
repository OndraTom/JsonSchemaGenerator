from typing import List


class CliArguments:

    default_args_prefix = "--"

    def __init__(self, arguments: List[str], args_prefix: str = default_args_prefix,
                 mandatory_arguments: List[str] = None, optional_arguments: List[str] = None):
        self.args_prefix = args_prefix
        self.arguments = self._parse_arguments(arguments)
        self.mandatory_arguments = mandatory_arguments
        self.optional_arguments = optional_arguments
        self._validate_arguments()

    def is_argument_set(self, argument_name: str) -> bool:
        return argument_name in self.arguments

    def get_argument_value(self, argument_name: str) -> str:
        if argument_name not in self.arguments:
            raise ArgumentNotFound(argument_name)
        if self.arguments[argument_name] is None:
            raise ArgumentValueNotDefined(argument_name)
        return self.arguments[argument_name]

    def _parse_arguments(self, arguments: List[str]) -> dict:
        arguments_dict = {}
        for argument in arguments:
            argument_value = None
            # check and remove the prefix
            if not argument.startswith(self.args_prefix):
                raise InvalidArgumentFormat(argument)
            argument = argument[len(self.args_prefix):]
            # extract the value
            if "=" in argument:
                split = argument.split("=")
                argument = split[0]
                argument_value = "=".join(split[1:])
            # save to the dictionary
            arguments_dict[argument] = argument_value
        return arguments_dict

    def _validate_arguments(self):
        possible_arguments = []
        if self.mandatory_arguments is not None:
            possible_arguments += self.mandatory_arguments
            for mandatory_argument in self.mandatory_arguments:
                if not self.is_argument_set(mandatory_argument):
                    raise MandatoryArgumentIsMissing(mandatory_argument)
        if self.optional_arguments is not None:
            possible_arguments += self.optional_arguments
        # we will check arguments presence validity only if mandatory and/or optional arguments are defined
        if len(possible_arguments) > 0:
            for defined_argument in self.arguments.keys():
                if defined_argument not in possible_arguments:
                    raise ArgumentNotAllowed(defined_argument)


class CliArgumentsException(Exception):
    pass


class InvalidArgumentFormat(CliArgumentsException):

    def __init__(self, argument: str):
        super().__init__("Argument '" + argument + "' has invalid format")


class ArgumentNotFound(CliArgumentsException):

    def __init__(self, argument: str):
        super().__init__("Argument '" + argument + "' not found")


class ArgumentValueNotDefined(CliArgumentsException):

    def __init__(self, argument: str):
        super().__init__("Argument '" + argument + "' value hasn't been defined")


class MandatoryArgumentIsMissing(CliArgumentsException):

    def __init__(self, argument: str):
        super().__init__("Mandatory argument '" + argument + "' hasn't been defined")


class ArgumentNotAllowed(CliArgumentsException):

    def __init__(self, argument: str):
        super().__init__("Argument '" + argument + "' is not allowed")
