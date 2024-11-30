import dataclasses
import enum
import inspect
import re
import sys
import typing
from dataclasses import dataclass
from typing import Annotated, Any, Callable, Optional, TypeVar, Union

from pysqlsync.formation.inspection import dataclass_has_primary_key
from pysqlsync.model.properties import FieldProperties, get_field_properties
from sphinx.application import Sphinx
from sphinx.errors import SphinxError
from sphinx.ext.autodoc import Options
from strong_typing.inspection import (
    DataclassInstance,
    TypeLike,
    evaluate_type,
    get_class_properties,
    is_dataclass_type,
    is_type_annotated,
    is_type_optional,
    is_type_union,
    unwrap_annotated_type,
    unwrap_optional_type,
    unwrap_union_types,
)
from strong_typing.name import python_type_to_str


class TypeTransform:
    "Maps a type to another type."

    type_transform: dict[str, TypeLike]

    def __init__(
        self, type_transform: Optional[dict[TypeLike, TypeLike]] = None
    ) -> None:
        if type_transform is not None:
            self.type_transform = {
                python_type_to_str(key, use_union_operator=True): value
                for key, value in type_transform.items()
            }
        else:
            self.type_transform = {}

    def __call__(self, arg_type: TypeLike) -> TypeLike:
        if isinstance(arg_type, str):
            raise TypeError("expected: evaluated type; got: `str`")

        mapped_type = self.type_transform.get(
            python_type_to_str(arg_type, use_union_operator=True)
        )
        if mapped_type is not None:
            return mapped_type

        if is_type_annotated(arg_type):
            annotation_types = typing.get_args(arg_type)
            annotated_type = annotation_types[0]
            annotation_objects = annotation_types[1:]
            transformed_type = self(annotated_type)
            return Annotated[(transformed_type, *annotation_objects)]
        if is_type_optional(arg_type):
            optional_type: TypeLike = unwrap_optional_type(arg_type)
            return Optional[self(optional_type)]
        if is_type_union(arg_type):
            union_type = unwrap_annotated_type(arg_type)
            union_types = unwrap_union_types(union_type)
            return Union[tuple(self(member_type) for member_type in union_types)]

        return arg_type


@dataclass
class Symbols:
    primary_key: str = "🔑"
    unique_constraint: str = "◉"


class MissingFieldError(SphinxError):
    "Raised when a doc-string param has no matching field in a class."


T = TypeVar("T")


class DocstringProcessor:
    """
    Ensures a compact yet comprehensive documentation is generated for classes and enumerations.

    This class should be registered with a call to
    ```
    app.connect("autodoc-process-docstring", DocstringProcessor(...))
    ```
    """

    symbols: Symbols
    type_transform: TypeTransform

    def __init__(
        self,
        *,
        symbols: Optional[Symbols] = None,
        type_transform: Optional[dict[TypeLike, TypeLike]] = None,
    ) -> None:
        """
        Creates a new doc-string processor.

        :param type_transform: A mapping from source type to target type.
        """

        if symbols is not None:
            self.symbols = symbols
        else:
            self.symbols = Symbols()

        if type_transform is not None:
            self.type_transform = TypeTransform(type_transform)
        else:
            self.type_transform = TypeTransform()

    def _python_type_to_str(self, arg_type: TypeLike) -> str:
        """Emits a string representation of a Python type, with substitutions."""

        transformed_type = self.type_transform(arg_type)
        return python_type_to_str(transformed_type, use_union_operator=True)

    def _process_object(
        self,
        name: str,
        props: dict[str, T],
        lines: list[str],
        transform: Callable[[T, str], tuple[str, str]],
    ) -> None:
        """
        Lists all fields of a class including field name, type and description string.

        :param name: Name of a plain class, a data-class or an entity class, or a function, or a method.
        :param props: Properties associated with each field of a plain class, a data-class or an entity class.
        :param lines: Documentation text as a multi-line string.
        :param transform: A transformation that maps field properties and the original description to a type string
            and an updated text.
        :raises MissingFieldError: Raised when a tag references a non-existent field.
        """

        param_expr = re.compile(r"^:param\s+([^:]+):(.*)$")
        for index, line in enumerate(lines):
            match: Optional[re.Match] = param_expr.match(line)
            if not match:
                continue

            field_name: str = match.group(1)
            if field_name not in props:
                raise MissingFieldError(
                    f"param `{field_name}` is not declared as a field in the class `{name}`"
                )

            field_type, text = transform(props[field_name], match.group(2))
            lines[index] = f":param {field_type} {field_name}: {text}"

    def _transform_field(self, field_type: TypeLike, text: str) -> tuple[str, str]:
        """
        Returns type information and description for a field in a class.

        :param field_type: Field properties.
        :param text: Original field description.
        """

        return self._python_type_to_str(field_type), text

    def process_class(self, cls: type, lines: list[str]) -> None:
        """
        Lists all fields of a plain class including field name, type and description string.

        :param cls: A plain class.
        :param lines: Documentation text as a multi-line string.
        """

        module = sys.modules[cls.__module__]
        fields: dict[str, TypeLike] = {
            field_name: evaluate_type(field_type, module)
            for field_name, field_type in get_class_properties(cls)
        }
        self._process_object(cls.__name__, fields, lines, self._transform_field)

    def process_dataclass(self, cls: type[DataclassInstance], lines: list[str]) -> None:
        """
        Lists all fields of a data-class including field name, type and description string.

        :param cls: A regular data-class.
        :param lines: Documentation text as a multi-line string.
        """

        module = sys.modules[cls.__module__]
        fields: dict[str, TypeLike] = {
            field.name: evaluate_type(field.type, module)
            for field in dataclasses.fields(cls)
        }
        self._process_object(cls.__name__, fields, lines, self._transform_field)

    def _transform_column(self, prop: FieldProperties, text: str) -> tuple[str, str]:
        """
        Returns type information and extended description for a field (column) in an entity (table).

        :param prop: Field properties.
        :param text: Original field description.
        """

        source_type: TypeLike
        if prop.nullable:
            source_type = Optional[prop.field_type]
        else:
            source_type = prop.field_type

        # generate type definition text
        field_type = self._python_type_to_str(source_type)

        # emit an emoji for SQL primary key and unique constraint
        pieces: list[str] = []
        if prop.is_primary:
            pieces.append(self.symbols.primary_key)
        if prop.is_unique:
            pieces.append(self.symbols.unique_constraint)
        pieces.append(text)

        description = " ".join(pieces)

        return field_type, description

    def process_table(self, cls: type[DataclassInstance], lines: list[str]) -> None:
        """
        Lists all fields of an entity that translates to a SQL table.

        :param cls: A database or data warehouse entity type (i.e. a data-class with a primary key).
        :param lines: Documentation text as a multi-line string.
        """

        module = sys.modules[cls.__module__]
        fields: dict[str, FieldProperties] = {
            field.name: get_field_properties(evaluate_type(field.type, module))
            for field in dataclasses.fields(cls)
        }
        self._process_object(cls.__name__, fields, lines, self._transform_column)

    def process_function(self, func: Callable[..., Any], lines: list[str]) -> None:
        params = typing.get_type_hints(func, include_extras=True)
        self._process_object(func.__name__, params, lines, self._transform_field)

    def process_enum(
        self, cls: type[enum.Enum], options: Options, lines: list[str]
    ) -> None:
        """
        Lists all values for an enumeration type.

        :param options: Sphinx configuration options.
        :param lines: Documentation text as a multi-line string.
        """

        options["undoc-members"] = True
        return

    def process_codeblock(self, lines: list[str]) -> None:
        """
        Replaces Markdown-style code blocks with Sphinx-style code blocks.

        :param lines: Documentation text as a multi-line string.
        """

        target_lines: list[str] = []
        code_block = False
        for source_line in lines:
            if not code_block:
                match: Optional[re.Match] = re.match(r"^```(.*)$", source_line)
                if match:
                    language: str = match.group(1)

                    target_lines.append(f".. code-block:: {language}")
                    target_lines.append("")
                    code_block = True
                else:
                    target_lines.append(source_line)
            else:
                if source_line.startswith("```"):
                    code_block = False
                else:
                    target_lines.append(f"    {source_line}")

        lines[:] = target_lines

    def __call__(
        self,
        app: Sphinx,
        what: str,
        name: str,
        obj: object,
        options: Options,
        lines: list[str],
    ) -> None:
        """
        Ensures a compact yet comprehensive documentation is generated for classes and enumerations.

        The parameters are passed by `autodoc` in Sphinx.

        :param app: The Sphinx application object.
        :param what: The type of the object which the docstring belongs to (one of 'module', 'class', 'exception',
            'function', 'method', 'attribute').
        :param name: The fully qualified name of the object.
        :param obj: The object itself.
        :param options: The options given to the directive: an object with attributes `inherited_members`,
            `undoc_members`, `show_inheritance` and `no-index` that are true if the flag option of same name was given
            to the auto directive.
        :param lines: The lines of the docstring.
        """

        self.process_codeblock(lines)

        if what == "class":
            cls: type = typing.cast(type, obj)
            if issubclass(cls, enum.Enum):
                self.process_enum(cls, options, lines)
            elif is_dataclass_type(cls):
                if dataclass_has_primary_key(cls):
                    self.process_table(cls, lines)
                else:
                    self.process_dataclass(cls, lines)
            elif inspect.isclass(cls):
                self.process_class(cls, lines)
        elif what == "exception":
            exc = typing.cast(type[Exception], obj)
            self.process_class(exc, lines)
        elif what in ["function", "method"]:
            func = typing.cast(Callable[..., Any], obj)
            self.process_function(func, lines)


def process_docstring(
    app: Sphinx, what: str, name: str, obj: object, options: Options, lines: list[str]
) -> None:
    """
    Ensures a compact yet comprehensive documentation is generated for classes and enumerations.

    This function should be registered with a call to
    ```
    app.connect("autodoc-process-docstring", process_docstring)
    ```
    """

    processor = DocstringProcessor()
    processor(app, what, name, obj, options, lines)


def skip_member(
    app: Sphinx, what: str, name: str, obj: object, skip: bool, options: Options
) -> Optional[bool]:
    """
    Enables documenting "special methods" using the Sphinx extension `sphinx.ext.autodoc`.

    This function should be registered with a call to
    ```
    app.connect("autodoc-skip-member", skip_member)
    ```

    This function implements a callback for ``autodoc-skip-member`` events to
    include documented "special methods" (method names with two leading and two
    trailing underscores) in your documentation. The result is similar to the
    use of the ``special-members`` flag with one big difference: special
    methods are included but other types of members are ignored. This means
    that attributes like ``__weakref__`` will always be ignored.

    The parameters expected by this function are those defined for Sphinx event
    callback functions.
    """

    if inspect.isroutine(obj):
        if name.startswith("_") and not name.startswith("__"):
            # skip private methods
            return True

        if getattr(obj, "__doc__", None):
            # include special methods with documentation
            return False

    return None